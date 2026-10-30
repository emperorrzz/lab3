#!/usr/bin/env bash
set -euo pipefail
cd "${GITHUB_WORKSPACE:?Run this script in GitHub Actions}"
test -d /opt/mortgage
install -m 644 app.py calculator.py /opt/mortgage/
printf '%s\n' "${GITHUB_SHA:?}" > /opt/mortgage/VERSION
sudo -n /usr/bin/systemctl restart mortgage.service
for attempt in {1..10}; do
  if curl --fail --silent --max-time 2 http://127.0.0.1:8000/health | grep -qx ok; then
    echo "Deployed ${GITHUB_SHA}"
    exit 0
  fi
  sleep 1
done
echo "Health check failed. Check: sudo journalctl -u mortgage.service -n 50" >&2
exit 1
