# local-ai-server
Paths: models -> /srv/models (NVMe), data -> /data/{pg,images,backups,logs} (HDD)
Convention: every service uses restart: unless-stopped; only Caddy publishes LAN ports.
