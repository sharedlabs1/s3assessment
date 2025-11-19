# AWS EMR Assessment - Medium

## Overview
Master advanced EMR features including EMR Serverless for cost-efficient processing, Apache Hive and Presto for SQL analytics, Step Functions for workflow orchestration, and production best practices like spot instances and auto-scaling.

**Difficulty**: Medium  
**Prerequisites**: EMR Easy completion, SQL knowledge  
**Estimated Time**: 3-4 hours  

## Learning Objectives
- Deploy EMR Serverless applications
- Use Apache Hive for data warehousing
- Query with Presto/Trino for interactive analytics
- Orchestrate EMR jobs with Step Functions
- Integrate with AWS Glue Data Catalog
- Optimize costs with Spot instances
- Implement auto-scaling policies
- Build multi-step ETL pipelines

## Prerequisites
- Completed EMR Easy assessment
- S3 bucket: emr-{student_id}
- Sample data in S3
- IAM roles configured

---

## Tasks

### Task 1: EMR Serverless Application
**Objective**: Create EMR Serverless application for running Spark jobs without managing clusters.

**Create application**:
```bash
# Create EMR Serverless application
aws emr-serverless create-application \
  --name "spark-app-{student_id}" \
  --type "SPARK" \
  --release-label "emr-6.15.0" \
  --initial-capacity '{
    "DRIVER": {
      "workerCount": 1,
      "workerConfiguration": {
        "cpu": "2vCPU",
        "memory": "4GB"
      }
    },
    "EXECUTOR": {
      "workerCount": 2,
      "workerConfiguration": {
        "cpu": "4vCPU",
        "memory": "8GB"
      }
    }
  }' \
  --maximum-capacity '{
    "cpu": "200vCPU",
    "memory": "100GB"
  }' \
  --auto-start-configuration enabled=true \
  --auto-stop-configuration enabled=true,idleTimeoutMinutes=15

# Get application ID
aws emr-serverless list-applications \
  --query "applications[?name=='spark-app-{student_id}'].id" \
  --output text
```

**Save application ID**:
```bash
APP_ID=$(aws emr-serverless list-applications \
  --query "applications[?name=='spark-app-{student_id}'].id" \
  --output text)

echo $APP_ID > emr-serverless-app-id.txt
```

---

### Task 2: Submit Jobs to EMR Serverless
**Objective**: Run Spark applications using EMR Serverless.

**Create Spark job script** (`scripts/serverless_spark_job.py`):
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, avg, count, to_date

# Initialize Spark
spark = SparkSession.builder \
    .appName("EMR Serverless Sales Analysis") \
    .getOrCreate()

# Read data from S3
df = spark.read.csv("s3://emr-{student_id}/data/sales.csv", 
                    header=True, inferSchema=True)

# Transform data
sales_summary = df.groupBy("product_category", to_date(col("sale_date")).alias("date")) \
    .agg(
        sum("amount").alias("total_sales"),
        avg("amount").alias("avg_sale"),
        count("order_id").alias("order_count")
    ) \
    .orderBy("date", "product_category")

# Write results
sales_summary.write \
    .mode("overwrite") \
    .partitionBy("date") \
    .parquet("s3://emr-{student_id}/output/serverless-sales-summary/")

print(f"Processed {df.count()} records")
print(f"Generated {sales_summary.count()} summary records")

spark.stop()
```

**Upload script and submit job**:
```bash
# Upload script
aws s3 cp scripts/serverless_spark_job.py s3://emr-{student_id}/scripts/

# Get role ARN
ROLE_ARN=$(aws iam get-role --role-name EMRServerlessRole-{student_id} --query 'Role.Arn' --output text)

# Submit job
aws emr-serverless start-job-run \
  --application-id $APP_ID \
  --execution-role-arn $ROLE_ARN \
  --job-driver '{
    "sparkSubmit": {
      "entryPoint": "s3://emr-{student_id}/scripts/serverless_spark_job.py",
      "sparkSubmitParameters": "--conf spark.executor.memory=4g --conf spark.executor.cores=2"
    }
  }' \
  --configuration-overrides '{
    "monitoringConfiguration": {
      "s3MonitoringConfiguration": {
        "logUri": "s3://emr-{student_id}/logs/serverless/"
      }
    }
  }'
