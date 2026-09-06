#!/usr/bin/env python3
"""Lint Wazuh local rules and an auditd rules file.

Usage: lint-rules.py [--rules rules/local_rules.xml] [--auditd rules/auditd.rules]

Checks (local_rules.xml):
  - rule ids are unique and inside the custom range 100000-120000
  - level is 0-15, and every rule has a description
  - if_sid / if_matched_sid targets are either custom rules defined here
    (and defined earlier or later) or look like built-in ids (numeric)
Checks (auditd):
  - every 'never,exit' exclusion appears before the first 'always,exit' rule
    (auditd uses first match wins, so a late exclusion never applies)
"""
import argparse
import re
import sys
import xml.etree.ElementTree as ET

CUSTOM_MIN, CUSTOM_MAX = 100000, 120000


def lint_rules(path):
    errors = []
    try:
        root = ET.fromstring(f"<root>{open(path, encoding='utf-8').read()}</root>")
    except ET.ParseError as e:
        return [f"{path}: not well-formed XML: {e}"]

    seen = {}
    for rule in root.iter("rule"):
        rid = rule.get("id")
        if rid is None or not rid.isdigit():
            errors.append(f"{path}: rule without numeric id: {ET.tostring(rule)[:60]!r}")
            continue
        n = int(rid)
        if not CUSTOM_MIN <= n <= CUSTOM_MAX:
            errors.append(f"rule {rid}: id outside custom range {CUSTOM_MIN}-{CUSTOM_MAX}")
        if rid in seen:
            errors.append(f"rule {rid}: duplicate id")
        seen[rid] = rule
        level = rule.get("level")
        if level is None or not level.isdigit() or not 0 <= int(level) <= 15:
            errors.append(f"rule {rid}: level must be 0-15 (got {level!r})")
        desc = rule.findtext("description")
        if not desc or not desc.strip():
            errors.append(f"rule {rid}: missing description")

    for rid, rule in seen.items():
        for tag in ("if_sid", "if_matched_sid"):
            for el in rule.findall(tag):
                for ref in re.split(r"[,\s]+", (el.text or "").strip()):
                    if not ref:
                        continue
                    if not ref.isdigit():
                        errors.append(f"rule {rid}: {tag} has non-numeric id {ref!r}")
                    elif int(ref) >= CUSTOM_MIN and ref not in seen:
                        errors.append(f"rule {rid}: {tag} references undefined custom rule {ref}")
    return errors


def lint_auditd(path):
    errors = []
    first_always = None
    for no, line in enumerate(open(path, encoding="utf-8"), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "always,exit" in line and first_always is None:
            first_always = no
        if "never,exit" in line and first_always is not None:
            errors.append(f"{path}:{no}: exclusion comes after an 'always,exit' rule (line {first_always}); it will never match")
    return errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rules", default="rules/local_rules.xml")
    ap.add_argument("--auditd", default="rules/auditd.rules")
    a = ap.parse_args()
    errors = lint_rules(a.rules) + lint_auditd(a.auditd)
    for e in errors:
        print("ERROR", e)
    print("lint OK" if not errors else f"{len(errors)} problem(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
