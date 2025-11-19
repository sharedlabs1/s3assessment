# AWS Glue Assessment - Enterprise Data Platform (Hard)

github-repo: https://github.com/sharedlabs1/s3assessment

## Difficulty Level: 🔴 Hard

## Scenario
You are the lead data architect at GlobalCorp. Design and implement an enterprise-grade data platform using AWS Glue with advanced features including Glue Studio visual ETL, DataBrew for data preparation, custom classifiers, Schema Registry, Lake Formation integration, encryption, and comprehensive governance.

## Prerequisites
- Access to the shared AWS training account
- Python 3.8+ installed
- GitHub CLI (`gh`) installed
- Advanced knowledge of ETL, data governance, PySpark, and AWS security

## Setup

1. **Download the assessment files** (you only need these 3 files):
   - `validate_tasks.py`
   - `requirements.txt`
   - `README_glue_hard.md`

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

That's it! You're ready to start the assessment.

## Tasks to Complete

### Task 1: Create Enterprise S3 Data Lake
Set up comprehensive data lake architecture:
- **Bucket Name**: `enterprise-datalake-${your-student-id}`
- Folder structure:
  - `/landing/` - Raw data ingestion
  - `/bronze/` - Raw historical data
  - `/silver/` - Cleaned and validated data
  - `/gold/` - Business-ready aggregated data
  - `/schemas/` - Schema definitions
  - `/scripts/` - ETL scripts
  - `/logs/` - Detailed logging
  - `/athena-results/` - Query results

**Requirements:**
- Enable versioning
- Enable server-side encryption with KMS
- **KMS Key Alias**: `alias/datalake-${your-student-id}`
- Enable S3 access logging
- Configure CORS for cross-origin access
- Add bucket policy for least privilege access
- Lifecycle policies:
  - Bronze: Archive to Glacier after 90 days
  - Silver: Archive to Glacier Deep Archive after 180 days
  - Logs: Expire after 365 days
- Add tags: `Environment=Production`, `Compliance=GDPR`, `DataClassification=Confidential`, `StudentID=${your-student-id}`

### Task 2: Create Multi-Database Architecture
Create databases for medallion architecture:

**Landing Database:**
- **Name**: `landing_${your-student-id}`
- **Location**: `s3://enterprise-datalake-${your-student-id}/landing/`
- **Encryption**: Enabled

**Bronze Database:**
- **Name**: `bronze_${your-student-id}`
- **Location**: `s3://enterprise-datalake-${your-student-id}/bronze/`
- **Encryption**: Enabled

**Silver Database:**
- **Name**: `silver_${your-student-id}`
- **Location**: `s3://enterprise-datalake-${your-student-id}/silver/`
- **Encryption**: Enabled

**Gold Database:**
- **Name**: `gold_${your-student-id}`
- **Location**: `s3://enterprise-datalake-${your-student-id}/gold/`
- **Encryption**: Enabled

Add tags to all databases: `Architecture=Medallion`, `Environment=Production`, `StudentID=${your-student-id}`

### Task 3: Configure Lake Formation
Set up AWS Lake Formation for data governance:
- Register S3 location with Lake Formation
- Create Lake Formation admin role
- Configure data permissions using Lake Formation
- Enable fine-grained access control
- Set up column-level security for PII data

**Lake Formation Permissions:**
- Grant SELECT on bronze database to data analysts
- Grant ALL on silver/gold databases to data engineers
- Implement column-level masking for sensitive fields

### Task 4: Create Custom Classifier
Create custom classifier for non-standard data formats:
- **Classifier Name**: `custom-log-classifier-${your-student-id}`
- **Type**: Grok classifier
- **Grok Pattern**: Parse custom application logs

**Sample Log Format:**
```
[2024-11-01 10:15:32] INFO user_id=12345 action=login ip=192.168.1.1 duration=250ms
[2024-11-01 10:16:45] ERROR user_id=67890 action=purchase ip=192.168.1.2 error="payment_failed"
```

**Grok Pattern:**
```
\[%{TIMESTAMP_ISO8601:timestamp}\] %{LOGLEVEL:log_level} user_id=%{NUMBER:user_id} action=%{WORD:action} ip=%{IP:ip_address}( duration=%{DATA:duration})?( error="%{DATA:error_message}")?
```

### Task 5: Set Up Schema Registry
Configure Glue Schema Registry for schema evolution:
- **Registry Name**: `enterprise-registry-${your-student-id}`
- **Compatibility Mode**: BACKWARD (allow removing fields)

