# AWS Glue Assessment - Advanced ETL & Automation (Medium)

github-repo: https://github.com/sharedlabs1/s3assessment

## Difficulty Level: 🟡 Medium

## Scenario
You are a senior data engineer at DataCorp. Build a production-ready ETL pipeline with automated workflows, job bookmarks for incremental processing, data quality checks, and scheduled execution.

## Prerequisites
- Access to the shared AWS training account
- Python 3.8+ installed
- GitHub CLI (`gh`) installed
- Understanding of ETL workflows, PySpark, and data quality concepts

## Setup

1. **Download the assessment files** (you only need these 3 files):
   - `validate_tasks.py`
   - `requirements.txt`
   - `README_glue_medium.md`

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

That's it! You're ready to start the assessment.

## Tasks to Complete

### Task 1: Create S3 Data Infrastructure
Set up comprehensive S3 structure:
- **Bucket Name**: `glue-pipeline-${your-student-id}`
- Folder structure:
  - `/raw/transactions/` - Daily transaction files
  - `/raw/products/` - Product catalog
  - `/staging/` - Intermediate processing
  - `/processed/` - Final output
  - `/scripts/` - Glue job scripts
  - `/temp/` - Temporary files
  - `/logs/` - Custom logs

**Sample Transaction Data** (transactions_2024-11-01.csv):
```csv
transaction_id,product_id,customer_id,quantity,price,timestamp
T1001,P100,C501,2,29.99,2024-11-01 10:15:00
T1002,P102,C502,1,149.99,2024-11-01 10:30:00
T1003,P101,C501,3,19.99,2024-11-01 11:00:00
```

**Requirements:**
- Enable versioning
- Add lifecycle policy to archive old data to S3 Glacier after 90 days
- Add tags: `Environment=Production`, `DataPipeline=ETL`, `StudentID=${your-student-id}`

### Task 2: Create Glue Databases
Create multiple databases for different stages:

**Raw Database:**
- **Name**: `raw_data_${your-student-id}`
- **Description**: "Raw data from source systems"

**Processed Database:**
- **Name**: `processed_data_${your-student-id}`
- **Description**: "Cleaned and transformed data"

Add tags to both: `Environment=Production`, `StudentID=${your-student-id}`

### Task 3: Create Enhanced IAM Role
Create comprehensive IAM role:
- **Role Name**: `GlueProductionRole-${your-student-id}`
- **Permissions**:
  - AWSGlueServiceRole
  - AWSGlueConsoleFullAccess (for Glue Studio)
  - S3 full access to pipeline bucket
  - CloudWatch Logs full access
  - SNS publish for notifications
  - Pass role permission for Glue

### Task 4: Create Crawler with Partition Detection
Create advanced crawler:
- **Crawler Name**: `transactions-crawler-${your-student-id}`
- **Data Source**: `s3://glue-pipeline-${your-student-id}/raw/transactions/`
- **Target Database**: raw_data database
- **Schedule**: Daily at 2:00 AM UTC (cron: `0 2 * * ? *`)
- **Configuration**:
  - Enable partition detection
  - Create new partitions based on date
  - Update table schema if detected
  - Configure grouping: Create separate tables for each top-level folder
- **Schema Change Policy**:
  - Update the table definition in Data Catalog
  - Log schema changes
- Add tags: `DataSource=Transactions`, `Scheduled=Yes`, `StudentID=${your-student-id}`

### Task 5: Create ETL Job with Job Bookmarks
Create incremental processing job:
- **Job Name**: `incremental-etl-${your-student-id}`
- **Glue Version**: 4.0
- **Worker Type**: G.1X
- **Number of Workers**: 5
- **Job Bookmarks**: Enabled (for incremental processing)
- **Max Retries**: 2
- **Timeout**: 30 minutes
- **Max Concurrent Runs**: 3

**ETL Script with Bookmarks:**
```python
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql.functions import col, sum, count, avg, current_timestamp

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Job bookmarks will track processed data
transactions_dyf = glueContext.create_dynamic_frame.from_catalog(
    database="raw_data_STUDENTID",
    table_name="transactions",
    transformation_ctx="transactions_dyf"  # Required for bookmarks
)

# Convert to DataFrame for transformations
df = transactions_dyf.toDF()

# Data transformations
df_cleaned = df.filter(col("quantity") > 0) \
               .filter(col("price") > 0) \
               .withColumn("total_amount", col("quantity") * col("price")) \
               .withColumn("processing_timestamp", current_timestamp())

# Aggregate by product
product_summary = df_cleaned.groupBy("product_id") \
    .agg(
        count("transaction_id").alias("transaction_count"),
        sum("quantity").alias("total_quantity"),
        sum("total_amount").alias("total_revenue"),
        avg("price").alias("avg_price")
    )

# Convert back to DynamicFrame
result_dyf = DynamicFrame.fromDF(product_summary, glueContext, "result_dyf")

# Write to processed database
glueContext.write_dynamic_frame.from_catalog(
    frame=result_dyf,
    database="processed_data_STUDENTID",
    table_name="product_summary",
    transformation_ctx="write_result"  # Required for bookmarks
)

job.commit()
```

**Job Parameters:**
- `--enable-metrics` (for CloudWatch metrics)
- `--enable-continuous-cloudwatch-log` (for real-time logs)
- `--enable-spark-ui` (for Spark UI)

### Task 6: Create Glue Workflow
Create automated workflow:
- **Workflow Name**: `etl-pipeline-${your-student-id}`
- **Description**: "Automated ETL pipeline with crawler and job"

