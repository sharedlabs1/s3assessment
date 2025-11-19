#!/usr/bin/env python3
"""Validator: cicd_medium_bluegreen

Checks for cicd/blue_green_workflow.yml and cicd/switch_traffic.sh containing TODO_CHECKLIST sentinel.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
REPORT = os.path.join(ROOT, "test_report.log")

def check(path):
    if not os.path.exists(path):
        return False, f"Missing file: {path}"
    with open(path, "r", encoding="utf-8") as f:
        c = f.read()
    if "TODO_CHECKLIST" not in c:
        return False, "TODO_CHECKLIST sentinel not found"
    return True, "OK"

def main():
    files = [
        ("blue_green_workflow.yml", os.path.join(ROOT, "cicd", "blue_green_workflow.yml")),
        ("switch_traffic.sh", os.path.join(ROOT, "cicd", "switch_traffic.sh")),
    ]
    checks = []
    for name, path in files:
        ok, msg = check(path)
        checks.append((name, ok, msg))

    passed = sum(1 for c in checks if c[1])
    total = len(checks)
    with open(REPORT, "a", encoding="utf-8") as r:
        r.write("\n=== cicd_medium_bluegreen ===\n")
        for n, ok, m in checks:
            r.write(f"{n}: {'PASS' if ok else 'FAIL'} - {m}\n")
        r.write(f"PASSED {passed}/{total} checks\n")

    print(f"PASSED {passed}/{total} checks")
    sys.exit(0 if passed == total else 1)

if __name__ == '__main__':
    main()
