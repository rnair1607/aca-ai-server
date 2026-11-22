# local-ai-server

Paths: models -> /srv/models (NVMe), data -> /data/{pg,images,backups,logs} (HDD)
Convention: every service uses restart: unless-stopped; only Caddy publishes LAN ports.

## Repo layout

aca-ai-server/
├── compose.yaml
├── .env.example
├── scripts/bootstrap.sh ← server setup
└── services/common/ ← shared Python package
├── pyproject.toml
├── README.md
└── aca_ai/{**init**,config,images,llm,food,cli}.py

## scripts/bootstrap.sh

It's safe to run more than once. Run it with sudo ./scripts/bootstrap.sh for every step, or name steps, e.g. sudo ./scripts/bootstrap.sh docker dirs.
