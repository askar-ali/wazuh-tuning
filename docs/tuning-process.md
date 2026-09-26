# Tuning process

1. `scripts/top-noisy-rules.sh` over a week of alerts -> list top rules.
2. Measure the effect later with `scripts/alert-report.py before.json after.json`.
   Note: lowering a rule's level moves alerts to a quieter level, it does not remove them;
   use `<ignore>` or a level-0 rule to suppress.
3. For each: is it actionable? If no, scope it down (FIM ignore / lower level in `local_rules.xml`).
4. Active-response misfires: confirm the blocked source, add it to `white_list`, narrow `rules_id`.
5. Validate: `scripts/check-xml.py`, then on the manager `wazuh-logtest` and `wazuh-analysisd -t`.
6. Roll out to a canary agent group, compare alert volume, then to all.

Note: rule IDs/levels here are examples; verify against your Wazuh version's ruleset.
`wazuh-logtest` was not run here (no Wazuh install); XML well-formedness was checked locally.