```

**Check job status**:
```bash
# Get job run ID
JOB_RUN_ID=$(aws emr-serverless list-job-runs \
  --application-id $APP_ID \
  --query 'jobRuns[0].id' \
  --output text)

# Check status
aws emr-serverless get-job-run \
  --application-id $APP_ID \
  --job-run-id $JOB_RUN_ID
```

---

### Task 3: Apache Hive on EMR
**Objective**: Set up Hive tables and run SQL queries on S3 data.

**Create EMR cluster with Hive**:
```bash
aws emr create-cluster \
  --name "Hive-Cluster-{student_id}" \
  --release-label emr-6.15.0 \
  --applications Name=Hive Name=Hadoop \
  --instance-type m5.xlarge \
  --instance-count 3 \
  --use-default-roles \
  --ec2-attributes KeyName=my-key-pair \
  --log-uri s3://emr-{student_id}/logs/hive/
```

**Create Hive external table** (`scripts/create_hive_table.hql`):
```sql
-- Create database
CREATE DATABASE IF NOT EXISTS sales_db;

USE sales_db;

-- Create external table pointing to S3
CREATE EXTERNAL TABLE IF NOT EXISTS sales (
    order_id STRING,
    customer_id STRING,
    product_id STRING,
    product_category STRING,
    amount DECIMAL(10,2),
    sale_date DATE,
    region STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION 's3://emr-{student_id}/data/hive/sales/'
TBLPROPERTIES ('skip.header.line.count'='1');

-- Create aggregated table (managed table)
CREATE TABLE IF NOT EXISTS daily_sales_summary (
    sale_date DATE,
    product_category STRING,
    total_sales DECIMAL(12,2),
    order_count BIGINT
)
STORED AS PARQUET;

-- Populate summary table
INSERT OVERWRITE TABLE daily_sales_summary
SELECT 
    sale_date,
    product_category,
    SUM(amount) as total_sales,
    COUNT(*) as order_count
FROM sales
GROUP BY sale_date, product_category;

-- Query summary
SELECT * FROM daily_sales_summary
ORDER BY sale_date DESC, total_sales DESC
LIMIT 100;
```

**Run Hive query via EMR step**:
```bash
# Upload Hive script
aws s3 cp scripts/create_hive_table.hql s3://emr-{student_id}/scripts/

# Add step to cluster
aws emr add-steps \
  --cluster-id <cluster-id> \
  --steps Type=HIVE,Name="Create Sales Tables",ActionOnFailure=CONTINUE,Args=[-f,s3://emr-{student_id}/scripts/create_hive_table.hql]
```

---

### Task 4: Presto on EMR
**Objective**: Configure Presto for interactive SQL analytics.

**Create cluster with Presto**:
```bash
aws emr create-cluster \
  --name "Presto-Cluster-{student_id}" \
  --release-label emr-6.15.0 \
  --applications Name=Presto Name=Hive \
  --instance-type m5.xlarge \
  --instance-count 3 \
  --use-default-roles
```

**Presto query script** (`scripts/presto_queries.sql`):
```sql
-- Query using Presto CLI
-- Connect to Hive metastore

-- Query 1: Top selling products
SELECT 
    product_category,
    COUNT(*) as order_count,
    SUM(amount) as total_revenue,
    AVG(amount) as avg_order_value
FROM hive.sales_db.sales
GROUP BY product_category
ORDER BY total_revenue DESC
LIMIT 10;

-- Query 2: Daily sales trend
SELECT 
    date_trunc('day', sale_date) as day,
    SUM(amount) as daily_revenue,
    COUNT(DISTINCT customer_id) as unique_customers
FROM hive.sales_db.sales
WHERE sale_date >= date_add('day', -30, current_date)
GROUP BY date_trunc('day', sale_date)
ORDER BY day;

-- Query 3: Customer segmentation
WITH customer_stats AS (
    SELECT 
        customer_id,
        COUNT(*) as order_count,
        SUM(amount) as total_spent,
        AVG(amount) as avg_order_value
    FROM hive.sales_db.sales
    GROUP BY customer_id
)
SELECT 
    CASE 
        WHEN total_spent > 1000 THEN 'High Value'
        WHEN total_spent > 500 THEN 'Medium Value'
        ELSE 'Low Value'
    END as customer_segment,
    COUNT(*) as customer_count,
    AVG(total_spent) as avg_lifetime_value
FROM customer_stats
GROUP BY CASE 
    WHEN total_spent > 1000 THEN 'High Value'
    WHEN total_spent > 500 THEN 'Medium Value'
    ELSE 'Low Value'
END;
```

**Run Presto queries**:
```bash
# SSH into master node and run
presto-cli --catalog hive --schema sales_db -f /tmp/presto_queries.sql
```

---

### Task 5: Step Functions Integration
**Objective**: Orchestrate EMR jobs with AWS Step Functions.

**Create Step Functions state machine** (`step-functions/emr-workflow.json`):
```json
{
  "Comment": "EMR ETL Pipeline Workflow",
  "StartAt": "CreateCluster",
  "States": {
    "CreateCluster": {
      "Type": "Task",
      "Resource": "arn:aws:states:::elasticmapreduce:createCluster.sync",
      "Parameters": {
        "Name": "ETL-Cluster-{student_id}",
        "ReleaseLabel": "emr-6.15.0",
        "Applications": [
          {"Name": "Spark"},
          {"Name": "Hive"}
        ],
        "Instances": {
          "InstanceGroups": [
            {
              "Name": "Master",
              "InstanceRole": "MASTER",
              "InstanceType": "m5.xlarge",
              "InstanceCount": 1
            },
            {
              "Name": "Core",
              "InstanceRole": "CORE",
              "InstanceType": "m5.xlarge",
              "InstanceCount": 2
            }
          ],
          "KeepJobFlowAliveWhenNoSteps": true
        },
        "ServiceRole": "EMR_DefaultRole",
        "JobFlowRole": "EMR_EC2_DefaultRole",
        "LogUri": "s3://emr-{student_id}/logs/stepfunctions/"
      },
      "ResultPath": "$.cluster",
      "Next": "RunDataIngestion"
    },
    "RunDataIngestion": {
      "Type": "Task",
      "Resource": "arn:aws:states:::elasticmapreduce:addStep.sync",
      "Parameters": {
        "ClusterId.$": "$.cluster.ClusterId",
        "Step": {
          "Name": "Data Ingestion",
          "ActionOnFailure": "CONTINUE",
          "HadoopJarStep": {
            "Jar": "command-runner.jar",
            "Args": [
              "spark-submit",
              "s3://emr-{student_id}/scripts/ingest_data.py"
            ]
          }
        }
      },
      "ResultPath": "$.ingestionStep",
      "Next": "RunTransformation"
    },
    "RunTransformation": {
      "Type": "Task",
      "Resource": "arn:aws:states:::elasticmapreduce:addStep.sync",
      "Parameters": {
        "ClusterId.$": "$.cluster.ClusterId",
        "Step": {
          "Name": "Data Transformation",
          "ActionOnFailure": "CONTINUE",
          "HadoopJarStep": {
            "Jar": "command-runner.jar",
            "Args": [
              "spark-submit",
              "s3://emr-{student_id}/scripts/transform_data.py"
            ]
          }
        }
      },
      "ResultPath": "$.transformStep",
      "Next": "TerminateCluster"
    },
    "TerminateCluster": {
      "Type": "Task",
      "Resource": "arn:aws:states:::elasticmapreduce:terminateCluster",
      "Parameters": {
        "ClusterId.$": "$.cluster.ClusterId"
      },
      "End": true
    }
  }
}
```

**Create and execute state machine**:
```bash
# Create IAM role for Step Functions
aws iam create-role \
  --role-name StepFunctionsEMRRole-{student_id} \
  --assume-role-policy-document file://step-functions-trust-policy.json

# Attach policy
aws iam attach-role-policy \
  --role-name StepFunctionsEMRRole-{student_id} \
  --policy-arn arn:aws:iam::aws:policy/AWSStepFunctionsFullAccess

# Create state machine
aws stepfunctions create-state-machine \
  --name "EMR-ETL-Pipeline-{student_id}" \
  --definition file://step-functions/emr-workflow.json \
  --role-arn arn:aws:iam::<account-id>:role/StepFunctionsEMRRole-{student_id}

# Start execution
aws stepfunctions start-execution \
  --state-machine-arn <state-machine-arn> \
  --name "execution-$(date +%s)"
```

---

### Task 6: EMR with Glue Data Catalog
**Objective**: Integrate EMR with Glue for centralized metadata.

**Configure cluster with Glue catalog**:
```bash
aws emr create-cluster \
  --name "EMR-Glue-{student_id}" \
  --release-label emr-6.15.0 \
  --applications Name=Spark Name=Hive \
  --instance-type m5.xlarge \
  --instance-count 3 \
  --use-default-roles \
  --configurations '[
    {
      "Classification": "hive-site",
      "Properties": {
        "hive.metastore.client.factory.class": "com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory"
      }
    },
    {
      "Classification": "spark-hive-site",
      "Properties": {
        "hive.metastore.client.factory.class": "com.amazonaws.glue.catalog.metastore.AWSGlueDataCatalogHiveClientFactory"
      }
    }
  ]'
```

**Create Glue table from Spark**:
```python
# scripts/create_glue_table.py
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Create Glue Table") \
    .enableHiveSupport() \
    .getOrCreate()

# Read data
df = spark.read.csv("s3://emr-{student_id}/data/sales.csv", 
                    header=True, inferSchema=True)

# Write as Glue table
df.write \
    .mode("overwrite") \
    .format("parquet") \
    .saveAsTable("glue_catalog.sales_db.transactions")

print("✅ Table created in Glue Data Catalog")

spark.stop()
```

---

### Task 7: Spot Instances for Cost Optimization
**Objective**: Use Spot instances for core and task nodes.

```bash
aws emr create-cluster \
  --name "Spot-Cluster-{student_id}" \
  --release-label emr-6.15.0 \
  --applications Name=Spark \
  --instance-groups '[
    {
      "Name": "Master",
      "InstanceRole": "MASTER",
      "InstanceType": "m5.xlarge",
      "InstanceCount": 1,
      "Market": "ON_DEMAND"
    },
    {
      "Name": "Core",
      "InstanceRole": "CORE",
      "InstanceType": "m5.xlarge",
      "InstanceCount": 2,
      "Market": "SPOT",
      "BidPrice": "0.10"
    },
    {
      "Name": "Task",
      "InstanceRole": "TASK",
      "InstanceType": "m5.xlarge",
      "InstanceCount": 3,
      "Market": "SPOT",
      "BidPrice": "0.10"
    }
  ]' \
  --use-default-roles \
  --log-uri s3://emr-{student_id}/logs/spot/
