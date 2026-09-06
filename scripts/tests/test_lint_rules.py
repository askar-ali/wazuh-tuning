import importlib.util
import os
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    "lint_rules", os.path.join(os.path.dirname(__file__), "..", "lint-rules.py"))
lint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lint)


def write(text):
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False)
    f.write(text)
    f.close()
    return f.name


GOOD = '<group name="x"><rule id="100100" level="3"><if_sid>550</if_sid><description>d</description></rule></group>'


class RuleLint(unittest.TestCase):
    def test_good(self):
        self.assertEqual(lint.lint_rules(write(GOOD)), [])

    def test_duplicate_id(self):
        r = '<group>' + '<rule id="100100" level="3"><description>d</description></rule>' * 2 + '</group>'
        self.assertTrue(any("duplicate" in e for e in lint.lint_rules(write(r))))

    def test_out_of_range_id(self):
        r = '<group><rule id="500" level="3"><description>d</description></rule></group>'
        self.assertTrue(any("custom range" in e for e in lint.lint_rules(write(r))))

    def test_bad_level_and_missing_description(self):
        r = '<group><rule id="100101" level="99"></rule></group>'
        errs = lint.lint_rules(write(r))
        self.assertTrue(any("level" in e for e in errs))
        self.assertTrue(any("description" in e for e in errs))

    def test_undefined_custom_parent(self):
        r = '<group><rule id="100102" level="3"><if_sid>100999</if_sid><description>d</description></rule></group>'
        self.assertTrue(any("undefined custom rule" in e for e in lint.lint_rules(write(r))))

    def test_malformed_xml(self):
        self.assertTrue(lint.lint_rules(write("<group><rule>")))


class AuditdLint(unittest.TestCase):
    def test_exclusion_first_is_ok(self):
        t = "-a never,exit -F exe=/x\n-a always,exit -S execve\n"
        self.assertEqual(lint.lint_auditd(write(t)), [])

    def test_late_exclusion_is_flagged(self):
        t = "-a always,exit -S execve\n-a never,exit -F exe=/x\n"
        self.assertEqual(len(lint.lint_auditd(write(t))), 1)


class RepoFiles(unittest.TestCase):
    """The committed rules must lint clean."""
    root = os.path.join(os.path.dirname(__file__), "..", "..")

    def test_committed_rules(self):
        self.assertEqual(lint.lint_rules(os.path.join(self.root, "rules/local_rules.xml")), [])
        self.assertEqual(lint.lint_auditd(os.path.join(self.root, "rules/auditd.rules")), [])


if __name__ == "__main__":
    unittest.main()
