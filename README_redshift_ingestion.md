# AWS Redshift Assessment - Data Ingestion & Storage

github-repo: https://github.com/sharedlabs1/s3assessment

## Difficulty Level: 🟡 Medium

## Scenario
You are a Data Engineer at DataCorp responsible for ingesting large volumes of data into Amazon Redshift Serverless for analytics. Implement efficient data loading patterns, handle multiple file formats, integrate with data lakes, and optimize ingestion workflows.

## Prerequisites
- Access to the shared AWS training account
- Understanding of data warehousing concepts
- Familiarity with SQL and ETL processes
- Python 3.8+ and boto3
- GitHub CLI (`gh`)
- Basic knowledge of S3 and file formats

## Setup

1. **Download the assessment files**:
   - `validate_tasks.py`
   - `requirements.txt`
   - `README_redshift_ingestion.md`

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Tasks to Complete

### Task 1: Create Redshift Serverless Workgroup
Set up Redshift Serverless for cost-effective analytics:

**Namespace Configuration:**
- **Namespace Name**: `analytics-namespace-${your-student-id}`
- **Database Name**: `analyticsdb`
- **Admin Username**: `admin`
- **Admin Password**: Create secure password (min 8 chars, mixed case, numbers)

**Workgroup Configuration:**
- **Workgroup Name**: `analytics-workgroup-${your-student-id}`
- **Base Capacity**: 8 RPUs (Redshift Processing Units)
- **Subnet**: Select 3 private subnets in different AZs
- **Security Group**: Create `redshift-serverless-sg-${your-student-id}`
  - Allow inbound on port 5439 from your IP/VPC
- **Publicly Accessible**: No (keep in VPC for security)

**Using AWS Console:**
1. Go to Amazon Redshift → Redshift Serverless
2. Click "Create workgroup"
3. Configure namespace and workgroup as above
4. Wait for workgroup to become "Available"

**Tags**: `Environment=Production`, `Application=Analytics`, `StudentID=${your-student-id}`

### Task 2: Create S3 Data Lake Structure
Set up S3 buckets for data ingestion:

**Bucket Name**: `redshift-data-lake-${your-student-id}`

**Folder Structure:**
```
redshift-data-lake-STUDENTID/
├── raw/
│   ├── customers/
│   ├── orders/
│   ├── products/
│   └── transactions/
├── staging/
│   ├── csv/
│   ├── parquet/
│   └── json/
├── processed/
│   └── aggregates/
└── logs/
    └── load-errors/
```

**Create bucket:**
```bash
aws s3 mb s3://redshift-data-lake-STUDENTID

# Create folders
aws s3api put-object --bucket redshift-data-lake-STUDENTID --key raw/customers/
aws s3api put-object --bucket redshift-data-lake-STUDENTID --key raw/orders/
aws s3api put-object --bucket redshift-data-lake-STUDENTID --key raw/products/
aws s3api put-object --bucket redshift-data-lake-STUDENTID --key raw/transactions/
aws s3api put-object --bucket redshift-data-lake-STUDENTID --key staging/csv/
aws s3api put-object --bucket redshift-data-lake-STUDENTID --key staging/parquet/
aws s3api put-object --bucket redshift-data-lake-STUDENTID --key staging/json/
aws s3api put-object --bucket redshift-data-lake-STUDENTID --key processed/aggregates/
aws s3api put-object --bucket redshift-data-lake-STUDENTID --key logs/load-errors/
```

### Task 3: Create IAM Role for Redshift
Create IAM role for Redshift to access S3:

**Role Name**: `RedshiftS3AccessRole-${your-student-id}`
**Trust Policy**: Allow Redshift service to assume role

**Permissions:**
- `AmazonS3ReadOnlyAccess` (or custom policy with specific bucket access)
- `AWSGlueConsoleFullAccess` (for Glue Data Catalog integration)

