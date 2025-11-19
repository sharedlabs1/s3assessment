#!/usr/bin/env python3
"""Validator: vpc_iam_cloudformation_medium

Checks for cloudformation/iam_role_template.yaml and cloudformation/iam_policy.json containing TODO_CHECKLIST sentinel.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
REPORT = os.path.join(ROOT, "test_report.log")

def check_file(path):
    if not os.path.exists(path):
        return False, f"Missing file: {path}"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if "TODO_CHECKLIST" not in content:
        return False, "Sentinel TODO_CHECKLIST not found in file"
    return True, "OK"

def main():
    checks = []
    role_path = os.path.join(ROOT, "cloudformation", "iam_role_template.yaml")
    policy_path = os.path.join(ROOT, "cloudformation", "iam_policy.json")

    checks.append(("iam_role_template.yaml exists and annotated",) + check_file(role_path))
    checks.append(("iam_policy.json exists and annotated",) + check_file(policy_path))

    passed = sum(1 for c in checks if c[1])
    total = len(checks)

    with open(REPORT, "a", encoding="utf-8") as r:
        r.write("\n=== vpc_iam_cloudformation_medium ===\n")
        for name, ok, msg in checks:
            r.write(f"{name}: {'PASS' if ok else 'FAIL'} - {msg}\n")
        r.write(f"PASSED {passed}/{total} checks\n")

    print(f"PASSED {passed}/{total} checks")
    sys.exit(0 if passed == total else 1)

if __name__ == '__main__':
    main()
