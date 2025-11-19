# AWS Redshift Assessment - Enterprise Data Warehouse (Hard)

github-repo: https://github.com/sharedlabs1/s3assessment

## Difficulty Level: 🔴 Hard

## Scenario
You are the lead data architect at GlobalCorp. Build an enterprise-grade, multi-region Redshift environment with disaster recovery, advanced security, data sharing, federated queries, and integration with Redshift Spectrum for data lake analytics.

## Prerequisites
- Access to the shared AWS training account
- Python 3.8+ installed
- GitHub CLI (`gh`) installed
- Advanced knowledge of Redshift architecture, query optimization, and AWS networking
- Experience with AWS KMS, IAM, Redshift Spectrum, and federated queries

## Setup

1. **Download the assessment files** (you only need these 3 files):
   - `validate_tasks.py`
   - `requirements.txt`
   - `README_redshift_hard.md`

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

That's it! You're ready to start the assessment.

## Tasks to Complete

### Task 1: Create Multi-Cluster Architecture
Create production cluster with disaster recovery:

**Primary Cluster:**
- **Cluster Identifier**: `dwh-primary-${your-student-id}`
- **Node Type**: ra3.4xlarge
- **Number of Nodes**: 6
- **Database Name**: enterprise_dwh
- **Encryption**: Customer-managed KMS key
- **KMS Key Alias**: `alias/redshift-${your-student-id}`
- **Enhanced VPC Routing**: Enabled
- **Maintenance Window**: Sun:03:00-Sun:05:00 UTC
- **Snapshot Retention**: 35 days
- **Automated Snapshot Schedule**: Every 6 hours

**Secondary Cluster (DR):**
- **Cluster Identifier**: `dwh-dr-${your-student-id}`
- Configure cross-region snapshot copy to secondary region
- Same configuration as primary
- Enable automated restore from snapshots

**Tags for all resources:**
- `Environment=Production`
- `Tier=Critical`
- `Compliance=SOC2`
- `StudentID=${your-student-id}`
- `DataClassification=Confidential`

### Task 2: Advanced Parameter Group Configuration
Create custom parameter group:
- **Parameter Group Name**: `enterprise-params-${your-student-id}`
- **Family**: redshift-1.0

**Configure parameters:**
```
enable_user_activity_logging: true
require_ssl: true
max_concurrency_scaling_clusters: 5
enable_case_sensitive_identifier: true
statement_timeout: 1800000
auto_analyze: true
use_fips_ssl: true
search_path: sales_data, analytics, staging, public
datestyle: ISO, MDY
```

**Custom WLM JSON Configuration:**
- 5 query queues with automatic WLM
- Enable short query acceleration (15 seconds)
- Queue priorities: 1=Critical, 2=High, 3=Medium, 4=Low, 5=Ad-hoc
- Configure queue assignment rules based on query groups and users

### Task 3: Enterprise Database Design with Advanced Optimization
Design star schema with optimization:

**Create schemas:**
```sql
CREATE SCHEMA sales_data;
CREATE SCHEMA analytics;
CREATE SCHEMA staging;
CREATE SCHEMA archive;
```

**Large Fact Table (billions of rows):**
```sql
CREATE TABLE sales_data.transactions (
    transaction_id BIGINT IDENTITY(1,1),
    customer_key INTEGER ENCODE az64,
    product_key INTEGER ENCODE az64,
    store_key SMALLINT ENCODE az64,
    date_key INTEGER ENCODE az64,
    time_key INTEGER ENCODE az64,
    quantity SMALLINT ENCODE az64,
    unit_price DECIMAL(12,2) ENCODE az64,
    discount_amount DECIMAL(10,2) ENCODE az64,
    tax_amount DECIMAL(10,2) ENCODE az64,
    total_amount DECIMAL(12,2) ENCODE az64,
    payment_method VARCHAR(20) ENCODE lzo,
    transaction_timestamp TIMESTAMP ENCODE az64
)
DISTKEY(customer_key)
COMPOUND SORTKEY(date_key, customer_key)
;
```

**Dimension Tables with Type 2 SCD:**
```sql
CREATE TABLE sales_data.dim_customer (
    customer_key INTEGER IDENTITY(1,1),
    customer_id VARCHAR(50),
    customer_name VARCHAR(200),
    email VARCHAR(200),
    phone VARCHAR(50),
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(50),
    customer_segment VARCHAR(50),
    effective_date DATE,
    expiration_date DATE,
    is_current BOOLEAN DEFAULT true
)
DISTSTYLE ALL
SORTKEY(customer_key);
```

