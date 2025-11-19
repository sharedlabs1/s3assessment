# AWS Redshift Assessment - Database Design & Optimization

github-repo: https://github.com/sharedlabs1/s3assessment

## Difficulty Level: 🔴 Hard

## Scenario
You are a Data Architect at AnalyticsCorp responsible for designing and optimizing a high-performance Redshift data warehouse. Implement distribution strategies, sort keys, compression encoding, table maintenance routines, and workload management to achieve maximum query performance and cost efficiency.

## Prerequisites
- Completed Redshift Data Ingestion assessment
- Deep understanding of columnar databases
- Experience with query optimization
- Knowledge of data warehouse design patterns
- Python 3.8+ and boto3
- GitHub CLI (`gh`)
- SQL proficiency

## Setup

1. **Download the assessment files**:
   - `validate_tasks.py`
   - `requirements.txt`
   - `README_redshift_design.md`

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Prerequisites from Previous Assessment
- Redshift Serverless workgroup: `analytics-workgroup-${your-student-id}`
- Database: `analyticsdb`
- S3 bucket: `redshift-data-lake-${your-student-id}`

## Tasks to Complete

### Task 1: Design Fact Table with Distribution Key
Create optimized fact table with proper distribution:

**sales_fact table** (large fact table):
```sql
CREATE TABLE sales_fact (
    sale_id BIGINT NOT NULL,
    order_date DATE NOT NULL SORTKEY,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    store_id INTEGER,
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    discount_amount DECIMAL(10,2),
    tax_amount DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    payment_method VARCHAR(20),
    region VARCHAR(50)
)
DISTKEY(customer_id)  -- Distribute by most common join key
SORTKEY(order_date);  -- Sort by date for time-based queries
```

**Why DISTKEY(customer_id)?**
- Most queries join on customer_id
- Reduces data movement during joins
- Co-locates related data on same slice

### Task 2: Create Dimension Tables with ALL Distribution
Small dimension tables should use ALL distribution:

**dim_customers** (dimension table):
```sql
CREATE TABLE dim_customers (
    customer_id INTEGER NOT NULL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    customer_segment VARCHAR(20),
    lifetime_value DECIMAL(12,2),
    registration_date DATE
)
DISTSTYLE ALL;  -- Replicate to all nodes for fast joins
```

**dim_products** (dimension table):
```sql
CREATE TABLE dim_products (
    product_id INTEGER NOT NULL PRIMARY KEY,
    product_name VARCHAR(200),
    category VARCHAR(50),
    sub_category VARCHAR(50),
    brand VARCHAR(50),
    unit_cost DECIMAL(10,2),
    unit_price DECIMAL(10,2)
)
DISTSTYLE ALL;
```

**dim_stores** (dimension table):
```sql
CREATE TABLE dim_stores (
    store_id INTEGER NOT NULL PRIMARY KEY,
    store_name VARCHAR(100),
    store_type VARCHAR(30),
    city VARCHAR(50),
    state VARCHAR(2),
    region VARCHAR(50),
    square_footage INTEGER,
    opening_date DATE
)
DISTSTYLE ALL;
```

**Benefits of DISTSTYLE ALL for dimensions:**
- No network transfer during joins
- Fast query performance
- Suitable for tables < 1 million rows

### Task 3: Implement Compound Sort Keys
Use compound sort keys for multi-column filtering:

**customer_orders table**:
```sql
CREATE TABLE customer_orders (
    order_id BIGINT NOT NULL,
    customer_id INTEGER NOT NULL,
    order_date DATE NOT NULL,
    ship_date DATE,
    order_status VARCHAR(20),
    total_amount DECIMAL(10,2),
    region VARCHAR(50)
)
DISTKEY(customer_id)
COMPOUND SORTKEY(customer_id, order_date);  -- Compound for range queries
```

**When to use COMPOUND SORTKEY:**
- Queries filter on first column in sort key
- Example: `WHERE customer_id = 123 AND order_date >= '2024-01-01'`
- Provides best performance for prefix matching

