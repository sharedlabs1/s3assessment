VPC + IAM + CloudFormation — Hard

Goal
-----
Design and author a production-oriented CloudFormation template that sets up networking, NAT, and IAM for an application fleet. This tests multi-AZ VPC design, NAT usage, parameterization, and role scoping.

What you must deliver
---------------------
- A CloudFormation template at `cloudformation/infra_template.yaml` that creates (at minimum):
  - A VPC with at least two Availability Zones (create two subnets per AZ: public + private)
  - An Internet Gateway
  - A NAT Gateway in a public subnet and routing so private subnets have outbound internet access
  - Route Tables and subnet associations for public and private subnets
  - A Security Group (app-tier) that allows HTTP from the public-tier and SSH from a defined CIDR
  - An IAM Role for an Auto Scaling Group (or EC2 fleet) that has a narrowly scoped policy. Use Parameters for any ARNs you cannot create.
  - At least one Parameter and one Mapping in the template (to assess parameterization & conditional logic)

- The template must include Outputs for VpcId, PublicSubnetIds (comma-separated or list), and one IAM Role ARN.

Starter file
------------
`cloudformation/infra_template.yaml` contains a TODO_CHECKLIST with a checklist of required subsections. Complete those sections and add short comments describing your design choices.

Assessment notes
----------------
- The validator will check the presence of the template and the sentinel `TODO_CHECKLIST` in the file. In CI graders may choose to deploy or inspect template structure; make sure the template is valid YAML/JSON and uses proper CloudFormation types.
- Keep the template idempotent and avoid creating high-cost resources (e.g., large instance types). Use small instance sizes and prefer minimal ASG sizes.

Run tests
---------
```bash
python validate_tasks.py vpc_iam_cloudformation_hard
```

Hints and constraints
---------------------
- Use Parameters for AZ choice, instance type, and any bucket names so graders can override them.
- Include short comments in the template explaining why you chose particular CIDRs and NAT placement.