**Additional dimension tables:** dim_product, dim_store, dim_date, dim_time
**Materialized views for aggregations**

### Task 4: Configure Redshift Spectrum for Data Lake Integration
Set up Spectrum external tables:

**Create external schema:**
```sql
CREATE EXTERNAL SCHEMA spectrum_data
FROM DATA CATALOG
DATABASE 'dwh_data_lake'
IAM_ROLE 'arn:aws:iam::ACCOUNT:role/RedshiftSpectrumRole-${your-student-id}'
CREATE EXTERNAL DATABASE IF NOT EXISTS;
```

**Create external table on S3:**
```sql
CREATE EXTERNAL TABLE spectrum_data.raw_transactions (
    transaction_id VARCHAR(50),
    customer_id VARCHAR(50),
    product_id VARCHAR(50),
    amount DECIMAL(12,2),
    transaction_date DATE
)
STORED AS PARQUET
LOCATION 's3://datalake-${your-student-id}/raw-transactions/'
TABLE PROPERTIES ('numRows'='1000000000');
```

**IAM Role Requirements:**
- Create `RedshiftSpectrumRole-${your-student-id}`
- Permissions: S3 read, Glue catalog access, CloudWatch Logs
- Trust relationship with Redshift service

### Task 5: Configure Data Sharing (Producer/Consumer)
Set up datashare:

**Create datashare:**
```sql
CREATE DATASHARE sales_datashare;
ALTER DATASHARE sales_datashare ADD SCHEMA sales_data;
ALTER DATASHARE sales_datashare ADD ALL TABLES IN SCHEMA sales_data;
GRANT USAGE ON DATASHARE sales_datashare TO NAMESPACE 'consumer-namespace-id';
```

### Task 6: Implement Advanced Security
Comprehensive security implementation:

**Network Security:**
- VPC with private subnets across 3 AZs
- DB subnet group: `dwh-subnet-${your-student-id}`
- Security group: `dwh-sg-${your-student-id}`
  - Inbound: PostgreSQL (5439) from corporate CIDR only
  - Outbound: HTTPS (443) for S3, Glue access
- VPC endpoints for S3 and Glue
- Network ACLs restricting traffic

**Encryption:**
- At-rest: Customer-managed KMS key with automatic rotation
- In-transit: SSL/TLS required for all connections
- Snapshot encryption with same KMS key
- Cross-region snapshot copies with different KMS key

**IAM and RBAC:**
```sql
-- Create user groups
CREATE GROUP analysts;
CREATE GROUP data_engineers;
CREATE GROUP data_scientists;
CREATE GROUP etl_service_accounts;

-- Fine-grained permissions
GRANT SELECT ON ALL TABLES IN SCHEMA sales_data TO GROUP analysts;
GRANT ALL ON SCHEMA staging TO GROUP data_engineers;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO GROUP data_scientists;

-- Row-level security
CREATE POLICY customer_region_policy
ON sales_data.transactions
FOR SELECT
USING (country = current_user_region());
```

**Audit Logging:**
- Enable audit logging to S3: `s3://redshift-audit-logs-${your-student-id}/`
- Log connection logs, user logs, user activity logs
- Enable CloudTrail for API calls
- Enable Database Audit Logging (DAL)

### Task 7: Configure Automated Maintenance and Monitoring
Advanced monitoring setup:

**CloudWatch Alarms:**
- CPUUtilization > 85% for 10 minutes
- PercentageDiskSpaceUsed > 80%
- DatabaseConnections > 450
- HealthStatus != HEALTHY
- QueriesCompletedPerSecond < 5 (anomaly detection)
- WLMQueueLength > 50

**SNS Topic**: `redshift-alerts-${your-student-id}` for alarm notifications

**Automated Maintenance:**
```sql
-- Create stored procedure for maintenance
CREATE OR REPLACE PROCEDURE maintain_tables()
AS $$
BEGIN
    -- VACUUM DELETE ONLY for large tables
    VACUUM DELETE ONLY sales_data.transactions;
    
    -- ANALYZE for all tables
    ANALYZE sales_data.transactions;
    ANALYZE sales_data.dim_customer;
    
    -- Archive old data
    INSERT INTO archive.transactions_archive
    SELECT * FROM sales_data.transactions 
    WHERE date_key < DATEADD(year, -3, CURRENT_DATE);
    
    DELETE FROM sales_data.transactions 
    WHERE date_key < DATEADD(year, -3, CURRENT_DATE);
END;
$$ LANGUAGE plpgsql;
```

