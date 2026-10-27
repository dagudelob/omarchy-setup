#!/usr/bin/env bash
set -euo pipefail

# Helper script invoked via pkexec to write /etc/iptsd.d/90-omarchy-pen.conf
# and reload/restart the iptsd daemon cleanly.

SRC_FILE="${1:-}"
if [[ -z "$SRC_FILE" || ! -f "$SRC_FILE" ]]; then
  echo "Usage: apply-iptsd.sh <source-conf-file>" >&2
  exit 1
fi

mkdir -p /etc/iptsd.d
install -m 0644 "$SRC_FILE" /etc/iptsd.d/90-omarchy-pen.conf

udevadm control --reload
systemctl restart "iptsd@*.service" 2>/dev/null || udevadm trigger -s hidraw
exit 0
