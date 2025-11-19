# AWS Glue Assessment - Data Catalog & ETL Basics (Easy)

github-repo: https://github.com/sharedlabs1/s3assessment

## Difficulty Level: 🟢 Easy

## Scenario
You are a data engineer at DataCorp. Set up a basic AWS Glue environment to catalog and transform data from S3 using crawlers and ETL jobs.

## Prerequisites
- Access to the shared AWS training account
- Python 3.8+ installed
- GitHub CLI (`gh`) installed
- Basic understanding of ETL concepts and data formats

## Setup

1. **Download the assessment files** (you only need these 3 files):
   - `validate_tasks.py`
   - `requirements.txt`
   - `README_glue_easy.md`

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

That's it! You're ready to start the assessment.

## Tasks to Complete

### Task 1: Create S3 Data Source
Set up S3 bucket with sample data:
- **Bucket Name**: `glue-data-${your-student-id}`
- Create folder structure:
  - `/raw/customers/` - CSV files with customer data
  - `/raw/orders/` - JSON files with order data
  - `/processed/` - Output folder for transformed data

**Sample Customer Data** (customers.csv):
```csv
customer_id,name,email,country,signup_date
1,John Doe,john@example.com,USA,2024-01-15
2,Jane Smith,jane@example.com,UK,2024-02-20
3,Bob Johnson,bob@example.com,Canada,2024-03-10
```

**Sample Order Data** (orders.json):
```json
{"order_id": 1001, "customer_id": 1, "amount": 150.50, "order_date": "2024-05-01"}
{"order_id": 1002, "customer_id": 2, "amount": 200.75, "order_date": "2024-05-02"}
{"order_id": 1003, "customer_id": 1, "amount": 89.99, "order_date": "2024-05-03"}
```

**Requirements:**
- Upload sample files to respective folders
- Set appropriate bucket permissions
- Add tags: `Environment=Development`, `Project=GlueBasics`, `StudentID=${your-student-id}`

### Task 2: Create Glue Database
Create a Glue Data Catalog database:
- **Database Name**: `datacatalog_${your-student-id}`
- **Description**: "Data catalog for ETL processing"
- Add tags: `Environment=Development`, `StudentID=${your-student-id}`

### Task 3: Create IAM Role for Glue
Create IAM role for Glue services:
- **Role Name**: `GlueServiceRole-${your-student-id}`
- **Trust Relationship**: Allow Glue service
- **Permissions**:
  - AWSGlueServiceRole (AWS managed policy)
  - S3 read/write access to your bucket
  - CloudWatch Logs write access

**Example trust policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "glue.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### Task 4: Create Glue Crawler for Customers
Create a crawler to discover customer data schema:
- **Crawler Name**: `customers-crawler-${your-student-id}`
- **IAM Role**: Use role from Task 3
- **Data Source**: S3 path `s3://glue-data-${your-student-id}/raw/customers/`
- **Target Database**: Database from Task 2
- **Schedule**: Run on demand
- **Configuration**:
  - Create a single schema for each S3 path
  - Add new tables and update existing ones
- Add tags: `DataSource=Customers`, `StudentID=${your-student-id}`

### Task 5: Create Glue Crawler for Orders
Create a crawler to discover order data schema:
- **Crawler Name**: `orders-crawler-${your-student-id}`
- **IAM Role**: Use role from Task 3
- **Data Source**: S3 path `s3://glue-data-${your-student-id}/raw/orders/`
- **Target Database**: Database from Task 2
- **Schedule**: Run on demand
- **Configuration**:
  - Create a single schema for each S3 path
  - Add new tables and update existing ones
- Add tags: `DataSource=Orders`, `StudentID=${your-student-id}`

### Task 6: Run Crawlers
Execute both crawlers:
1. Run customers crawler and wait for completion
2. Run orders crawler and wait for completion
3. Verify tables are created in Data Catalog:
   - `customers` table should appear
   - `orders` table should appear
4. Check table schemas in AWS Glue Console

### Task 7: Create Basic ETL Job
Create a Glue ETL job to join customer and order data:
- **Job Name**: `customer-orders-job-${your-student-id}`
- **IAM Role**: Use role from Task 3
- **Type**: Spark ETL job
- **Glue Version**: 4.0
- **Language**: Python 3
- **Worker Type**: G.1X
- **Number of Workers**: 2
- **Script Location**: `s3://glue-data-${your-student-id}/scripts/`
- **Temporary Directory**: `s3://glue-data-${your-student-id}/temp/`

**ETL Script** (customer_orders_etl.py):
```python
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read data from Glue Data Catalog
customers_df = glueContext.create_dynamic_frame.from_catalog(
    database="datacatalog_STUDENTID",
    table_name="customers"
).toDF()

orders_df = glueContext.create_dynamic_frame.from_catalog(
    database="datacatalog_STUDENTID",
    table_name="orders"
).toDF()

# Join customer and order data
joined_df = orders_df.join(customers_df, "customer_id", "inner")

# Select relevant columns
result_df = joined_df.select(
    "order_id",
    "customer_id",
    "name",
    "email",
    "country",
    "amount",
    "order_date"
)

# Write output to S3
result_df.write.mode("overwrite").parquet(
    "s3://glue-data-STUDENTID/processed/customer_orders/"
)

job.commit()
```

**Job Configuration:**
- Max concurrency: 1
- Timeout: 10 minutes
- Max retries: 0
- Add tags: `JobType=ETL`, `StudentID=${your-student-id}`

### Task 8: Run ETL Job
Execute the ETL job:
1. Trigger the job manually
2. Monitor job execution in Glue Console
3. Wait for job to complete successfully
4. Verify output in S3: `s3://glue-data-${your-student-id}/processed/customer_orders/`
5. Check CloudWatch Logs for job execution details

## Validation

Once you've completed all tasks, run the validation script:

```bash
python validate_tasks.py glue_easy
```

The script will verify:
- S3 bucket with correct folder structure
- Glue database exists
- IAM role with appropriate permissions
- Both crawlers created and executed
- Tables exist in Data Catalog
- ETL job created
- Job execution history
- Output data in processed folder

## Cleanup (After Assessment)
1. Delete Glue ETL job
2. Delete crawlers
3. Delete tables from Data Catalog
4. Delete Glue database
5. Empty and delete S3 bucket
6. Delete IAM role and policies

## Tips
- Use AWS Glue Console to visually inspect Data Catalog
- Crawlers automatically detect schema from data
- Check CloudWatch Logs if job fails
- Use Glue Studio for visual ETL design (optional)
- Parquet format is more efficient than CSV for analytics
- Test with small datasets first before scaling
- Review job metrics after execution
- Use IAM roles instead of hardcoded credentials

## Common Issues
- **Crawler fails**: Check IAM role permissions for S3 access
- **Job fails**: Verify script location and temporary directory exist
- **No tables created**: Ensure data files are in correct S3 paths
- **Join fails**: Verify column names match between datasets
- **Permission denied**: Check IAM role policies include necessary S3 and Glue permissions

## Learning Resources
- AWS Glue Data Catalog overview
- Apache Spark transformations
- Glue DynamicFrame vs Spark DataFrame
- Data partitioning strategies
- Glue job monitoring and debugging
