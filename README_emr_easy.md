# AWS EMR Assessment - Easy

## Overview
Learn Amazon EMR (Elastic MapReduce) basics by creating clusters, running Apache Spark jobs, and processing big data workloads.

**Difficulty**: Easy  
**Prerequisites**: Basic AWS knowledge, S3 basics  
**Estimated Time**: 2-3 hours  

## Learning Objectives
- Create and configure EMR clusters
- Run Spark jobs on EMR
- Process data with PySpark
- Monitor EMR cluster health
- Work with EMR file system (EMRFS)
- Understand cluster scaling

## Tasks

### Task 1: EMR S3 Bucket Setup
Create S3 bucket for EMR scripts, data, and logs:
```bash
aws s3 mb s3://emr-{student_id}
aws s3api put-object --bucket emr-{student_id} --key scripts/
aws s3api put-object --bucket emr-{student_id} --key data/
aws s3api put-object --bucket emr-{student_id} --key logs/
aws s3api put-object --bucket emr-{student_id} --key output/
```

### Task 2: Sample Dataset Upload
Upload sample dataset for processing:
```bash
# Create sample CSV data
cat > sample-data.csv << 'EOF'
date,product,quantity,price
2024-01-01,Widget,10,25.50
2024-01-01,Gadget,5,50.00
2024-01-02,Widget,15,25.50
2024-01-02,Gadget,8,50.00
EOF

aws s3 cp sample-data.csv s3://emr-{student_id}/data/
```

### Task 3: IAM Role for EMR
Create IAM roles for EMR service and EC2 instances:
```bash
# EMR service role
aws iam create-role \
  --role-name EMRServiceRole-{student_id} \
  --assume-role-policy-document file://emr-trust-policy.json

aws iam attach-role-policy \
  --role-name EMRServiceRole-{student_id} \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonEMRServicePolicy_v2

# EC2 instance profile
aws iam create-role \
  --role-name EMRInstanceRole-{student_id} \
  --assume-role-policy-document file://ec2-trust-policy.json

aws iam attach-role-policy \
  --role-name EMRInstanceRole-{student_id} \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonElasticMapReduceforEC2Role
```

### Task 4: Create EMR Cluster
Launch an EMR cluster with Spark:
```bash
aws emr create-cluster \
  --name "EMR-Cluster-{student_id}" \
  --release-label emr-6.15.0 \
  --applications Name=Spark Name=Hadoop \
  --ec2-attributes KeyName=my-key-pair,InstanceProfile=EMRInstanceRole-{student_id} \
  --instance-type m5.xlarge \
  --instance-count 3 \
  --use-default-roles \
  --log-uri s3://emr-{student_id}/logs/ \
  --region us-east-1
```

### Task 5: PySpark Word Count Job
Create and run a simple PySpark word count script:
```python
# scripts/wordcount.py
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("WordCount").getOrCreate()

# Read text file
lines = spark.read.text("s3://emr-{student_id}/data/sample.txt")

# Word count
from pyspark.sql.functions import explode, split
words = lines.select(explode(split(lines.value, " ")).alias("word"))
word_counts = words.groupBy("word").count().orderBy("count", ascending=False)

# Save results
word_counts.write.mode("overwrite").csv("s3://emr-{student_id}/output/wordcount/")

spark.stop()
```

Upload and run:
```bash
aws s3 cp scripts/wordcount.py s3://emr-{student_id}/scripts/

aws emr add-steps \
  --cluster-id <cluster-id> \
  --steps Type=Spark,Name="Word Count",ActionOnFailure=CONTINUE,Args=[s3://emr-{student_id}/scripts/wordcount.py]
```

### Task 6: Data Processing with PySpark
Process the sample CSV data:
```python
# scripts/process_sales.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import sum, avg, count

spark = SparkSession.builder.appName("SalesAnalysis").getOrCreate()

# Read CSV
df = spark.read.csv("s3://emr-{student_id}/data/sample-data.csv", header=True, inferSchema=True)

# Analysis
daily_sales = df.groupBy("date").agg(
    sum("quantity").alias("total_quantity"),
    sum("price").alias("total_revenue")
)

# Save
daily_sales.write.mode("overwrite").parquet("s3://emr-{student_id}/output/daily-sales/")

spark.stop()
```

### Task 7: Monitor Cluster
Check cluster status and metrics:
```bash
# Get cluster status
aws emr describe-cluster --cluster-id <cluster-id>

# List running steps
aws emr list-steps --cluster-id <cluster-id>

# View CloudWatch metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ElasticMapReduce \
  --metric-name IsIdle \
  --dimensions Name=JobFlowId,Value=<cluster-id> \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T23:59:59Z \
  --period 3600 \
  --statistics Average
```

### Task 8: EMR Notebook (Optional)
Create EMR notebook for interactive development:
```bash
aws emr create-studio \
  --name "EMR-Studio-{student_id}" \
  --auth-mode IAM \
  --vpc-id <vpc-id> \
  --subnet-ids <subnet-id> \
  --service-role <studio-role-arn> \
  --workspace-security-group-id <sg-id>
```

### Task 9: Cluster Scaling
Test manual and automatic scaling:
```bash
# Manual scaling
aws emr modify-instance-groups \
  --cluster-id <cluster-id> \
  --instance-groups InstanceGroupId=<core-group-id>,InstanceCount=5
```

### Task 10: Terminate Cluster
Clean up resources:
```bash
aws emr terminate-clusters --cluster-ids <cluster-id>
```

## Validation
```bash
python validate_tasks.py emr_easy
```

**Minimum passing score**: 70%

---

**Good luck with your EMR Easy assessment!** 🚀
