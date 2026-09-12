#!/usr/bin/env bash
# Wazuh active-response wrapper: refuse to block anything on the protected list.
#
# Wazuh passes one JSON document on stdin (extra_args, parameters.alert.data.srcip, ...).
# Protected CIDRs/addresses (CI/CD workers, monitoring, bastion) come from
# $PROTECTED_FILE, one per line. If the source is protected we log and exit 0
# (no block); otherwise we delegate to the stock firewall-drop script.
#
# Test mode: SAFE_BLOCK_DRY_RUN=1 prints the decision and does not call firewall-drop.
set -euo pipefail

PROTECTED_FILE="${PROTECTED_FILE:-/var/ossec/etc/protected-sources.list}"
FIREWALL_DROP="${FIREWALL_DROP:-/var/ossec/active-response/bin/firewall-drop}"
LOG="${AR_LOG:-/var/ossec/logs/active-responses.log}"

payload="$(cat)"
srcip="$(jq -r '.parameters.alert.data.srcip // empty' <<<"$payload")"

log() { printf '%s safe-block: %s\n' "$(date '+%Y/%m/%d %H:%M:%S')" "$*" >>"$LOG" 2>/dev/null || true; echo "$*"; }

if [[ -z "$srcip" ]]; then
  log "no srcip in alert, nothing to block"
  exit 0
fi

is_protected() {
  python3 -I - "$1" "$PROTECTED_FILE" <<'PY'
import ipaddress, sys
ip = ipaddress.ip_address(sys.argv[1])
try:
    lines = open(sys.argv[2], encoding="utf-8").read().splitlines()
except FileNotFoundError:
    sys.exit(1)
for line in lines:
    line = line.split("#")[0].strip()
    if line and ip in ipaddress.ip_network(line, strict=False):
        sys.exit(0)
sys.exit(1)
PY
}

if is_protected "$srcip"; then
  log "SKIPPED block of protected source $srcip"
  exit 0
fi

if [[ "${SAFE_BLOCK_DRY_RUN:-0}" == "1" ]]; then
  log "WOULD block $srcip"
  exit 0
fi

log "blocking $srcip"
exec "$FIREWALL_DROP" <<<"$payload"
