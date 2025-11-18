# AWS EC2 Assessment - Instance Management

github-repo: https://github.com/sharedlabs1/s3assessment

## Scenario
You are a cloud engineer at TechCorp. Your task is to set up and manage EC2 instances with proper configuration.

## Prerequisites
- Access to the shared AWS training account
- Python 3.8+ installed
- GitHub CLI (`gh`) installed

## Setup

1. **Download the assessment files** (you only need these 3 files):
   - `validate_tasks.py`
   - `requirements.txt`
   - `README_ec2.md`

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

That's it! You're ready to start the assessment.

## Tasks to Complete

### Task 1: Launch EC2 Instance
Launch an EC2 instance with the following specifications:
- **Instance Name**: `webserver-${your-student-id}`
- **Instance Type**: t2.micro
- **AMI**: Amazon Linux 2023
- **Key Pair**: Create or use existing key pair

**Requirements:**
- Enable detailed monitoring
- Add proper tags: `Environment=Development`, `Project=WebServer`, `StudentID=${your-student-id}`

### Task 2: Configure Security Group
Create and attach a security group:
- **Security Group Name**: `web-sg-${your-student-id}`
- Allow SSH (port 22) from your IP
- Allow HTTP (port 80) from anywhere (0.0.0.0/0)
- Allow HTTPS (port 443) from anywhere (0.0.0.0/0)

### Task 3: Elastic IP
- Allocate and associate an Elastic IP to your instance
- Tag the Elastic IP: `Name=webserver-eip-${your-student-id}`

## Validation

Once you've completed all tasks, run the validation script:

```bash
python validate_tasks.py ec2
```

You will be prompted to enter your Student ID. The script will then:
- Trigger automated tests via GitHub Actions in the central repository
- The workflow uses shared AWS credentials (configured by your instructor)
- Tests will verify YOUR specific EC2 resources (webserver-{your-student-id}, etc.)
- Wait for the tests to complete (2-3 minutes)
- Download and display your test results
- Save the results to `test_report.log` in your local directory

**Note:** You don't need to configure AWS credentials or create GitHub secrets. Just provide your student ID when prompted, and the system will automatically test your EC2 resources in the shared training account.

## Cleanup (After Assessment)
To avoid charges:
- Terminate your EC2 instance
- Delete your security group
- Release your Elastic IP