### Task 4: Implement Interleaved Sort Keys
Use interleaved sort keys for equal-weight columns:

**event_logs table**:
```sql
CREATE TABLE event_logs (
    event_id BIGINT NOT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    user_id INTEGER,
    event_type VARCHAR(50),
    page_url VARCHAR(500),
    session_id VARCHAR(100),
    ip_address VARCHAR(15)
)
DISTKEY(user_id)
INTERLEAVED SORTKEY(event_timestamp, user_id, event_type);  -- Equal weight on all three
```

**When to use INTERLEAVED SORTKEY:**
- Queries filter on different combinations
- Example 1: `WHERE event_timestamp >= ...`
- Example 2: `WHERE user_id = ...`
- Example 3: `WHERE event_type = ...`
- More flexible but slower VACUUM

### Task 5: Optimize Compression Encoding
Analyze and apply optimal compression:

**Check current compression:**
```sql
-- Analyze table for optimal compression
ANALYZE COMPRESSION sales_fact;
```

**Create table with optimal encoding:**
```sql
CREATE TABLE sales_fact_optimized (
    sale_id BIGINT ENCODE az64,
    order_date DATE ENCODE az64,
    customer_id INTEGER ENCODE az64,
    product_id INTEGER ENCODE az64,
    store_id INTEGER ENCODE az64,
    quantity INTEGER ENCODE az64,
    unit_price DECIMAL(10,2) ENCODE az64,
    discount_amount DECIMAL(10,2) ENCODE az64,
    tax_amount DECIMAL(10,2) ENCODE az64,
    total_amount DECIMAL(10,2) ENCODE az64,
    payment_method VARCHAR(20) ENCODE lzo,
    region VARCHAR(50) ENCODE lzo
)
DISTKEY(customer_id)
SORTKEY(order_date);
```

**Compression Types:**
- **AZ64**: Best for numeric columns (new default)
- **LZO**: Good for text columns
- **ZSTD**: Better compression ratio, slower
- **RAW**: No compression (for pre-compressed data)

**Measure compression benefits:**
```sql
-- Check table size and compression
SELECT 
    "table",
    size AS size_mb,
    tbl_rows,
    (size / NULLIF(tbl_rows, 0))::DECIMAL(10,2) AS bytes_per_row
FROM SVV_TABLE_INFO
WHERE "table" IN ('sales_fact', 'sales_fact_optimized')
ORDER BY size DESC;
```

### Task 6: Implement Table Partitioning Strategy
Use date-based partitioning for large tables:

**Create partitioned tables by month:**
```sql
-- Partition 1: January 2024
CREATE TABLE sales_202401 (
    sale_id BIGINT NOT NULL,
    order_date DATE NOT NULL CHECK (order_date >= '2024-01-01' AND order_date < '2024-02-01'),
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    total_amount DECIMAL(10,2)
)
DISTKEY(customer_id)
SORTKEY(order_date);

-- Partition 2: February 2024
CREATE TABLE sales_202402 (
    sale_id BIGINT NOT NULL,
    order_date DATE NOT NULL CHECK (order_date >= '2024-02-01' AND order_date < '2024-03-01'),
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    total_amount DECIMAL(10,2)
)
DISTKEY(customer_id)
SORTKEY(order_date);

-- Create view for seamless querying
CREATE VIEW sales_all AS
SELECT * FROM sales_202401
UNION ALL
SELECT * FROM sales_202402
UNION ALL
SELECT * FROM sales_202403;
```

**Benefits:**
- Drop old partitions for data retention
- Query only relevant partitions
- Faster VACUUM and ANALYZE

### Task 7: Implement VACUUM Strategy
Regular maintenance to reclaim space and sort rows:

**Types of VACUUM:**

```sql
-- Full VACUUM (sorts and reclaims space)
VACUUM sales_fact;

-- VACUUM DELETE ONLY (reclaims space from deleted rows)
VACUUM DELETE ONLY sales_fact;

-- VACUUM SORT ONLY (re-sorts rows)
VACUUM SORT ONLY sales_fact;

-- VACUUM REINDEX (recreates indexes, used after many deletes)
VACUUM REINDEX sales_fact;
```

