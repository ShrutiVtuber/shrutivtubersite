#!/usr/bin/env bash
# Install the shrutivtuber.com Cloudflare DNS token into /etc/caddy/caddy.env
# and reload Caddy — safely.
#
# caddy.env is a live secrets file for sites that are currently serving
# traffic. A bad write here takes theourgia's TLS down with it, so this script
# backs up first, validates before reloading, and rolls back on failure.
#
# Usage, ON THE SERVER:
#   read -rs -p 'token: ' TOKEN && export TOKEN     # never echoed, not in history
#   bash scripts/install-caddy-token.sh
#
set -euo pipefail

ENVFILE=/etc/caddy/caddy.env
VAR=CLOUDFLARE_API_TOKEN_SHRUTI
STAMP=$(date +%Y%m%d-%H%M%S)

[[ -n "${TOKEN:-}" ]] || { echo "error: TOKEN is not set. See usage at the top of this script." >&2; exit 1; }
[[ ${#TOKEN} -ge 30 ]] || { echo "error: TOKEN looks too short (${#TOKEN} chars) — is it a placeholder?" >&2; exit 1; }

echo "==> verifying the token against Cloudflare before touching anything"
verify=$(curl -sS --max-time 20 -H "Authorization: Bearer ${TOKEN}" \
  https://api.cloudflare.com/client/v4/user/tokens/verify)
python3 - "$verify" <<'PY'
import json, sys
d = json.loads(sys.argv[1])
if not d.get("success"):
    print("  token REJECTED by Cloudflare:", [e.get("message") for e in d.get("errors", [])])
    raise SystemExit(1)
print("  token valid, status:", (d.get("result") or {}).get("status"))
PY

echo "==> checking it can actually see the shrutivtuber.com zone"
zones=$(curl -sS --max-time 20 -H "Authorization: Bearer ${TOKEN}" \
  "https://api.cloudflare.com/client/v4/zones?name=shrutivtuber.com")
python3 - "$zones" <<'PY'
import json, sys
d = json.loads(sys.argv[1])
res = d.get("result") or []
if not d.get("success") or not res:
    print("  WARNING: token cannot list shrutivtuber.com.")
    print("  If you scoped it to a single zone this can still be fine —")
    print("  zone-scoped DNS tokens sometimes cannot enumerate zones.")
    print("  Caddy's DNS-01 challenge is the real test.")
else:
    print("  zone visible:", res[0]["name"], "status:", res[0].get("status"))
PY

if sudo grep -q "^${VAR}=" "$ENVFILE" 2>/dev/null; then
    echo "==> ${VAR} already present — updating it"
    sudo cp -a "$ENVFILE" "${ENVFILE}.bak-${STAMP}"
    sudo sed -i "s|^${VAR}=.*|${VAR}=${TOKEN}|" "$ENVFILE"
else
    echo "==> appending ${VAR}"
    sudo cp -a "$ENVFILE" "${ENVFILE}.bak-${STAMP}"
    printf '%s=%s\n' "$VAR" "$TOKEN" | sudo tee -a "$ENVFILE" >/dev/null
fi
echo "    backup: ${ENVFILE}.bak-${STAMP}"

echo "==> validating the full Caddy config"
if ! sudo /usr/local/bin/caddy validate --config /etc/caddy/Caddyfile; then
    echo "!! validation FAILED — rolling back and leaving Caddy untouched" >&2
    sudo cp -a "${ENVFILE}.bak-${STAMP}" "$ENVFILE"
    exit 1
fi

echo "==> reloading Caddy"
sudo /usr/local/bin/caddy-reload

echo "==> done. Watch certificate issuance with:"
echo "    journalctl -u caddy -f | grep -i shrutivtuber"
