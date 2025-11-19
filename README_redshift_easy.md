# AWS Redshift Assessment - Data Warehousing (Easy)

github-repo: https://github.com/sharedlabs1/s3assessment

## Difficulty Level: 🟢 Easy

## Scenario
You are a data analyst at StartupCo. Set up a basic Redshift cluster for data analytics and reporting.

## Prerequisites
- Access to the shared AWS training account
- Python 3.8+ installed
- GitHub CLI (`gh`) installed

## Setup

1. **Download the assessment files** (you only need these 3 files):
   - `validate_tasks.py`
   - `requirements.txt`
   - `README_redshift_easy.md`

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

That's it! You're ready to start the assessment.

## Tasks to Complete

### Task 1: Create Redshift Cluster
Create a Redshift cluster with:
- **Cluster Identifier**: `analytics-cluster-${your-student-id}`
- **Node Type**: dc2.large
- **Number of Nodes**: 2 (single-node for testing, 2-node for real workload)
- **Database Name**: analytics
- **Master Username**: admin
- **Master Password**: (Set your own secure password)

**Requirements:**
- Enable automated snapshots (retention: 7 days)
- Enable encryption at rest (use default AWS key)
- Add tags: `Environment=Development`, `Project=Analytics`, `StudentID=${your-student-id}`

### Task 2: Configure Security
Create and attach security group:
- **Security Group Name**: `analytics-redshift-sg-${your-student-id}`
- Allow Redshift (port 5439) from your IP address
- Add description: "Redshift cluster access for analytics"

### Task 3: Create Database Schema and Load Sample Data
Connect to your cluster and:
- Create schema: `sales_data`
- Create table: `orders` with columns:
  - order_id (INTEGER, PRIMARY KEY)
  - customer_id (INTEGER)
  - order_date (DATE)
  - amount (DECIMAL(10,2))
- Load at least 10 sample rows

### Task 4: Configure Basic Monitoring
- Enable CloudWatch metrics
- Enable audit logging to S3 bucket (or CloudWatch)
- **Log S3 Bucket** (if using S3): `redshift-logs-${your-student-id}`

## Validation

Once you've completed all tasks, run the validation script:

```bash
python validate_tasks.py redshift-easy
```

The script will verify:
- Cluster configuration
- Security group setup
- Database schema and tables
- Audit logging configuration

## Cleanup (After Assessment)
To avoid charges:
1. Delete manual snapshots
2. Delete cluster (skip final snapshot for dev)
3. Delete security group
4. Delete S3 logging bucket (if created)

## Tips
- Cluster creation takes 5-10 minutes
- Use SQL client like DBeaver or psql to connect
- Keep master password accessible for testing
- dc2.large nodes are cost-effective for learning
