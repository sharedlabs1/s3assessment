# AWS RDS Assessment - Database Management (Easy)

github-repo: https://github.com/sharedlabs1/s3assessment

## Difficulty Level: 🟢 Easy

## Scenario
You are a junior database administrator at DataCorp. Your task is to set up a basic RDS MySQL database for development purposes.

## Prerequisites
- Access to the shared AWS training account
- Python 3.8+ installed
- GitHub CLI (`gh`) installed

## Setup

1. **Download the assessment files** (you only need these 3 files):
   - `validate_tasks.py`
   - `requirements.txt`
   - `README_rds_easy.md`

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

That's it! You're ready to start the assessment.

## Tasks to Complete

### Task 1: Create RDS MySQL Database Instance
Create an RDS MySQL database instance with the following specifications:
- **DB Instance Identifier**: `myapp-db-${your-student-id}`
- **Engine**: MySQL 8.0 (or latest)
- **Instance Class**: db.t3.micro
- **Storage**: 20 GB General Purpose (SSD)
- **Master Username**: admin
- **Master Password**: (Set your own secure password - you'll need to remember it)

**Requirements:**
- Enable automated backups (retention period: 7 days)
- Disable Multi-AZ deployment (this is for cost savings in dev environment)
- Add tags: `Environment=Development`, `Project=MyApp`, `StudentID=${your-student-id}`

### Task 2: Configure Security Group
Create and attach a security group for database access:
- **Security Group Name**: `myapp-db-sg-${your-student-id}`
- Allow MySQL/Aurora (port 3306) from your IP address only
- Add description: "MySQL database access for development"

### Task 3: Enable Enhanced Monitoring
- Enable Enhanced Monitoring with 60-second granularity
- Use the default monitoring role (or create one if needed)

## Validation

Once you've completed all tasks, run the validation script:

```bash
python validate_tasks.py rds-easy
```

You will be prompted to enter your Student ID. The script will then:
- Trigger automated tests via GitHub Actions in the central repository
- The workflow uses shared AWS credentials (configured by your instructor)
- Tests will verify YOUR specific RDS instance (myapp-db-{your-student-id})
- Wait for the tests to complete (2-3 minutes)
- Download and display your test results
- Save the results to `test_report.log` in your local directory

**Note:** You don't need to configure AWS credentials or create GitHub secrets. Just provide your student ID when prompted.

## Cleanup (After Assessment)
To avoid charges:
- Delete your RDS instance (note: you can skip final snapshot for dev environments)
- Delete your security group
- Verify no snapshots remain

## Tips
- Use the AWS Management Console for easier setup
- Keep your master password secure but accessible for testing
- The db.t3.micro instance is Free Tier eligible (if available in your account)
- Make sure to tag all resources with your student ID for easy identification
