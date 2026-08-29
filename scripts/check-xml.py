#!/usr/bin/env python3
"""Check that config/rule XML fragments are well-formed (wrapped in a root)."""
import sys
import xml.etree.ElementTree as ET

bad = 0
for path in sys.argv[1:]:
    text = open(path, encoding="utf-8").read()
    try:
        ET.fromstring(f"<root>{text}</root>")
        print(f"ok   {path}")
    except ET.ParseError as e:
        bad += 1
        print(f"FAIL {path}: {e}")
sys.exit(1 if bad else 0)