**Create VACUUM automation** (Lambda function):
```python
import boto3
import json

def lambda_handler(event, context):
    """Automate VACUUM on large tables"""
    
    redshift_data = boto3.client('redshift-data')
    
    workgroup_name = 'analytics-workgroup-STUDENTID'
    database = 'analyticsdb'
    
    # Tables to vacuum
    tables = ['sales_fact', 'customer_orders', 'event_logs']
    
    for table in tables:
        try:
            # Check if VACUUM is needed
            check_sql = f"""
            SELECT 
                COUNT(*) as unsorted_rows
            FROM svv_table_info
            WHERE "table" = '{table}'
            AND unsorted > 5;
            """
            
            response = redshift_data.execute_statement(
                WorkgroupName=workgroup_name,
                Database=database,
                Sql=check_sql
            )
            
            query_id = response['Id']
            
            # If unsorted rows > 5%, run VACUUM
            vacuum_sql = f"VACUUM {table};"
            
            vacuum_response = redshift_data.execute_statement(
                WorkgroupName=workgroup_name,
                Database=database,
                Sql=vacuum_sql
            )
            
            print(f"VACUUM started for {table}: {vacuum_response['Id']}")
            
        except Exception as e:
            print(f"Error vacuuming {table}: {e}")
    
    return {'statusCode': 200}
```

**Schedule with EventBridge**: Daily at 2 AM

### Task 8: Implement ANALYZE Strategy
Update table statistics for optimal query planning:

```sql
-- Analyze specific table
ANALYZE sales_fact;

-- Analyze all tables in schema
ANALYZE;

-- Check table statistics age
SELECT 
    "table",
    stats_off,
    CASE 
        WHEN stats_off > 10 THEN 'Analyze needed'
        ELSE 'OK'
    END as recommendation
FROM SVV_TABLE_INFO
WHERE schema = 'public'
ORDER BY stats_off DESC;
```

**Automated ANALYZE:**
```python
def analyze_tables(workgroup_name, database):
    """Run ANALYZE on tables with stale statistics"""
    
    redshift_data = boto3.client('redshift-data')
    
    # Find tables needing ANALYZE (stats_off > 10%)
    check_sql = """
    SELECT "table"
    FROM SVV_TABLE_INFO
    WHERE schema = 'public'
    AND stats_off > 10
    ORDER BY tbl_rows DESC;
    """
    
    response = redshift_data.execute_statement(
        WorkgroupName=workgroup_name,
        Database=database,
        Sql=check_sql
    )
    
    # Get results and analyze each table
    # (Implementation details omitted for brevity)
```

### Task 9: Configure Workload Management (WLM)
Create query queues for different workload types:

**Create parameter group** for WLM:
```json
{
  "wlm_json_configuration": [
    {
      "name": "ETL Queue",
      "query_concurrency": 5,
      "memory_percent_to_use": 30,
      "query_group": "etl",
      "max_execution_time": 7200000,
      "user_group": ["etl_users"]
    },
    {
      "name": "Dashboard Queue",
      "query_concurrency": 10,
      "memory_percent_to_use": 40,
      "query_group": "dashboard",
      "max_execution_time": 300000,
      "user_group": ["dashboard_users"]
    },
    {
      "name": "Ad-hoc Queue",
      "query_concurrency": 3,
      "memory_percent_to_use": 20,
      "query_group": "adhoc",
      "max_execution_time": 600000,
      "user_group": ["analysts"]
    },
    {
      "name": "Default Queue",
      "query_concurrency": 2,
      "memory_percent_to_use": 10
    }
  ]
}
```

**Use query groups in queries:**
```sql
-- Set query group for session
SET query_group TO 'etl';

-- Run ETL queries
INSERT INTO sales_fact SELECT * FROM staging_sales;

-- Reset to default
RESET query_group;
```

