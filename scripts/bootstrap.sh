#!/usr/bin/env bash
# Re-runnable server setup for aca-ai-server (Ubuntu Server LTS, GTX 1660 Ti).
# Usage: sudo ./scripts/bootstrap.sh [step ...]   (no args = all steps)
set -euo pipefail
[[ $EUID -eq 0 ]] || { echo "run with sudo"; exit 1; }
USER_NAME="${SUDO_USER:-acameth}"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
log(){ echo -e "\n==> $*"; }

base(){ log "base packages"
  apt-get update
  apt-get install -y ca-certificates curl git jq unzip htop nvtop lm-sensors imagemagick \
    python3-venv pipx avahi-daemon wpasupplicant rfkill unattended-upgrades
  sensors-detect --auto >/dev/null || true; }

firewall(){ log "ufw"
  ufw default deny incoming; ufw default allow outgoing
  ufw allow OpenSSH; ufw allow 5353/udp comment 'mDNS'
  ufw --force enable; }

ssh_harden(){ log "sshd: keys only"
  cat > /etc/ssh/sshd_config.d/00-hardening.conf <<'X'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
X
  sshd -t && systemctl restart ssh; }

updates(){ log "unattended-upgrades"
  cat > /etc/apt/apt.conf.d/20auto-upgrades <<'X'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
X
  cat > /etc/apt/apt.conf.d/52local-unattended <<'X'
Unattended-Upgrade::Automatic-Reboot "true";
Unattended-Upgrade::Automatic-Reboot-Time "04:00";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
Unattended-Upgrade::Package-Blacklist { "nvidia-"; "libnvidia-"; "cuda-"; };
X
}

power(){ log "lid ignore + no sleep"
  mkdir -p /etc/systemd/logind.conf.d
  cat > /etc/systemd/logind.conf.d/10-lid.conf <<'X'
[Login]
HandleLidSwitch=ignore
HandleLidSwitchExternalPower=ignore
HandleLidSwitchDocked=ignore
X
  systemctl restart systemd-logind
  systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target; }

nvidia(){ log "NVIDIA server driver"
  if ! command -v nvidia-smi >/dev/null; then
    ubuntu-drivers install --gpgpu
    v=$(dpkg -l | grep -oP 'nvidia-headless-no-dkms-\K[0-9]+(?=-server)' | head -1)
    apt-get install -y "nvidia-utils-${v}-server"
    echo "!! reboot required, then re-run: sudo $0 nvidia docker"
  fi
  mkdir -p /etc/systemd/system/nvidia-persistenced.service.d
  cat > /etc/systemd/system/nvidia-persistenced.service.d/override.conf <<'X'
[Service]
ExecStart=
ExecStart=/usr/bin/nvidia-persistenced --user nvidia-persistenced --persistence-mode --verbose

[Install]
WantedBy=multi-user.target
X
  systemctl daemon-reload; systemctl enable nvidia-persistenced || true; }

docker_setup(){ log "Docker + NVIDIA container toolkit"
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  cat > /etc/apt/sources.list.d/docker.sources <<X
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "$VERSION_CODENAME")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
X
  curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey \
    | gpg --dearmor --yes -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
  curl -fsSL https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list \
    | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' \
    > /etc/apt/sources.list.d/nvidia-container-toolkit.list
  apt-get update
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin nvidia-container-toolkit
  usermod -aG docker "$USER_NAME"
  cat > /etc/docker/daemon.json <<'X'
{
  "runtimes": { "nvidia": { "args": [], "path": "nvidia-container-runtime" } },
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" }
}
X
  systemctl restart docker; }

dirs(){ log "storage layout"
  mkdir -p /srv/models /data/{pg,images,backups,logs,models-archive,evals}
  chown -R "$USER_NAME:$USER_NAME" /srv/models /data; }

python_env(){ log "repo venv + aca CLI"
  sudo -u "$USER_NAME" bash -c "cd '$REPO_DIR' && python3 -m venv .venv && .venv/bin/pip install -q -e services/common"; }

models(){ log "download models"
  sudo -u "$USER_NAME" bash -lc "pipx install -q 'huggingface_hub[cli]' || true
    hf download unsloth/Qwen3.5-4B-GGUF --include '*Q4_K_M*.gguf' --include 'mmproj-F16.gguf' --local-dir /srv/models/qwen3.5-4b"; }

verify(){ log "verify"
  ufw status | head -5; nvidia-smi --query-gpu=name,memory.total,persistence_mode --format=csv || true
  docker run --rm --gpus all nvidia/cuda:13.0.0-base-ubuntu24.04 nvidia-smi -L || true
  df -h / /data; }

ALL=(base firewall ssh_harden updates power nvidia docker_setup dirs python_env models verify)
steps=("${@:-${ALL[@]}}")
for s in "${steps[@]}"; do [[ $s == docker ]] && s=docker_setup; "$s"; done
log "done"