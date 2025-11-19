# AWS RDS Assessment - Database Management (Hard)

github-repo: https://github.com/sharedlabs1/s3assessment

## Difficulty Level: 🔴 Hard

## Scenario
You are a senior database architect at FinTech Solutions. Design and implement a highly available, secure, and compliant RDS Aurora cluster for a financial application with strict requirements.

## Prerequisites
- Access to the shared AWS training account
- Python 3.8+ installed
- GitHub CLI (`gh`) installed
- Understanding of database encryption, IAM authentication, and AWS Secrets Manager

## Setup

1. **Download the assessment files** (you only need these 3 files):
   - `validate_tasks.py`
   - `requirements.txt`
   - `README_rds_hard.md`

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

That's it! You're ready to start the assessment.

## Tasks to Complete

### Task 1: Create Aurora PostgreSQL Cluster with Global Database
Create an Aurora PostgreSQL cluster:
- **Cluster Identifier**: `finapp-cluster-${your-student-id}`
- **Engine**: Aurora PostgreSQL (Serverless v2 or Provisioned)
- **Instance Class**: db.r6g.large (if provisioned) or Serverless v2 with 0.5-2 ACU
- **Number of Instances**: 1 writer + 2 readers across different AZs
- **Storage**: Encrypted with AWS KMS (create or use existing CMK)

**Requirements:**
- Enable encryption at rest using KMS
- Enable IAM database authentication
- Enable deletion protection
- Enable automated backups (retention: 30 days)
- Enable backtrack with 24-hour window (if supported)
- Set backup window: 02:00-03:00 UTC
- Set maintenance window: Sat:03:00-Sat:04:00 UTC
- Add tags: `Environment=Production`, `Compliance=PCI-DSS`, `Project=FinApp`, `StudentID=${your-student-id}`, `CostCenter=Engineering`

### Task 2: Configure Custom Parameter and Option Groups
Create custom cluster parameter group:
- **Parameter Group Name**: `finapp-aurora-params-${your-student-id}`
- Configure:
  - `rds.force_ssl`: 1 (force SSL connections)
  - `log_statement`: ddl (log DDL statements for audit)
  - `log_connections`: 1
  - `log_disconnections`: 1
  - `shared_preload_libraries`: pg_stat_statements (for query analysis)

Create custom DB parameter group for instances:
- **Parameter Group Name**: `finapp-aurora-instance-params-${your-student-id}`
- Configure instance-specific parameters

### Task 3: Configure Advanced Security
Implement comprehensive security:

**Security Groups:**
- **Primary SG**: `finapp-db-sg-${your-student-id}`
  - PostgreSQL (5432) from application tier SG only
  - No public access
  
**IAM Authentication:**
- Create IAM role for database access
- Configure IAM policy for RDS connect
- Enable IAM authentication on cluster

**Secrets Manager:**
- Store master password in AWS Secrets Manager
- **Secret Name**: `finapp/db/master-${your-student-id}`
- Enable automatic rotation (30 days)

**Network:**
- Place cluster in private subnets only
- Create DB subnet group spanning 3 AZs
- **Subnet Group Name**: `finapp-db-subnet-${your-student-id}`

### Task 4: Configure Monitoring, Logging, and Alerting

**CloudWatch Logs:**
- Enable and export all log types:
  - PostgreSQL logs
  - Audit logs
  - Slow query logs
  - Error logs

**Enhanced Monitoring:**
- Enable with 15-second granularity
- Create custom IAM role for enhanced monitoring

**Performance Insights:**
- Enable with 7 days retention (free tier)
- Or 731 days (long-term retention)

**CloudWatch Alarms:**
Create alarms for:
- CPU Utilization > 80%
- Database Connections > 80% of max
- Replica Lag > 1000ms
- Failed Login Attempts > 5
- Storage usage > 85%

### Task 5: Implement Backup and Disaster Recovery

**Automated Backups:**
- 30-day retention
- Cross-region backup replication to secondary region

**Manual Snapshots:**
- Create manual snapshot: `finapp-cluster-${your-student-id}-baseline`
- Share snapshot with DR account (if available)
- Encrypt snapshot

**Point-in-Time Recovery:**
- Verify PITR is enabled
- Document recovery point objective (RPO): < 5 minutes

### Task 6: Create Aurora Global Database (Optional - Advanced)
If your account supports it:
- Create global database cluster
- Add secondary region cluster
- **Global Cluster ID**: `finapp-global-${your-student-id}`
- Configure replication lag monitoring

## Validation

Once you've completed all tasks, run the validation script:

```bash
python validate_tasks.py rds-hard
```

You will be prompted to enter your Student ID. The script will verify:
- Aurora cluster configuration with Multi-AZ
- Encryption settings (KMS)
- IAM authentication enabled
- Custom parameter groups
- Security group configuration
- Secrets Manager integration
- DB subnet group configuration
- Enhanced monitoring and Performance Insights
- CloudWatch logs export
- Backup configuration and snapshots
- Network isolation (private subnets)

**Note:** This is a comprehensive assessment testing enterprise-grade database architecture skills.

## Cleanup (After Assessment)
**⚠️ Important: Follow this order to avoid errors**

1. Delete CloudWatch alarms
2. Disable deletion protection on cluster
3. Delete reader instances
4. Delete writer instance
5. Delete cluster
6. Delete manual snapshots
7. Delete automated backup replications
8. Delete custom parameter groups
9. Delete DB subnet group
10. Delete secrets from Secrets Manager
11. Delete security groups
12. Delete IAM roles and policies created
13. Delete KMS key (schedule deletion)

## Evaluation Criteria

This hard assessment tests:
- ✅ Aurora cluster architecture (25 points)
- ✅ Security implementation (25 points)
- ✅ Monitoring and alerting (15 points)
- ✅ Backup and DR strategy (20 points)
- ✅ Network design (10 points)
- ✅ Best practices and compliance (5 points)

**Total: 100 points**
**Passing Score: 80 points**

## Tips
- Aurora cluster creation takes 15-20 minutes
- Test IAM authentication before validation
- Verify SSL connections are enforced
- Document your KMS key ID for cleanup
- Keep Secrets Manager ARN handy
- Understand the difference between cluster and instance parameters
- Review AWS Well-Architected Framework for databases
