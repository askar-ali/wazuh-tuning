#!/usr/bin/env bash
# Run on a Wazuh MANAGER with these decoders/rules installed. Feeds each line of a
# cases file to wazuh-logtest and checks the matched rule id.
# Usage: logtest.sh [tests/logtest/webapp-cases.tsv]
set -euo pipefail

CASES="${1:-$(dirname "$0")/../tests/logtest/webapp-cases.tsv}"
LOGTEST="${LOGTEST:-/var/ossec/bin/wazuh-logtest}"
[[ -x "$LOGTEST" ]] || { echo "wazuh-logtest not found at $LOGTEST (run on the manager)" >&2; exit 2; }

fail=0
while IFS=$'\t' read -r line expected; do
  [[ -z "$line" || "$line" == \#* ]] && continue
  got="$(printf '%s\n' "$line" | "$LOGTEST" -q 2>&1 | awk '/id: /{gsub(/\x27/,"",$2); print $2}' | tail -1)"
  if [[ "$got" == "$expected" ]]; then echo "ok   $expected  $line"; else echo "FAIL expected $expected got '$got'  $line"; fail=1; fi
done <"$CASES"
exit "$fail"