**Custom S3 Policy** (recommended):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:GetObjectVersion",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::redshift-data-lake-STUDENTID",
        "arn:aws:s3:::redshift-data-lake-STUDENTID/*"
      ]
    }
  ]
}
```

**Attach role to Redshift Serverless namespace:**
1. Go to Redshift Serverless → Namespaces
2. Select your namespace
3. Security and encryption → Manage IAM roles
4. Add the IAM role

### Task 4: Create Tables in Redshift
Connect to Redshift and create tables:

**Connection String:**
```
Host: your-workgroup.account.region.redshift-serverless.amazonaws.com
Port: 5439
Database: analyticsdb
User: admin
```

**Create Customers Table:**
```sql
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    address VARCHAR(200),
    city VARCHAR(50),
    state VARCHAR(2),
    zip_code VARCHAR(10),
    country VARCHAR(50),
    registration_date DATE,
    customer_segment VARCHAR(20)
);
```

**Create Orders Table:**
```sql
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date TIMESTAMP,
    ship_date TIMESTAMP,
    ship_mode VARCHAR(20),
    total_amount DECIMAL(10,2),
    discount DECIMAL(10,2),
    tax DECIMAL(10,2),
    profit DECIMAL(10,2),
    order_status VARCHAR(20)
);
```

**Create Products Table:**
```sql
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(200),
    category VARCHAR(50),
    sub_category VARCHAR(50),
    brand VARCHAR(50),
    unit_price DECIMAL(10,2),
    cost DECIMAL(10,2),
    stock_quantity INTEGER,
    supplier_id INTEGER
);
```

**Create Transactions Table (partitioned by date):**
```sql
CREATE TABLE transactions (
    transaction_id BIGINT PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    discount_percent DECIMAL(5,2),
    transaction_date DATE,
    payment_method VARCHAR(20)
);
```

### Task 5: Load CSV Data Using COPY Command
Load data from S3 CSV files:

**Upload sample CSV data to S3:**
```bash
# Sample customers.csv
cat > customers.csv << 'EOF'
customer_id,first_name,last_name,email,phone,address,city,state,zip_code,country,registration_date,customer_segment
1,John,Doe,john.doe@email.com,555-0101,123 Main St,New York,NY,10001,USA,2024-01-15,Premium
2,Jane,Smith,jane.smith@email.com,555-0102,456 Oak Ave,Los Angeles,CA,90001,USA,2024-02-20,Standard
3,Bob,Johnson,bob.j@email.com,555-0103,789 Pine Rd,Chicago,IL,60601,USA,2024-03-10,Premium
EOF

aws s3 cp customers.csv s3://redshift-data-lake-STUDENTID/raw/customers/
```

**COPY Command to Load CSV:**
```sql
COPY customers
FROM 's3://redshift-data-lake-STUDENTID/raw/customers/customers.csv'
IAM_ROLE 'arn:aws:iam::ACCOUNT:role/RedshiftS3AccessRole-STUDENTID'
FORMAT AS CSV
IGNOREHEADER 1
DELIMITER ','
REGION 'us-east-1'
DATEFORMAT 'YYYY-MM-DD';
```

**Verify data loaded:**
```sql
SELECT COUNT(*) FROM customers;
SELECT * FROM customers LIMIT 10;
```

### Task 6: Load Parquet Data
Load optimized Parquet files for better performance:

**Generate Parquet file** (Python script):
```python
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import boto3

# Sample products data
products_data = {
    'product_id': [1, 2, 3, 4, 5],
    'product_name': ['Laptop Pro', 'Wireless Mouse', 'USB Keyboard', '27" Monitor', 'Webcam HD'],
    'category': ['Electronics', 'Electronics', 'Electronics', 'Electronics', 'Electronics'],
    'sub_category': ['Computers', 'Accessories', 'Accessories', 'Displays', 'Accessories'],
    'brand': ['TechCorp', 'LogiTech', 'KeyMaster', 'ViewSonic', 'CamPro'],
    'unit_price': [1299.99, 29.99, 49.99, 349.99, 79.99],
    'cost': [800.00, 15.00, 25.00, 200.00, 40.00],
    'stock_quantity': [50, 200, 150, 75, 100],
    'supplier_id': [101, 102, 102, 103, 104]
}

df = pd.DataFrame(products_data)

# Write to Parquet
df.to_parquet('products.parquet', engine='pyarrow', compression='snappy')

