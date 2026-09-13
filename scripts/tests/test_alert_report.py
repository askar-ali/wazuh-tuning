import os
import subprocess
import sys
import unittest

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
SCRIPT = os.path.join(ROOT, "scripts", "alert-report.py")
DATA = os.path.join(ROOT, "tests", "data")


def report(*extra):
    return subprocess.run(
        [sys.executable, "-I", SCRIPT, os.path.join(DATA, "alerts-before.json"),
         os.path.join(DATA, "alerts-after.json"), *extra],
        capture_output=True, text=True, check=True).stdout


class AlertReport(unittest.TestCase):
    def test_per_rule_reduction(self):
        out = report()
        line = next(l for l in out.splitlines() if l.startswith("550"))
        self.assertIn("-88%", line)

    def test_totals(self):
        self.assertIn("Total alerts: 53 -> 48", report())

    def test_new_rules_after_tuning_are_listed(self):
        out = report()
        self.assertIn("only appear AFTER", out)
        self.assertIn("100100", out)

    def test_min_level_filters_low_severity(self):
        # level >= 7 keeps rules 550 and 5712 only
        self.assertIn("Total alerts: 43 -> 8", report("--min-level", "7"))


if __name__ == "__main__":
    unittest.main()