### Task 10: Implement Short Query Acceleration (SQA)
Enable SQA for fast dashboard queries:

**Configure SQA in workgroup:**
- Max execution time: 10 seconds
- Priority: HIGH for short queries

**Test SQA effectiveness:**
```sql
-- Check SQA usage
SELECT 
    query,
    service_class,
    queue_time,
    exec_time,
    CASE 
        WHEN service_class = 14 THEN 'Short Query'
        ELSE 'Normal Queue'
    END as queue_type
FROM stl_wlm_query
WHERE userid > 1
ORDER BY starttime DESC
LIMIT 20;
```

### Task 11: Optimize Joins with Co-location
Ensure fact and dimension tables are properly distributed:

**Check data distribution:**
```sql
-- Check distribution skew
SELECT 
    slice,
    COUNT(*) as rows_on_slice
FROM 
    (SELECT sale_id, SLICE FROM sales_fact)
GROUP BY slice
ORDER BY slice;

-- Ideal: Even distribution across all slices
```

**Fix distribution skew:**
```sql
-- If skewed, recreate table with better DISTKEY
CREATE TABLE sales_fact_new (
    -- same structure
)
DISTKEY(customer_id);  -- or use DISTSTYLE EVEN for even distribution

-- Copy data
INSERT INTO sales_fact_new SELECT * FROM sales_fact;

-- Swap tables
DROP TABLE sales_fact;
ALTER TABLE sales_fact_new RENAME TO sales_fact;
```

### Task 12: Implement Result Set Caching
Leverage result caching for repeated queries:

**Check query result cache:**
```sql
-- View cached results
SELECT 
    userid,
    query,
    starttime,
    elapsed / 1000000.0 as seconds,
    CASE 
        WHEN elapsed < 1000 THEN 'Likely from cache'
        ELSE 'Executed'
    END as cache_status
FROM stl_query
WHERE userid > 1
ORDER BY starttime DESC
LIMIT 20;
```

**Warm up cache for dashboard queries:**
```sql
-- Run common dashboard queries during off-peak hours
-- Results will be cached for 24 hours

SELECT region, SUM(total_amount) as revenue
FROM sales_fact
WHERE order_date >= CURRENT_DATE - 7
GROUP BY region;

SELECT category, COUNT(*) as orders
FROM sales_fact s
JOIN dim_products p ON s.product_id = p.product_id
WHERE s.order_date >= CURRENT_DATE - 30
GROUP BY category;
```

### Task 13: Monitor Table Design Metrics
Track table design effectiveness:

**Create monitoring view:**
```sql
CREATE VIEW v_table_health AS
SELECT 
    "table",
    size AS size_mb,
    tbl_rows,
    diststyle,
    sortkey1,
    unsorted AS unsorted_pct,
    stats_off,
    skew_rows,
    CASE 
        WHEN unsorted > 20 THEN 'VACUUM needed'
        WHEN stats_off > 10 THEN 'ANALYZE needed'
        WHEN skew_rows > 2.0 THEN 'Distribution skew'
        ELSE 'Healthy'
    END as health_status,
    CASE 
        WHEN size > 1000 AND diststyle = 'ALL' THEN 'Consider KEY distribution'
        WHEN size < 100 AND diststyle = 'KEY' THEN 'Consider ALL distribution'
        ELSE 'OK'
    END as design_recommendation
FROM SVV_TABLE_INFO
WHERE schema = 'public'
ORDER BY size DESC;
```

**Query the health view:**
```sql
SELECT * FROM v_table_health
WHERE health_status != 'Healthy'
OR design_recommendation != 'OK';
```

### Task 14: Implement Automatic Table Optimization
Enable AUTO distribution and sort keys:

**Create table with AUTO settings:**
```sql
CREATE TABLE sales_auto (
    sale_id BIGINT NOT NULL,
    order_date DATE NOT NULL,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    total_amount DECIMAL(10,2)
)
DISTSTYLE AUTO  -- Let Redshift choose distribution
SORTKEY AUTO;   -- Let Redshift choose sort keys
```