**Create Schemas:**
1. **Customer Schema** (Avro):
```json
{
  "type": "record",
  "name": "Customer",
  "namespace": "com.datacorp.customer",
  "fields": [
    {"name": "customer_id", "type": "string"},
    {"name": "name", "type": "string"},
    {"name": "email", "type": ["null", "string"], "default": null},
    {"name": "phone", "type": ["null", "string"], "default": null},
    {"name": "created_at", "type": "long", "logicalType": "timestamp-millis"}
  ]
}
```

2. **Transaction Schema** (Avro):
```json
{
  "type": "record",
  "name": "Transaction",
  "namespace": "com.datacorp.transaction",
  "fields": [
    {"name": "transaction_id", "type": "string"},
    {"name": "customer_id", "type": "string"},
    {"name": "amount", "type": "double"},
    {"name": "currency", "type": "string", "default": "USD"},
    {"name": "timestamp", "type": "long", "logicalType": "timestamp-millis"},
    {"name": "status", "type": {"type": "enum", "name": "Status", "symbols": ["PENDING", "COMPLETED", "FAILED"]}}
  ]
}
```

### Task 6: Create Advanced Crawler with Custom Classifier
Create enterprise crawler:
- **Crawler Name**: `enterprise-crawler-${your-student-id}`
- **Custom Classifier**: Use custom log classifier from Task 4
- **Data Sources**: Multiple S3 paths (landing/bronze)
- **Target Databases**: Landing and bronze databases
- **Schedule**: Hourly (cron: `0 * * * ? *`)
- **Configuration**:
  - Enable partition detection with custom keys
  - Configure table prefix: `tbl_`
  - Schema change policy: Update and create new columns
  - Object deletion: Mark table as deprecated
  - Enable configuration optimization
  - Sample size: 10MB per path
- **Recrawl Policy**: Crawl all folders
- **Security Configuration**: Use encryption config
- Add tags: `Enterprise=Yes`, `Governance=Enabled`, `StudentID=${your-student-id}`

### Task 7: Create DataBrew Project
Use AWS Glue DataBrew for data quality and preparation:
- **Project Name**: `data-quality-project-${your-student-id}`
- **Dataset Name**: `customer-data-${your-student-id}`
- **Data Source**: S3 or Glue Data Catalog table
- **IAM Role**: DataBrew service role

**Data Quality Rules:**
1. Remove duplicate records
2. Handle missing values in critical fields
3. Validate email format using regex
4. Standardize phone numbers
5. Detect and flag outliers in amount field
6. Convert dates to standard format
7. Trim whitespace from text fields

**Create Recipe:**
- Recipe Name: `clean-customer-data-${your-student-id}`
- **Recipe Steps**:
  1. Remove duplicates based on customer_id
  2. Fill missing emails with "unknown@example.com"
  3. Validate email format: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
  4. Change column type for created_at to datetime
  5. Delete rows where customer_id is null
  6. Flag outliers in amount field (3 standard deviations)

### Task 8: Create Glue Studio Visual ETL Job
Build complex ETL using Glue Studio:
- **Job Name**: `studio-etl-pipeline-${your-student-id}`
- **Type**: Visual ETL with diagram
- **Glue Version**: 4.0

**Visual ETL Flow:**
1. **Source 1**: Read from bronze database - customers table
2. **Source 2**: Read from bronze database - transactions table
3. **Join**: Inner join on customer_id
4. **Filter**: Remove invalid transactions (amount <= 0)
5. **Aggregate**: Calculate total spent per customer
6. **Transform**: Add derived columns:
   - `customer_segment` (High/Medium/Low based on total_spent)
   - `processing_date` (current date)
   - `data_quality_score` (calculated field)
7. **Split**: Separate into high-value and regular customers
8. **Target 1**: Write high-value customers to gold database
9. **Target 2**: Write regular customers to silver database

**Job Configuration:**
- Workers: 10 (G.2X)
- Job bookmarks: Enabled
- Flex execution: Enabled (for cost optimization)
- Max concurrent runs: 5
- Encryption: Enabled (S3 and CloudWatch)
- Enable Spark UI with S3 logs
- Enable continuous logging
- Enable job metrics

### Task 9: Implement Streaming ETL
Create real-time streaming ETL job:
- **Job Name**: `streaming-etl-${your-student-id}`
- **Type**: Spark Streaming ETL
- **Source**: Kinesis Data Stream or Kafka (create stream first)
- **Processing**: Window-based aggregations
- **Target**: Write to silver database

