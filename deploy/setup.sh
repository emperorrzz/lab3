#!/usr/bin/env bash
# Ubuntu 22.04: sudo bash deploy/setup.sh <runner-user>
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ $EUID -ne 0 ]]; then
  echo "Usage: sudo bash deploy/setup.sh <runner-user>" >&2
  exit 1
fi
runner_user="${1:?Specify the Linux account running GitHub Actions Runner}"
id "$runner_user" >/dev/null
runner_group="$(id -gn "$runner_user")"
if ! id mortgage >/dev/null 2>&1; then
  useradd --system --no-create-home --shell /usr/sbin/nologin mortgage
fi
install -d -o "$runner_user" -g "$runner_group" -m 755 /opt/mortgage
install -m 644 app.py calculator.py /opt/mortgage/
chown "$runner_user:$runner_group" /opt/mortgage/app.py /opt/mortgage/calculator.py
install -m 644 deploy/mortgage.service /etc/systemd/system/mortgage.service
sudoers_file="$(mktemp)"
trap 'rm -f "$sudoers_file"' EXIT
printf '%s ALL=(root) NOPASSWD: /usr/bin/systemctl restart mortgage.service\n' "$runner_user" > "$sudoers_file"
visudo -cf "$sudoers_file"
install -o root -g root -m 440 "$sudoers_file" /etc/sudoers.d/mortgage
systemctl daemon-reload
systemctl enable --now mortgage.service
systemctl restart mortgage.service
echo "Ready: http://<VM-IP>:8000. Allow TCP 8000 in UFW if enabled."