```

---

### Task 8: EMR Managed Scaling
**Objective**: Enable automatic scaling based on metrics.

```bash
# Create scaling policy
cat > scaling-policy.json << 'EOF'
{
  "ComputeLimits": {
    "UnitType": "Instances",
    "MinimumCapacityUnits": 2,
    "MaximumCapacityUnits": 10,
    "MaximumOnDemandCapacityUnits": 2,
    "MaximumCoreCapacityUnits": 5
  }
}
EOF

# Apply scaling to cluster
aws emr put-managed-scaling-policy \
  --cluster-id <cluster-id> \
  --managed-scaling-policy file://scaling-policy.json
```

---

### Task 9: Custom Bootstrap Actions
**Objective**: Create bootstrap script for custom configuration.

**Bootstrap script** (`scripts/bootstrap.sh`):
```bash
#!/bin/bash
# Custom bootstrap for EMR cluster

# Install additional Python packages
sudo pip3 install pandas pyarrow scikit-learn

# Configure environment variables
echo "export EMR_STUDENT_ID={student_id}" >> /home/hadoop/.bashrc

# Download custom libraries
aws s3 cp s3://emr-{student_id}/libs/custom-lib.jar /usr/lib/spark/jars/

echo "✅ Bootstrap completed"
```

**Upload and use**:
```bash
aws s3 cp scripts/bootstrap.sh s3://emr-{student_id}/scripts/