**Streaming Job Script:**
```python
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import DataFrame, functions as F
from pyspark.sql.types import *
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.window import Window

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read streaming data
streaming_df = glueContext.create_data_frame.from_options(
    connection_type="kinesis",
    connection_options={
        "streamName": "transactions-stream-STUDENTID",
        "startingPosition": "TRIM_HORIZON",
        "inferSchema": "true"
    }
)

# Window aggregations
windowed_df = streaming_df \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(
        F.window("timestamp", "5 minutes", "1 minute"),
        "product_id"
    ) \
    .agg(
        F.count("transaction_id").alias("transaction_count"),
        F.sum("amount").alias("total_revenue"),
        F.avg("amount").alias("avg_transaction_value")
    )

# Write streaming results
query = windowed_df.writeStream \
    .outputMode("append") \
    .format("parquet") \
    .option("path", "s3://enterprise-datalake-STUDENTID/silver/streaming_results/") \
    .option("checkpointLocation", "s3://enterprise-datalake-STUDENTID/checkpoints/streaming/") \
    .start()

query.awaitTermination()
```

### Task 10: Create Complex Workflow with Multiple Triggers
Build enterprise workflow:
- **Workflow Name**: `enterprise-pipeline-${your-student-id}`

**Workflow Stages:**
1. **Stage 1 - Ingestion**:
   - Crawler: Scan landing zone
   - Trigger: On completion

2. **Stage 2 - Data Quality**:
   - DataBrew job: Clean and validate
   - Conditional trigger: Only if crawler found new data

3. **Stage 3 - Bronze Processing**:
   - ETL Job: Move to bronze layer
   - Parallel execution: Multiple jobs for different datasets

4. **Stage 4 - Silver Processing**:
   - ETL Job: Transform to silver layer
   - Data quality checks
   - Conditional trigger: Only if bronze succeeded

5. **Stage 5 - Gold Processing**:
   - Studio Visual ETL: Create business aggregates
   - Trigger: On silver completion

6. **Stage 6 - Notification**:
   - Lambda function: Send completion notification
   - Update metadata catalog

**Workflow Triggers:**
- **Event-based trigger**: S3 event when new file lands
- **Scheduled trigger**: Daily at 1:00 AM UTC
- **Conditional trigger**: Based on previous job success/failure

### Task 11: Implement Data Quality Framework
Create comprehensive data quality checks:

**Data Quality Rulesets:**

1. **Schema Validation Ruleset:**
```
Rules = [
    ColumnExists "customer_id",
    ColumnExists "transaction_id",
    ColumnExists "amount",
    ColumnDataType "customer_id" = "STRING",
    ColumnDataType "amount" = "FRACTIONAL",
    ColumnLength "customer_id" between 5 and 50
]
```

2. **Business Rules Ruleset:**
```
Rules = [
    ColumnValues "amount" between 0.01 and 1000000,
    ColumnValues "currency" in ["USD", "EUR", "GBP"],
    RowCount between 1000 and 10000000,
    CustomSQL "SELECT COUNT(*) FROM $table WHERE amount < 0" = 0,
    Uniqueness "transaction_id" > 0.99,
    Completeness "customer_id" > 0.95
]
```

3. **Anomaly Detection Ruleset:**
```
Rules = [
    Mean "amount" between 50 and 500,
    StandardDeviation "amount" < 1000,
    CustomSQL "SELECT AVG(amount) FROM $table WHERE date = CURRENT_DATE" within 20% of historical average
]
```

### Task 12: Configure Security and Encryption
Implement comprehensive security:

**Security Configuration:**
- **Name**: `enterprise-security-config-${your-student-id}`
- **S3 Encryption**: SSE-KMS with custom key
- **CloudWatch Logs Encryption**: Enabled with KMS
- **Job Bookmarks Encryption**: Enabled with KMS

**Secrets Manager Integration:**
- Store database credentials in Secrets Manager
- Reference secrets in Glue jobs
- Enable automatic rotation

**IAM Roles:**
1. **Glue Service Role**: Least privilege access
2. **DataBrew Role**: Limited to specific S3 paths
3. **Lake Formation Admin Role**: Data governance
4. **Cross-Account Access Role**: For shared data catalog

### Task 13: Implement Monitoring and Observability
Set up comprehensive monitoring:

**CloudWatch Dashboards:**
- **Dashboard Name**: `glue-pipeline-metrics-${your-student-id}`
- **Widgets**:
  - Job success/failure rates
  - Job duration trends
  - DPU utilization
  - Data quality score trends
  - Cost per job
  - Crawler run statistics