# Upload to S3
s3 = boto3.client('s3')
s3.upload_file('products.parquet', 'redshift-data-lake-STUDENTID', 'staging/parquet/products.parquet')
```

**COPY Command for Parquet:**
```sql
COPY products
FROM 's3://redshift-data-lake-STUDENTID/staging/parquet/products.parquet'
IAM_ROLE 'arn:aws:iam::ACCOUNT:role/RedshiftS3AccessRole-STUDENTID'
FORMAT AS PARQUET;
```

**Verify:**
```sql
SELECT COUNT(*) FROM products;
SELECT * FROM products;
```

### Task 7: Load JSON Data
Handle semi-structured JSON data:

**Sample JSON file** (orders.json):
```json
{"order_id": 1001, "customer_id": 1, "order_date": "2024-11-01 10:30:00", "ship_date": "2024-11-03 14:20:00", "ship_mode": "Standard", "total_amount": 1500.00, "discount": 50.00, "tax": 120.00, "profit": 300.00, "order_status": "Delivered"}
{"order_id": 1002, "customer_id": 2, "order_date": "2024-11-02 15:45:00", "ship_date": "2024-11-04 09:10:00", "ship_mode": "Express", "total_amount": 89.97, "discount": 0.00, "tax": 7.20, "profit": 25.00, "order_status": "Delivered"}
{"order_id": 1003, "customer_id": 1, "order_date": "2024-11-05 08:15:00", "ship_date": null, "ship_mode": "Standard", "total_amount": 450.00, "discount": 22.50, "tax": 36.00, "profit": 100.00, "order_status": "Processing"}
```

**Upload to S3:**
```bash
aws s3 cp orders.json s3://redshift-data-lake-STUDENTID/staging/json/
```

**COPY Command for JSON:**
```sql
COPY orders
FROM 's3://redshift-data-lake-STUDENTID/staging/json/orders.json'
IAM_ROLE 'arn:aws:iam::ACCOUNT:role/RedshiftS3AccessRole-STUDENTID'
FORMAT AS JSON 'auto'
TIMEFORMAT 'YYYY-MM-DD HH:MI:SS';
```

### Task 8: Handle Load Errors with Error Logging
Configure error handling for data loads:

**COPY with Error Logging:**
```sql
COPY orders
FROM 's3://redshift-data-lake-STUDENTID/staging/json/orders.json'
IAM_ROLE 'arn:aws:iam::ACCOUNT:role/RedshiftS3AccessRole-STUDENTID'
FORMAT AS JSON 'auto'
MAXERROR 100
TIMEFORMAT 'YYYY-MM-DD HH:MI:SS';
```

**Check for load errors:**
```sql
-- View load errors
SELECT * FROM stl_load_errors
ORDER BY starttime DESC
LIMIT 10;

-- View detailed error info
SELECT 
    query,
    filename,
    line_number,
    colname,
    type,
    raw_line,
    err_reason
FROM stl_load_errors
WHERE query = pg_last_copy_id()
ORDER BY line_number;
```

### Task 9: Implement Incremental Data Loading
Load only new/changed data:

**Create staging table:**
```sql
CREATE TABLE orders_staging (
    order_id INTEGER,
    customer_id INTEGER,
    order_date TIMESTAMP,
    ship_date TIMESTAMP,
    ship_mode VARCHAR(20),
    total_amount DECIMAL(10,2),
    discount DECIMAL(10,2),
    tax DECIMAL(10,2),
    profit DECIMAL(10,2),
    order_status VARCHAR(20)
);
```

**Load new data to staging:**
```sql
COPY orders_staging
FROM 's3://redshift-data-lake-STUDENTID/raw/orders/2024-11-19/'
IAM_ROLE 'arn:aws:iam::ACCOUNT:role/RedshiftS3AccessRole-STUDENTID'
FORMAT AS CSV
IGNOREHEADER 1;
```

**Merge into main table (UPSERT pattern):**
```sql
-- Begin transaction
BEGIN TRANSACTION;

-- Delete existing records that will be updated
DELETE FROM orders
WHERE order_id IN (SELECT order_id FROM orders_staging);

-- Insert all records from staging
INSERT INTO orders
SELECT * FROM orders_staging;

-- Commit
END TRANSACTION;

-- Clear staging
TRUNCATE orders_staging;
```

### Task 10: Optimize COPY Performance with Multiple Files
Use manifest file for parallel loading:

**Create manifest file** (load_manifest.json):
```json
{
  "entries": [
    {"url": "s3://redshift-data-lake-STUDENTID/raw/transactions/part-001.csv", "mandatory": true},
    {"url": "s3://redshift-data-lake-STUDENTID/raw/transactions/part-002.csv", "mandatory": true},
    {"url": "s3://redshift-data-lake-STUDENTID/raw/transactions/part-003.csv", "mandatory": true}
  ]
}
```

**Upload manifest:**
```bash
aws s3 cp load_manifest.json s3://redshift-data-lake-STUDENTID/staging/
```

**COPY using manifest:**
```sql
COPY transactions
FROM 's3://redshift-data-lake-STUDENTID/staging/load_manifest.json'
IAM_ROLE 'arn:aws:iam::ACCOUNT:role/RedshiftS3AccessRole-STUDENTID'
FORMAT AS CSV
MANIFEST
IGNOREHEADER 1
COMPUPDATE ON;
```

### Task 11: Integrate with AWS Glue Data Catalog
Use Glue as external metadata store:

**Create Glue Database:**
```bash
aws glue create-database \
    --database-input '{"Name":"redshift_external_db_STUDENTID","Description":"External tables for Redshift Spectrum"}'
