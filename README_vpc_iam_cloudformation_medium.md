IAM / CloudFormation — Medium

Goal
-----
Create a CloudFormation template that provisions an IAM Role and Policy suitable for an EC2 instance to read from a specific S3 bucket. This assesses IAM policy design and CloudFormation parameterization.

What you must deliver
---------------------
- A CloudFormation template at `cloudformation/iam_role_template.yaml` that:
  - Accepts a parameter for the S3 bucket name
  - Creates an IAM Policy granting read-only access to the specified S3 prefix
  - Creates an IAM Role and Instance Profile suitable for EC2, and attaches the policy

- A policy file `cloudformation/iam_policy.json` (starter) with a TODO_CHECKLIST section to guide least-privilege design.

Starter files
-------------
- `cloudformation/iam_role_template.yaml` (starter)
- `cloudformation/iam_policy.json` (starter)

Deliverables and verification
-----------------------------
- The validator checks that both starter files exist and contain the sentinel `TODO_CHECKLIST` so graders can confirm you used the template guidance.
- In CI, validators may check IAM names/outputs; ensure your template includes an Output for the Role ARN.

Run tests
---------
```bash
python validate_tasks.py vpc_iam_cloudformation_medium
```

Hints
-----
- Keep policies narrowly scoped to the provided S3 bucket/prefix (use Condition with aws:ResourceArn or Resource ARNs when possible).
- Use Parameters for bucket name and put a short description in the template for each parameter.