**CloudWatch Alarms:**
1. Job failure rate > 10%
2. Job duration > 60 minutes
3. DPU usage > 80% of allocated
4. Data quality score < 90%
5. Cost per day > budget threshold

**SNS Topics:**
- `glue-critical-alerts-${your-student-id}`: P1 incidents
- `glue-warnings-${your-student-id}`: P2 warnings
- `glue-info-${your-student-id}`: Informational

**EventBridge Rules:**
- Capture all Glue state changes
- Send to Lambda for custom processing
- Archive to S3 for audit trail

### Task 14: Create Development and Testing Infrastructure
Set up development environment:

**Development Endpoint:**
- Interactive Jupyter/Zeppelin notebooks
- Shared endpoint for team collaboration

**CI/CD Pipeline:**
- Store Glue scripts in Git repository
- Use AWS CodePipeline for deployment
- Implement testing in Dev environment
- Promote to Prod after validation

**Unit Testing:**
- Create PyTest framework for Glue jobs
- Test transformations with sample data
- Validate schema evolution
- Test data quality rules

### Task 15: Implement Cost Optimization
Configure cost optimization:
- Enable Glue Flex execution for non-time-sensitive jobs
- Use auto-scaling for worker allocation
- Implement job bookmarks to avoid reprocessing
- Configure appropriate worker types (G.1X vs G.2X)
- Set up cost allocation tags
- Create AWS Budget alerts
- Analyze CloudWatch metrics for right-sizing
- Archive old data to cheaper storage tiers

## Validation

Once you've completed all tasks, run the validation script:

```bash
python validate_tasks.py glue_hard
```

The script will verify:
- S3 data lake with encryption and policies
- Multi-database medallion architecture
- Lake Formation configuration
- Custom classifiers
- Schema Registry with schemas
- Advanced crawler configuration
- DataBrew project and recipe
- Glue Studio visual ETL job
- Streaming ETL job (if applicable)
- Complex workflow with multiple stages
- Data quality rulesets
- Security configuration
- Monitoring dashboards and alarms
- IAM roles with proper permissions
- Job execution history and metrics

## Cleanup (After Assessment)
1. Stop streaming jobs
2. Delete workflows and triggers
3. Delete all Glue jobs
4. Delete DataBrew projects and recipes
5. Delete crawlers
6. Delete custom classifiers
7. Delete Schema Registry and schemas
8. Delete data quality rulesets
9. Delete Lake Formation permissions
10. Delete databases and tables
11. Delete CloudWatch dashboards and alarms
12. Delete SNS topics and subscriptions
13. Delete EventBridge rules
14. Delete Lambda functions
15. Delete security configurations
16. Empty and delete S3 bucket
17. Delete KMS keys (after waiting period)
18. Delete IAM roles and policies
19. Delete Secrets Manager secrets

## Tips
- Lake Formation provides centralized data governance
- Schema Registry enables schema evolution without breaking consumers
- Custom classifiers handle non-standard data formats
- DataBrew offers visual data preparation without code
- Glue Studio simplifies complex ETL with drag-and-drop
- Flex execution reduces costs for non-critical jobs
- Use medallion architecture (bronze/silver/gold) for data maturity
- Implement column-level security for PII data
- Enable audit logging for compliance
- Use Glue connections for JDBC data sources
- Partition large tables by date for performance
- Monitor DPU usage to optimize worker allocation
- Test data quality rules with diverse datasets
- Implement data lineage tracking
- Use Glue blueprints for common patterns

## Common Issues
- **Lake Formation conflicts**: Ensure IAM and LF permissions align
- **Schema Registry incompatibility**: Check compatibility mode settings
- **Custom classifier not applied**: Verify classifier order and pattern
- **DataBrew job fails**: Check IAM role permissions for S3 access
- **Streaming job lag**: Increase worker count or adjust batch interval
- **Encryption errors**: Ensure KMS key policies allow Glue access
- **Workflow stuck**: Check conditional trigger logic
- **High costs**: Review worker types and enable Flex execution
- **Data quality failures**: Validate rules against actual data patterns

## Learning Resources
- AWS Lake Formation best practices
- Glue Schema Registry documentation
- DataBrew transformation reference
- Medallion architecture patterns
- PySpark performance tuning
- Data governance frameworks
- Column-level security implementation
- Cost optimization strategies
- Real-time streaming with Glue
- Glue Studio visual design patterns