```

**Create external schema in Redshift:**
```sql
CREATE EXTERNAL SCHEMA spectrum_schema
FROM DATA CATALOG
DATABASE 'redshift_external_db_STUDENTID'
IAM_ROLE 'arn:aws:iam::ACCOUNT:role/RedshiftS3AccessRole-STUDENTID'
CREATE EXTERNAL DATABASE IF NOT EXISTS;
```

**Create external table (Redshift Spectrum):**
```sql
CREATE EXTERNAL TABLE spectrum_schema.external_logs (
    log_timestamp TIMESTAMP,
    log_level VARCHAR(10),
    message VARCHAR(500),
    user_id INTEGER
)
STORED AS PARQUET
LOCATION 's3://redshift-data-lake-STUDENTID/raw/logs/';
```

**Query external data:**
```sql
SELECT log_level, COUNT(*) as count
FROM spectrum_schema.external_logs
WHERE log_timestamp >= CURRENT_DATE - 7
GROUP BY log_level;
```

### Task 12: Monitor Data Loads
Track load performance and issues:

**Query system tables for load history:**
```sql
-- View recent COPY commands
SELECT 
    query,
    filename,
    curtime as load_time,
    status,
    rows_loaded,
    bytes_loaded,
    DATEDIFF(seconds, starttime, endtime) as duration_seconds
FROM stl_load_commits
WHERE filename LIKE '%redshift-data-lake%'
ORDER BY curtime DESC
LIMIT 20;

-- View load performance metrics
SELECT 
    TRIM(filename) as file,
    lines_scanned,
    lines_loaded,
    bytes_loaded / 1024 / 1024 as mb_loaded,
    DATEDIFF(ms, starttime, endtime) / 1000.0 as seconds
FROM stl_load_commits
ORDER BY starttime DESC
LIMIT 10;
```

## Validation

Run the validation script:

```bash
python validate_tasks.py redshift_ingestion
```

The script will verify:
- Redshift Serverless workgroup exists and is available
- Namespace `analytics-namespace-${your-student-id}` configured
- S3 bucket `redshift-data-lake-${your-student-id}` exists with correct structure
- IAM role for S3 access exists
- Required tables (customers, orders, products, transactions) exist
- Tables contain data (COPY commands executed)
- Glue Data Catalog database exists
- External schema configured in Redshift
- Tags properly set

## Cleanup (After Assessment)
1. Drop all Redshift tables
2. Delete external schemas
3. Delete Redshift Serverless workgroup and namespace
4. Delete S3 bucket and all data
5. Delete IAM role
6. Delete Glue database

## Tips
- **Redshift Serverless** charges only for actual usage (no idle costs)
- Use **Parquet** for columnar storage and better compression
- **COPY** is 10x faster than INSERT for bulk loads
- Split large files into 1-16 MB chunks for parallel loading
- Use **COMPUPDATE ON** to analyze and set optimal compression
- **Manifest files** ensure all files are loaded exactly once
- Monitor **stl_load_errors** for troubleshooting
- **Redshift Spectrum** queries S3 data without loading
- Use **VACUUM** and **ANALYZE** after large loads
- Enable **automatic table optimization** for maintenance

## Common Issues
- **Access Denied**: Check IAM role is attached to namespace
- **S3 bucket not found**: Verify bucket name and region
- **Load timeout**: Break large files into smaller chunks
- **Encoding errors**: Specify correct ENCODING in COPY
- **NULL values**: Use EMPTYASNULL or BLANKSASNULL options
- **Date format errors**: Use DATEFORMAT and TIMEFORMAT correctly
- **Duplicate keys**: Check for duplicates before loading

## Learning Resources
- Redshift Serverless architecture and pricing
- COPY command options and optimization
- File formats (CSV, Parquet, JSON, Avro, ORC)
- IAM roles for Redshift
- Redshift Spectrum for querying S3
- Glue Data Catalog integration
- Error handling and monitoring
- Incremental loading patterns (UPSERT)
- Manifest files for atomic loads
- Compression and encoding strategies
