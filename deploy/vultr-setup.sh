#!/usr/bin/env bash
# One-shot setup on a fresh Vultr Compute instance (Ubuntu 22.04/24.04).
#   curl -fsSL https://raw.githubusercontent.com/Ak759-wq/Can_I_Bring_It_-/main/deploy/vultr-setup.sh | bash -s -- YOUR_GEMINI_KEY
set -euo pipefail
KEY="${1:?usage: vultr-setup.sh GEMINI_API_KEY}"
apt-get update -y && apt-get install -y git docker.io docker-compose-v2 ufw
systemctl enable --now docker
cd /opt
[ -d Can_I_Bring_It_- ] || git clone https://github.com/Ak759-wq/Can_I_Bring_It_-.git
cd Can_I_Bring_It_- && git pull
cat > backend/.env <<ENV
GEMINI_API_KEY=$KEY
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_EMBED_MODEL=gemini-embedding-001
RATE_PER_MIN=20
CORS_ORIGINS=*
ENV
ufw allow 22 && ufw allow 80 && ufw --force enable || true
docker compose up -d --build
sleep 5
curl -s localhost/api/health && echo
echo "Live at: http://$(curl -s ifconfig.me)/"
