# AWS RDS Assessment - Database Management (Medium)

github-repo: https://github.com/sharedlabs1/s3assessment

## Difficulty Level: 🟡 Medium

## Scenario
You are a database administrator at TechStart Inc. Your task is to set up a production-ready RDS PostgreSQL database with high availability and automated backups.

## Prerequisites
- Access to the shared AWS training account
- Python 3.8+ installed
- GitHub CLI (`gh`) installed

## Setup

1. **Download the assessment files** (you only need these 3 files):
   - `validate_tasks.py`
   - `requirements.txt`
   - `README_rds_medium.md`

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

That's it! You're ready to start the assessment.

## Tasks to Complete

### Task 1: Create RDS PostgreSQL Database with Multi-AZ
Create an RDS PostgreSQL database instance with:
- **DB Instance Identifier**: `webapp-db-${your-student-id}`
- **Engine**: PostgreSQL 15 (or latest)
- **Instance Class**: db.t3.small
- **Storage**: 100 GB General Purpose (SSD) with autoscaling enabled (max: 200 GB)
- **Master Username**: postgres
- **Master Password**: (Set your own secure password)

**Requirements:**
- Enable Multi-AZ deployment for high availability
- Enable automated backups (retention period: 14 days)
- Set backup window: 03:00-04:00 UTC
- Set maintenance window: Sun:04:00-Sun:05:00 UTC
- Enable deletion protection
- Add tags: `Environment=Production`, `Project=WebApp`, `StudentID=${your-student-id}`, `Backup=Required`

### Task 2: Configure Parameter Group
Create a custom DB parameter group:
- **Parameter Group Name**: `webapp-postgres-params-${your-student-id}`
- **Family**: postgres15 (match your engine version)
- Modify parameters:
  - `max_connections`: 200
  - `shared_buffers`: 256MB
  - `log_statement`: all (for audit purposes)

Associate this parameter group with your database instance.

### Task 3: Configure Security and Networking
Create and configure security groups:
- **Security Group Name**: `webapp-db-sg-${your-student-id}`
- Allow PostgreSQL (port 5432) from:
  - Your application security group (or specific IP range)
  - A bastion host security group (for admin access)
- Add description for each rule

### Task 4: Create Read Replica
- Create a read replica of your primary database
- **Read Replica Identifier**: `webapp-db-${your-student-id}-replica`
- Use db.t3.small instance class
- Place in a different availability zone from primary
- Add tags: `Role=ReadReplica`, `StudentID=${your-student-id}`

### Task 5: Configure Monitoring and Alerts
- Enable Enhanced Monitoring with 30-second granularity
- Enable Performance Insights with 7 days retention
- Export logs to CloudWatch:
  - PostgreSQL logs
  - Upgrade logs

## Validation

Once you've completed all tasks, run the validation script:

```bash
python validate_tasks.py rds-medium
```

You will be prompted to enter your Student ID. The script will verify:
- Primary database configuration with Multi-AZ
- Custom parameter group settings
- Security group rules
- Read replica setup
- Monitoring and Performance Insights configuration

**Note:** This assessment tests production-ready database setup skills.

## Cleanup (After Assessment)
To avoid charges (in order):
1. Delete read replica first
2. Disable deletion protection on primary database
3. Delete primary database (create final snapshot if desired)
4. Delete custom parameter group
5. Delete security groups
6. Delete manual snapshots if created

## Tips
- Multi-AZ deployment takes 10-15 minutes to create
- Parameter changes may require database restart
- Read replica creation takes 5-10 minutes
- Keep track of all resource names for cleanup
- Test connectivity before validation
