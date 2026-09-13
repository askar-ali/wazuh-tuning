#!/usr/bin/env python3
"""Compare alert volume per rule between two Wazuh alerts.json files (before/after tuning).

Usage: alert-report.py BEFORE.json AFTER.json [--top 15] [--min-level 0]
Prints per-rule counts, the change, and the overall reduction; lists rules that
appear only after (new noise) separately. Input is one JSON object per line.
"""
import argparse
import json
import sys
from collections import Counter


def count(path, min_level):
    c, desc = Counter(), {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rule = json.loads(line)["rule"]
            except (json.JSONDecodeError, KeyError):
                continue
            if int(rule.get("level", 0)) < min_level:
                continue
            c[rule["id"]] += 1
            desc[rule["id"]] = rule.get("description", "")
    return c, desc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("before")
    ap.add_argument("after")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--min-level", type=int, default=0)
    a = ap.parse_args()

    b, bd = count(a.before, a.min_level)
    f, fd = count(a.after, a.min_level)
    desc = {**bd, **fd}
    tb, tf = sum(b.values()), sum(f.values())

    print(f"{'rule':<8}{'before':>8}{'after':>8}{'change':>9}  description")
    for rid, n in b.most_common(a.top):
        after = f.get(rid, 0)
        pct = (after - n) / n * 100
        print(f"{rid:<8}{n:>8}{after:>8}{pct:>8.0f}%  {desc[rid][:50]}")

    new = [r for r in f if r not in b]
    if new:
        print("\nRules that only appear AFTER tuning (check these):")
        for rid in sorted(new, key=lambda r: -f[r]):
            print(f"  {rid}: {f[rid]} alerts  {desc[rid][:60]}")

    red = (tb - tf) / tb * 100 if tb else 0.0
    print(f"\nTotal alerts: {tb} -> {tf} ({red:+.1f}% reduction)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