**Workflow Steps:**
1. **Crawler Node**: Run transactions crawler
2. **Job Node**: Run incremental ETL job (triggers after crawler succeeds)

**Workflow Configuration:**
- Add trigger conditions
- Configure error handling
- Add tags: `Automation=Workflow`, `StudentID=${your-student-id}`

### Task 7: Create Workflow Triggers
Create triggers to automate workflow:

**Scheduled Trigger:**
- **Trigger Name**: `daily-trigger-${your-student-id}`
- **Type**: Scheduled
- **Schedule**: Daily at 3:00 AM UTC (cron: `0 3 * * ? *`)
- **Actions**: Start the workflow
- **Description**: "Daily automated ETL pipeline execution"

**On-Demand Trigger:**
- **Trigger Name**: `manual-trigger-${your-student-id}`
- **Type**: On-demand
- **Actions**: Start the workflow
- **Description**: "Manual workflow execution"

### Task 8: Implement Data Quality Rules
Create Glue Data Quality ruleset:
- **Ruleset Name**: `transaction-quality-${your-student-id}`
- **Target Table**: transactions table in raw_data database

**Quality Rules:**
```
Rules = [
    RowCount > 0,
    IsComplete "transaction_id",
    IsComplete "product_id",
    IsComplete "customer_id",
    IsComplete "quantity",
    IsComplete "price",
    ColumnValues "quantity" > 0,
    ColumnValues "price" > 0,
    ColumnValues "price" < 10000,
    IsUnique "transaction_id",
    ColumnDataType "transaction_id" = "STRING",
    ColumnDataType "quantity" = "INTEGRAL",
    ColumnDataType "price" = "FRACTIONAL"
]
```

**Configuration:**
- Run data quality checks before ETL job
- Publish results to CloudWatch
- Send alerts if rules fail

### Task 9: Configure Job Monitoring
Set up comprehensive monitoring:

**CloudWatch Alarms:**
1. **Job Failure Alarm**:
   - Alarm Name: `glue-job-failure-${your-student-id}`
   - Metric: Job failures
   - Threshold: >= 1 failure
   - Period: 5 minutes

2. **Job Duration Alarm**:
   - Alarm Name: `glue-job-duration-${your-student-id}`
   - Metric: Job execution time
   - Threshold: > 20 minutes
   - Period: 5 minutes

**SNS Topic:**
- Topic Name: `glue-alerts-${your-student-id}`
- Subscription: Email notification

### Task 10: Create Development Endpoint (Optional)
Create development endpoint for interactive testing:
- **Endpoint Name**: `dev-endpoint-${your-student-id}`
- **IAM Role**: Use production role
- **Worker Type**: G.1X
- **Number of Workers**: 2
- **Glue Version**: 4.0
- **Public Key**: (for SSH access - optional)

Add tags: `Purpose=Development`, `StudentID=${your-student-id}`

### Task 11: Implement Job Parameterization
Create parameterized version of ETL job:
- **Job Name**: `parameterized-etl-${your-student-id}`
- **Default Parameters**:
  - `--source_database`: raw_data database name
  - `--target_database`: processed_data database name
  - `--source_table`: transactions
  - `--processing_date`: Current date
  - `--output_format`: parquet

This allows flexible execution with different parameters.

### Task 12: Execute and Validate Workflow
Run the complete workflow:
1. Trigger workflow manually using on-demand trigger
2. Monitor crawler execution
3. Wait for ETL job to start automatically
4. Check data quality results
5. Verify output in processed database
6. Review CloudWatch metrics and logs
7. Confirm job bookmarks are working (run again with new data)

## Validation

Once you've completed all tasks, run the validation script:

```bash
python validate_tasks.py glue_medium
```

The script will verify:
- S3 bucket with versioning and lifecycle policy
- Multiple Glue databases
- IAM role with comprehensive permissions
- Crawler with schedule and partition detection
- ETL job with job bookmarks enabled
- Workflow with multiple nodes
- Triggers (scheduled and on-demand)
- Data quality ruleset
- CloudWatch alarms
- Job execution history
- Processed data output

## Cleanup (After Assessment)
1. Stop and delete development endpoint
2. Disable and delete triggers
3. Delete workflow
4. Delete jobs
5. Delete crawlers
6. Delete data quality rulesets
7. Delete tables and databases
8. Delete CloudWatch alarms
9. Delete SNS topic
10. Empty and delete S3 bucket
11. Delete IAM role

## Tips
- Job bookmarks prevent reprocessing the same data
- Use transformation_ctx parameter consistently for bookmarks
- Workflows provide visual representation of ETL pipelines
- Data quality rules ensure data integrity
- Use G.2X workers for larger datasets
- Enable Spark UI for performance troubleshooting
- Partition data by date for efficient querying
- Test data quality rules with sample data first
- Use separate databases for different data stages
- Monitor job metrics to optimize worker allocation

## Common Issues
- **Bookmarks not working**: Missing transformation_ctx parameter
- **Workflow stuck**: Check crawler/job status and error logs
- **Data quality fails**: Review rules and actual data format
- **Job timeout**: Increase worker count or timeout setting
- **Trigger doesn't fire**: Verify cron expression and timezone (UTC)
- **Permission errors**: Ensure IAM role has all required policies

## Learning Resources
- Glue job bookmarks documentation
- Workflow orchestration patterns
- Data quality rule syntax
- PySpark transformation best practices
- Partition strategy for large datasets
- Glue performance tuning guide