**Benefits:**
- Redshift monitors query patterns
- Automatically adjusts distribution and sort keys
- Adapts to changing workloads
- Reduces manual tuning

**Check AUTO optimization status:**
```sql
SELECT 
    tablename,
    diststyle,
    sortkey1,
    automatic_compression
FROM pg_table_def
WHERE schemaname = 'public'
AND tablename LIKE 'sales%';
```

### Task 15: Create Performance Baseline
Document current performance metrics:

```sql
-- Baseline query 1: Aggregate by date
SELECT 
    order_date,
    COUNT(*) as num_orders,
    SUM(total_amount) as revenue
FROM sales_fact
WHERE order_date >= '2024-01-01'
GROUP BY order_date
ORDER BY order_date;

-- Baseline query 2: Join with dimensions
SELECT 
    p.category,
    c.customer_segment,
    COUNT(*) as num_orders,
    SUM(s.total_amount) as revenue
FROM sales_fact s
JOIN dim_products p ON s.product_id = p.product_id
JOIN dim_customers c ON s.customer_id = c.customer_id
WHERE s.order_date >= '2024-01-01'
GROUP BY p.category, c.customer_segment;

-- Measure execution time
SELECT 
    query,
    TRIM(querytxt) as query_text,
    starttime,
    endtime,
    DATEDIFF(seconds, starttime, endtime) as duration_seconds
FROM stl_query
WHERE userid > 1
AND query IN (SELECT MAX(query) FROM stl_query WHERE userid > 1)
ORDER BY starttime DESC
LIMIT 5;
```

**Document metrics:**
- Query execution time (before optimization)
- Table sizes
- Distribution skew
- Unsorted percentage

**After optimization, measure improvements:**
- Query speedup: 2-10x typical
- Storage reduction: 30-70% with compression
- Cost savings: Based on compute time reduction

## Validation

Run the validation script:

```bash
python validate_tasks.py redshift_design
```

The script will verify:
- Fact table `sales_fact` exists with DISTKEY
- Dimension tables use DISTSTYLE ALL
- Tables have appropriate SORTKEY configuration
- Compression encoding is applied
- VACUUM and ANALYZE have been run recently
- Monitoring views exist
- Performance baseline documented
- Workgroup configuration includes WLM settings

## Cleanup (After Assessment)
1. Drop all optimized tables
2. Drop monitoring views
3. Reset WLM configuration to default
4. Document learnings and performance improvements

## Tips
- **DISTKEY** should match most common JOIN column
- Use **DISTSTYLE ALL** for small dimension tables (< 1M rows)
- **COMPOUND SORTKEY** for queries filtering on leftmost columns
- **INTERLEAVED SORTKEY** for queries using different column combinations
- Run **VACUUM** after deletes/updates > 10%
- Run **ANALYZE** after significant data changes
- **SQA** improves dashboard query performance
- **Result caching** effective for repeated queries
- Monitor **SVV_TABLE_INFO** regularly
- **AUTO** settings good for new workloads
- Aim for < 10% unsorted rows
- Target < 2.0 distribution skew ratio

## Common Issues
- **Slow queries**: Check distribution skew and sort keys
- **High storage costs**: Apply compression encoding
- **Uneven data distribution**: Review DISTKEY choice
- **Long VACUUM time**: Use VACUUM DELETE ONLY or SORT ONLY
- **Stale statistics**: Run ANALYZE more frequently
- **Query timeouts**: Review WLM memory allocation
- **Cache misses**: Check if queries are identical

## Learning Resources
- Distribution styles (KEY, ALL, EVEN, AUTO)
- Sort keys (COMPOUND vs INTERLEAVED)
- Compression encoding algorithms
- VACUUM and ANALYZE operations
- Workload Management (WLM)
- Short Query Acceleration (SQA)
- Result set caching
- Distribution skew analysis
- Query monitoring and tuning
- Automatic table optimization