**Schedule maintenance via Lambda + EventBridge**

### Task 8: Query Optimization and Performance Tuning
Implement performance best practices:

**Distribution Key Analysis:**
```sql
-- Verify distribution
SELECT slice, col, num_values, minvalue, maxvalue
FROM svv_diskusage
WHERE name = 'transactions' AND col = 0
ORDER BY slice;
```

**Query Monitoring Rules (QMR):**
```sql
-- Create QMR to log slow queries
CREATE OR REPLACE RULE abort_long_queries
FOR query_execution_time > 3600 SECONDS
LOG;

-- Rule to hop queries consuming too much temp space
CREATE OR REPLACE RULE hop_high_temp_space_queries
FOR query_temp_blocks_to_disk > 1000000
HOP TO queue_low_priority;
```

**Materialized Views:**
```sql
CREATE MATERIALIZED VIEW analytics.daily_sales_summary
AS
SELECT 
    date_key,
    customer_segment,
    COUNT(*) as transaction_count,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_transaction_value
FROM sales_data.transactions t
JOIN sales_data.dim_customer c ON t.customer_key = c.customer_key
WHERE c.is_current = true
GROUP BY date_key, customer_segment;

-- Auto refresh
REFRESH MATERIALIZED VIEW analytics.daily_sales_summary;
```

### Task 9: Disaster Recovery Testing
Implement and document DR procedures:

1. **Create manual snapshot:**
   - Snapshot Name: `dr-test-${your-student-id}-${timestamp}`
   - Copy to secondary region
   
2. **Document restore procedure:**
   - RTO: 4 hours
   - RPO: 6 hours
   
3. **Test failover:**
   - Restore from cross-region snapshot
   - Update DNS/endpoint references
   - Verify data integrity

4. **Create Lambda function for automated DR:**
   - Monitor primary cluster health
   - Trigger failover if unhealthy > 15 minutes
   - Send notifications via SNS

### Task 10: Cost Optimization
Implement cost controls:

- Enable concurrency scaling with maximum spend: $100/day
- Configure pause/resume schedules for non-prod clusters
- Use RA3 nodes for independent compute/storage scaling
- Archive cold data to S3 (>1 year old)
- Set up Cost and Usage Reports
- Create AWS Budgets alert at 80% threshold
- Tag all resources for cost allocation

## Validation

Once you've completed all tasks, run the validation script:

```bash
python validate_tasks.py redshift-hard
```

The script will verify:
- Primary and DR cluster configuration
- Custom parameter group with advanced settings
- Database schema with proper encoding and distribution
- Redshift Spectrum external schema and tables
- Data sharing configuration
- Security groups, encryption, IAM roles
- Monitoring and alarms setup
- Materialized views
- Query monitoring rules
- Cost optimization settings

## Cleanup (After Assessment)
1. Delete datashares
2. Delete external schemas and tables
3. Create final snapshots of both clusters
4. Delete/pause clusters
5. Delete cross-region snapshot copies
6. Delete custom parameter groups
7. Delete KMS keys (after 7-day waiting period)
8. Detach and delete IAM roles
9. Empty and delete S3 buckets (data, logs, audit)
10. Delete VPC endpoints, subnet groups, security groups
11. Delete CloudWatch alarms and dashboards
12. Delete SNS topics and subscriptions
13. Delete Lambda functions

## Tips
- RA3 nodes are best for large-scale production workloads
- Use COPY with manifest files for controlled data loading
- Implement slowly changing dimensions (Type 2) for historical tracking
- Leverage Spectrum for cold data analysis without loading
- Monitor WLM queue metrics to optimize concurrency
- Use automatic table optimization (ATO) for distribution keys
- Implement column-level encryption for PII data
- Test DR procedures quarterly
- Use reserved instances for cost savings on stable workloads
- Enable query monitoring rules to prevent runaway queries
- Create composite sort keys for multi-column filtering
- Use DISTSTYLE ALL for small dimension tables (<5M rows)
- Implement data lifecycle policies to archive old data
- Use federated queries to integrate RDS/Aurora data sources

## Success Criteria
- All automated tests pass
- Query performance < 5 seconds for standard reports
- DR recovery completed in < 4 hours
- Zero security vulnerabilities in AWS Security Hub
- Cost within budget constraints
- 99.9% uptime over assessment period
