# wazuh-tuning

Reducing Wazuh SIEM alert noise without losing signal: file-integrity (FIM)
scoping, custom local rules, auditd rules and safe active-response.

> Generic lab recreation of tuning I do on production SIEMs (since 10/2025).
> Contains sample config snippets only: no real hostnames, agents or data.

## Principles

1. Measure first: find the top noisy rule IDs before changing anything.
2. Tune narrowly: lower level or ignore only for a specific path/process, never a whole rule family.
3. Active response must never block infrastructure (CI/CD workers, monitoring, bastions): use a whitelist.
4. Every change is a reviewed commit with a reason.

## Layout

```
config/ossec-agent-fim.conf    FIM scoping (what to watch, what to ignore)
config/active-response.conf    safe active-response with a whitelist
rules/local_rules.xml          noise-reduction and escalation rules
rules/auditd.rules             auditd rules for the audit trail
scripts/top-noisy-rules.sh     find noisy rules from alerts.json
scripts/check-xml.py           well-formedness check for the XML files
docs/tuning-process.md
```
