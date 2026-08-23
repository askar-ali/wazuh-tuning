#!/usr/bin/env bash
# Top N rule IDs by alert count from a Wazuh alerts.json (one JSON object per line).
# Usage: top-noisy-rules.sh [alerts.json] [N]
set -euo pipefail

FILE="${1:-/var/ossec/logs/alerts/alerts.json}"
N="${2:-15}"
command -v jq >/dev/null || { echo "jq required" >&2; exit 1; }

jq -r '"\(.rule.id)\t\(.rule.level)\t\(.rule.description)"' "$FILE" \
  | sort | uniq -c | sort -rn | head -n "$N"