aws emr create-cluster \
  --name "Custom-Bootstrap-{student_id}" \
  --release-label emr-6.15.0 \
  --applications Name=Spark \
  --instance-type m5.xlarge \
  --instance-count 3 \
  --use-default-roles \
  --bootstrap-actions Path=s3://emr-{student_id}/scripts/bootstrap.sh
```

---

### Task 10: Multi-Step ETL Pipeline
**Objective**: Build complete ETL with multiple processing stages.

**Pipeline script** (`scripts/complete_etl.py`):
```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder.appName("Complete ETL").getOrCreate()

# Stage 1: Ingest raw data
raw_df = spark.read.csv("s3://emr-{student_id}/data/raw/", header=True)
print(f"Stage 1: Ingested {raw_df.count()} records")

# Stage 2: Cleanse data
clean_df = raw_df \
    .filter(col("amount").isNotNull()) \
    .filter(col("amount") > 0) \
    .dropDuplicates(["order_id"])
print(f"Stage 2: Cleaned {clean_df.count()} records")

# Stage 3: Transform
transformed_df = clean_df \
    .withColumn("year", year(col("sale_date"))) \
    .withColumn("month", month(col("sale_date"))) \
    .withColumn("revenue_category", 
                when(col("amount") > 1000, "High")
                .when(col("amount") > 500, "Medium")
                .otherwise("Low"))

