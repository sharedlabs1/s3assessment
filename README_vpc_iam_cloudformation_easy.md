VPC / CloudFormation — Easy

Goal
-----
Build a minimal Amazon VPC using AWS CloudFormation. This exercise tests basic VPC networking knowledge and ability to author a small CloudFormation template.

What you must deliver
---------------------
- A CloudFormation template at `cloudformation/vpc_template.yaml` that creates:
  - A VPC with a sensible CIDR (e.g., 10.0.0.0/16)
  - One public subnet
  - An Internet Gateway attached to the VPC
  - A Route Table with a route to the Internet Gateway and an association with the public subnet
  - A Security Group that allows SSH (22) and HTTP (80) from anywhere (or a limited CIDR of your choosing)

- Outputs: VpcId, PublicSubnetId, SecurityGroupId

Starter file
------------
We've provided a starter CloudFormation template at `cloudformation/vpc_template.yaml`. It contains a short TODO_CHECKLIST to guide your work — replace/complete the sections marked there.

How you'll be assessed
----------------------
- The test harness verifies the presence of `cloudformation/vpc_template.yaml` and looks for the sentinel `TODO_CHECKLIST` in it. In CI the validator may also attempt to deploy (not by default) — so ensure your template is syntactically valid CloudFormation.

Run tests
---------
Use the repository helper to run the assessment validator:

```bash
python validate_tasks.py vpc_iam_cloudformation_easy
```

Notes and constraints
---------------------
- Keep the template focused: only create the resources requested above.
- Include short resource descriptions and Outputs.
- Clean up any test stacks you create in your AWS account after verification.
