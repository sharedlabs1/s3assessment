# AWS Redshift Assessment - Data Warehousing (Medium)

github-repo: https://github.com/sharedlabs1/s3assessment

## Difficulty Level: 🟡 Medium

## Scenario
You are a data engineer at DataCorp. Design a production Redshift cluster with optimized performance, automated backups, and data loading pipelines.

## Prerequisites
- Access to the shared AWS training account
- Python 3.8+ installed
- GitHub CLI (`gh`) installed
- Understanding of Redshift distribution styles and sort keys

## Setup

1. **Download the assessment files** (you only need these 3 files):
   - `validate_tasks.py`
   - `requirements.txt`
   - `README_redshift_medium.md`

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

That's it! You're ready to start the assessment.

## Tasks to Complete

### Task 1: Create Production Redshift Cluster
Create a Redshift cluster with:
- **Cluster Identifier**: `dwh-cluster-${your-student-id}`
- **Node Type**: ra3.xlplus
- **Number of Nodes**: 4
- **Database Name**: datawarehouse
- **Master Username**: dwhadmin
- **Master Password**: (Set secure password)

**Requirements:**
- Enable automated snapshots (retention: 14 days)
- Set snapshot schedule: Daily at 02:00 UTC
- Enable encryption with KMS (use default key or custom)
- Enable enhanced VPC routing
- Set maintenance window: Sun:03:00-Sun:04:00 UTC
- Add tags: `Environment=Production`, `Project=DataWarehouse`, `CostCenter=Analytics`, `StudentID=${your-student-id}`

### Task 2: Configure Parameter Group
Create custom parameter group:
- **Parameter Group Name**: `dwh-params-${your-student-id}`
- **Family**: redshift-1.0
- Configure parameters:
  - `enable_user_activity_logging`: true
  - `require_ssl`: true
  - `max_concurrency_scaling_clusters`: 2
  - `wlm_json_configuration`: Configure 3 query queues with memory allocation

### Task 3: Design Database Schema with Optimization
Create optimized tables:

**Fact Table: sales_fact**
```sql
CREATE TABLE sales_data.sales_fact (
    sale_id BIGINT PRIMARY KEY,
    customer_id INTEGER,
    product_id INTEGER,
    store_id INTEGER,
    sale_date DATE,
    quantity INTEGER,
    amount DECIMAL(12,2)
)
DISTKEY(customer_id)
SORTKEY(sale_date);
```

**Dimension Tables:**
- `customers` (100K rows) - DISTSTYLE ALL
- `products` (10K rows) - DISTSTYLE ALL
- `stores` (1K rows) - DISTSTYLE ALL

### Task 4: Configure S3 Data Loading
Set up S3 integration:
- **S3 Bucket**: `redshift-data-${your-student-id}`
- Create folders:
  - `/landing/` - raw data files
  - `/processed/` - cleaned data
  - `/logs/` - cluster logs
- Create IAM role for Redshift to access S3
- **Role Name**: `RedshiftS3Access-${your-student-id}`
- Attach role to cluster

Create COPY command to load data from S3:
```sql
COPY sales_data.sales_fact 
FROM 's3://redshift-data-${your-student-id}/landing/sales/'
IAM_ROLE 'arn:aws:iam::ACCOUNT:role/RedshiftS3Access-${your-student-id}'
CSV
DATEFORMAT 'YYYY-MM-DD';
```

### Task 5: Configure Workload Management (WLM)
Create WLM configuration with:
- **Queue 1**: ETL workloads (40% memory, concurrency: 3)
- **Queue 2**: Reporting (40% memory, concurrency: 5)
- **Queue 3**: Ad-hoc queries (20% memory, concurrency: 5)
- Enable short query acceleration
- Enable concurrency scaling for queues 2 and 3

### Task 6: Configure Monitoring and Maintenance
Set up comprehensive monitoring:
- Enable CloudWatch metrics
- Enable audit logging to S3 bucket
- Create CloudWatch alarms for:
  - CPU Utilization > 80%
  - Disk usage > 85%
  - Health status
  - Query throughput
- Configure automated VACUUM and ANALYZE schedule

### Task 7: Configure Security
Implement security best practices:
- Create security group restricting access to specific CIDR
- Enable VPC with private subnets
- Create DB subnet group: `dwh-subnet-${your-student-id}`
- Enable database audit logging
- Configure user groups with different privileges:
  - `analysts` - Read-only
  - `engineers` - Read/Write
  - `admins` - Full access

## Validation

Once you've completed all tasks, run the validation script:

```bash
python validate_tasks.py redshift-medium
```

The script will verify:
- Cluster configuration with ra3 nodes
- Custom parameter group
- Database schema with distribution and sort keys
- S3 IAM role attachment
- WLM configuration
- Monitoring setup
- Security groups and network configuration

## Cleanup (After Assessment)
1. Delete automated and manual snapshots
2. Pause or delete cluster (create final snapshot if needed)
3. Delete custom parameter group
4. Detach and delete IAM role
5. Empty and delete S3 buckets
6. Delete subnet group
7. Delete security groups
8. Delete CloudWatch alarms

## Tips
- ra3 nodes use managed storage and scale compute/storage independently
- DISTKEY on high-cardinality columns for even distribution
- SORTKEY on frequently filtered columns
- Test WLM queues with sample queries
- Monitor query performance with system tables
- Use COPY command for bulk loading (much faster than INSERT)
- Enable concurrency scaling for unpredictable workloads
