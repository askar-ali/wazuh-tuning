#!/usr/bin/env bash
# Behavioural test for active-response/safe-block.sh (no Wazuh needed).
set -euo pipefail
cd "$(dirname "$0")/.."

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
cp config/protected-sources.list.example "$TMP/protected"
export PROTECTED_FILE="$TMP/protected" AR_LOG="$TMP/ar.log" SAFE_BLOCK_DRY_RUN=1

run() { jq -nc --arg ip "$1" '{parameters:{alert:{data:{srcip:$ip}}}}' | active-response/safe-block.sh; }
fail() { echo "FAIL: $*" >&2; exit 1; }

[[ "$(run 192.0.2.5)"     == *SKIPPED* ]]   || fail "CI worker in CIDR should be protected"
[[ "$(run 198.51.100.10)" == *SKIPPED* ]]   || fail "single protected address should be skipped"
[[ "$(run 203.0.113.9)"   == *"WOULD block"* ]] || fail "unlisted address should be blocked"
[[ "$(echo '{}' | active-response/safe-block.sh)" == *"no srcip"* ]] || fail "missing srcip should be a no-op"

PROTECTED_FILE="$TMP/missing" bash -c 'jq -nc "{parameters:{alert:{data:{srcip:\"203.0.113.9\"}}}}" | active-response/safe-block.sh' | grep -q "WOULD block" \
  || fail "missing protected file should not protect anything"
echo "safe-block tests OK"