# Stage 4: Aggregate
summary_df = transformed_df.groupBy("year", "month", "product_category") \
    .agg(
        sum("amount").alias("total_revenue"),
        avg("amount").alias("avg_revenue"),
        count("*").alias("order_count")
    )

# Stage 5: Write outputs
summary_df.write.mode("overwrite") \
    .partitionBy("year", "month") \
    .parquet("s3://emr-{student_id}/output/etl-summary/")

print("✅ ETL pipeline completed")
spark.stop()
```

---

## Validation Commands

```bash
# Check EMR Serverless applications
aws emr-serverless list-applications

# List clusters
aws emr list-clusters --active

# Check Step Functions
aws stepfunctions list-state-machines

# Verify Glue tables
aws glue get-tables --database-name sales_db

# Run validation
python validate_tasks.py emr_medium
```

---

## Success Criteria

✅ **EMR Serverless**: Application created and job executed  
✅ **Hive**: Tables created and queries run  
✅ **Presto**: Interactive queries executed  
✅ **Step Functions**: Workflow orchestration working  
✅ **Glue Catalog**: Integration configured  
✅ **Spot Instances**: Cluster with spot nodes running  
✅ **Auto-Scaling**: Managed scaling enabled  
✅ **Bootstrap**: Custom bootstrap actions applied  
✅ **ETL Pipeline**: Multi-stage pipeline executed  

---

## Testing Your Work

```bash
python validate_tasks.py emr_medium
```

**Minimum passing score**: 70% (7 out of 10 tasks)

---

## Cost Considerations

**EMR Serverless**: Pay per vCPU-hour and GB-hour (~$0.05/vCPU-hour)  
**Spot Instances**: 70-90% discount vs On-Demand  
**Auto-Scaling**: Scale down when idle  

**Estimated Cost**: $5-15 for assessment (with spot instances)

---

## Additional Resources

- [EMR Serverless](https://docs.aws.amazon.com/emr/latest/EMR-Serverless-UserGuide/)
- [Apache Hive on EMR](https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-hive.html)
- [Presto on EMR](https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-presto.html)
- [Step Functions EMR Integration](https://docs.aws.amazon.com/step-functions/latest/dg/connect-emr.html)

---

**Good luck with your EMR Medium assessment!** 🚀
