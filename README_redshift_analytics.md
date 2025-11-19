# AWS Redshift Querying & Analytics Assessment

## Overview
Master advanced SQL querying and analytics capabilities in Amazon Redshift Serverless. Learn to write complex queries, optimize performance, use window functions, and leverage Redshift's powerful analytical features.

**Difficulty**: Medium  
**Prerequisites**: Completion of Redshift Data Ingestion & Storage assessment  
**Estimated Time**: 2-3 hours  

## Learning Objectives
- Write complex analytical queries with JOINs and aggregations
- Master window functions for advanced analytics
- Use Common Table Expressions (CTEs) for query organization
- Optimize query performance with EXPLAIN plans
- Leverage materialized views for faster queries
- Implement result caching strategies
- Use UNLOAD for efficient data export

## Prerequisites
- Completed Redshift Data Ingestion assessment
- Tables with data: `customers`, `orders`, `products`, `transactions`, `sales_fact`
- Dimension tables: `dim_customers`, `dim_products`, `dim_stores`
- Running Redshift Serverless workgroup: `analytics-workgroup-{student_id}`

---

## Tasks

### Task 1: Complex Multi-Table Join Query
**Objective**: Write and execute a complex query joining multiple tables.

Create a query named `customer_order_summary.sql` that:
- Joins `customers`, `orders`, `products`, and `transactions` tables
- Calculates total revenue per customer
- Includes customer name, email, order count, and total spent
- Filters for customers with more than 3 orders
- Orders results by total revenue descending

**Query Structure**:
```sql
-- Save as: queries/customer_order_summary.sql
SELECT 
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.email,
    COUNT(DISTINCT o.order_id) AS order_count,
    SUM(t.amount) AS total_revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN transactions t ON o.order_id = t.order_id
WHERE o.order_status = 'completed'
GROUP BY c.customer_id, c.first_name, c.last_name, c.email
HAVING COUNT(DISTINCT o.order_id) > 3
ORDER BY total_revenue DESC;
```

**Validation**:
```bash
# Run query via Redshift query editor or AWS CLI
aws redshift-data execute-statement \
  --workgroup-name analytics-workgroup-{student_id} \
  --database analyticsdb \
  --sql "$(cat queries/customer_order_summary.sql)"
```

---

### Task 2: Window Functions for Ranking
**Objective**: Use window functions for ranking and running totals.

Create a query `product_sales_ranking.sql` that:
- Ranks products by revenue within each category
- Calculates running total of sales
- Uses `ROW_NUMBER()`, `RANK()`, and `SUM() OVER()`
- Shows top 10 products per category

**Query Example**:
```sql
-- Save as: queries/product_sales_ranking.sql
SELECT 
    p.category,
    p.product_name,
    SUM(t.amount) AS revenue,
    ROW_NUMBER() OVER (PARTITION BY p.category ORDER BY SUM(t.amount) DESC) AS rank_in_category,
    SUM(SUM(t.amount)) OVER (PARTITION BY p.category ORDER BY SUM(t.amount) DESC 
                             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM products p
JOIN transactions t ON p.product_id = t.product_id
GROUP BY p.category, p.product_name, p.product_id
QUALIFY rank_in_category <= 10
ORDER BY p.category, rank_in_category;
```

---

### Task 3: Common Table Expressions (CTEs)
**Objective**: Organize complex logic using CTEs.

Create a query `monthly_cohort_analysis.sql` with multiple CTEs:
- CTE 1: Calculate first purchase month per customer
- CTE 2: Calculate total purchases per customer per month
- CTE 3: Aggregate cohort retention metrics
- Final query joins CTEs for cohort analysis

**Query Structure**:
```sql
-- Save as: queries/monthly_cohort_analysis.sql
WITH first_purchase AS (
    SELECT 
        customer_id,
        DATE_TRUNC('month', MIN(order_date))::DATE AS cohort_month
    FROM orders
    GROUP BY customer_id
),
monthly_purchases AS (
    SELECT 
        customer_id,
        DATE_TRUNC('month', order_date)::DATE AS purchase_month,
        COUNT(*) AS purchase_count,
        SUM(order_total) AS total_spent
    FROM orders
    WHERE order_status = 'completed'
    GROUP BY customer_id, DATE_TRUNC('month', order_date)
),
cohort_data AS (
    SELECT 
        fp.cohort_month,
        mp.purchase_month,
        DATEDIFF(month, fp.cohort_month, mp.purchase_month) AS months_since_first,
        COUNT(DISTINCT mp.customer_id) AS customers,
        SUM(mp.total_spent) AS cohort_revenue
    FROM first_purchase fp
    JOIN monthly_purchases mp ON fp.customer_id = mp.customer_id
    GROUP BY fp.cohort_month, mp.purchase_month
)
SELECT 
    cohort_month,
    months_since_first,
    customers,
    cohort_revenue,
    ROUND(cohort_revenue / customers, 2) AS avg_revenue_per_customer
FROM cohort_data
ORDER BY cohort_month, months_since_first;
```

---

### Task 4: EXPLAIN Plan Analysis
**Objective**: Analyze and optimize query performance using EXPLAIN.

For your `customer_order_summary.sql` query:
1. Run with `EXPLAIN` to see execution plan
2. Document the plan in `performance_analysis.txt`
3. Identify any sequential scans
4. Note estimated rows and cost

**Commands**:
```sql
-- Save output to: queries/explain_customer_summary.txt
EXPLAIN
SELECT 
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    COUNT(DISTINCT o.order_id) AS order_count,
    SUM(t.amount) AS total_revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN transactions t ON o.order_id = t.order_id
WHERE o.order_status = 'completed'
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY total_revenue DESC;

-- Also run with verbose option for more details
EXPLAIN VERBOSE [same query];
```

**Document**:
- Create `queries/performance_analysis.txt`
- List all steps in execution plan
- Note any performance concerns (seq scans, nested loops)
- Suggest improvements (indexes, distribution keys)

---

### Task 5: Materialized Views
**Objective**: Create materialized views for frequently accessed aggregations.

Create a materialized view `mv_daily_sales_summary`:
```sql
CREATE MATERIALIZED VIEW mv_daily_sales_summary AS
SELECT 
    DATE_TRUNC('day', o.order_date)::DATE AS sale_date,
    p.category,
    p.product_name,
    COUNT(DISTINCT o.order_id) AS order_count,
    SUM(t.quantity) AS units_sold,
    SUM(t.amount) AS revenue,
    AVG(t.amount) AS avg_order_value
FROM orders o
JOIN transactions t ON o.order_id = t.order_id
JOIN products p ON t.product_id = p.product_id
WHERE o.order_status = 'completed'
GROUP BY DATE_TRUNC('day', o.order_date), p.category, p.product_name;
```

**Refresh Strategy**:
```sql
-- Manual refresh
REFRESH MATERIALIZED VIEW mv_daily_sales_summary;

-- Create a stored procedure for scheduled refresh
CREATE OR REPLACE PROCEDURE sp_refresh_sales_summary()
LANGUAGE plpgsql
AS $$
BEGIN
    REFRESH MATERIALIZED VIEW mv_daily_sales_summary;
END;
$$;
```

**Validation**:
```sql
-- Query materialized view (should be faster than base tables)
SELECT * FROM mv_daily_sales_summary
WHERE sale_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY sale_date DESC, revenue DESC;
```

---

### Task 6: Query Monitoring and Performance
**Objective**: Monitor query execution and identify slow queries.

Create monitoring queries in `queries/query_monitoring.sql`:

```sql
-- Save as: queries/query_monitoring.sql

-- 1. Currently running queries
SELECT 
    query,
    pid,
    user_name,
    starttime,
    DATEDIFF(second, starttime, GETDATE()) AS duration_seconds,
    LEFT(querytxt, 100) AS query_text
FROM STV_RECENTS
WHERE status = 'Running'
ORDER BY duration_seconds DESC;

-- 2. Top 10 longest running queries (last 24 hours)
SELECT 
    userid,
    query,
    starttime,
    endtime,
    DATEDIFF(second, starttime, endtime) AS duration_seconds,
    LEFT(querytxt, 100) AS query_text
FROM SVL_QLOG
WHERE starttime >= GETDATE() - INTERVAL '24 hours'
ORDER BY duration_seconds DESC
LIMIT 10;

-- 3. Queries with disk-based operations (potential memory issues)
SELECT 
    q.query,
    q.starttime,
    COUNT(*) AS disk_operations,
    SUM(s.rows) AS total_rows
FROM SVL_QUERY_SUMMARY s
JOIN STL_QUERY q ON s.query = q.query
WHERE s.is_diskbased = 't'
  AND q.starttime >= GETDATE() - INTERVAL '24 hours'
GROUP BY q.query, q.starttime
ORDER BY disk_operations DESC
LIMIT 10;

-- 4. Query queue wait times
SELECT 
    query,
    service_class,
    queue_start_time,
    queue_end_time,
    DATEDIFF(second, queue_start_time, queue_end_time) AS wait_seconds
FROM STL_WLM_QUERY
WHERE queue_start_time >= GETDATE() - INTERVAL '24 hours'
  AND queue_end_time IS NOT NULL
ORDER BY wait_seconds DESC
LIMIT 20;
```

---

### Task 7: Result Caching Test
**Objective**: Understand and verify result caching behavior.

Test result caching with these steps:

1. **Run query first time** (cold cache):
```sql
-- Save as: queries/cache_test.sql
SELECT 
    category,
    COUNT(*) AS product_count,
    AVG(price) AS avg_price,
    SUM(price) AS total_value
FROM products
GROUP BY category;
```

2. **Document execution time** in `queries/cache_results.txt`:
```
First run (cold): [record execution time]
Query ID: [record query ID from SVL_QLOG]
```

3. **Run same query again** (warm cache):
```sql
-- Exact same query
SELECT 
    category,
    COUNT(*) AS product_count,
    AVG(price) AS avg_price,
    SUM(price) AS total_value
FROM products
GROUP BY category;
```

4. **Document second run**:
```
Second run (warm): [record execution time]
Query ID: [record query ID]
Speedup: [calculate percentage improvement]
```

5. **Verify caching** in system tables:
```sql
-- Check if query was served from cache
SELECT 
    query,
    starttime,
    endtime,
    CASE WHEN result_cache_hit = 1 THEN 'Cache Hit' ELSE 'Cache Miss' END AS cache_status
FROM SVL_QLOG
WHERE querytxt LIKE '%category%product_count%'
ORDER BY starttime DESC
LIMIT 5;
```

---

### Task 8: Aggregate Functions and GROUPING SETS
**Objective**: Use advanced aggregation features for multi-dimensional analysis.

Create query `sales_analysis_grouping.sql`:
```sql
-- Save as: queries/sales_analysis_grouping.sql
SELECT 
    COALESCE(category, 'ALL CATEGORIES') AS category,
    COALESCE(region, 'ALL REGIONS') AS region,
    COALESCE(DATE_TRUNC('month', sale_date)::VARCHAR, 'ALL MONTHS') AS sale_month,
    SUM(revenue) AS total_revenue,
    COUNT(DISTINCT customer_id) AS unique_customers,
    AVG(revenue) AS avg_revenue
FROM (
    SELECT 
        p.category,
        c.region,
        o.order_date AS sale_date,
        t.amount AS revenue,
        c.customer_id
    FROM orders o
    JOIN transactions t ON o.order_id = t.order_id
    JOIN products p ON t.product_id = p.product_id
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'completed'
) sales_data
GROUP BY GROUPING SETS (
    (category, region, DATE_TRUNC('month', sale_date)),  -- Full detail
    (category, region),                                   -- By category and region
    (category),                                           -- By category only
    ()                                                    -- Grand total
)
ORDER BY category NULLS LAST, region NULLS LAST, sale_month NULLS LAST;
```

---

### Task 9: UNLOAD Data Export
**Objective**: Export query results to S3 using UNLOAD.

Export aggregated data to S3:
```sql
-- Save as: queries/unload_monthly_summary.sql
UNLOAD (
    'SELECT 
        DATE_TRUNC(''month'', order_date)::DATE AS month,
        category,
        COUNT(*) AS order_count,
        SUM(revenue) AS total_revenue,
        AVG(revenue) AS avg_revenue
    FROM (
        SELECT 
            o.order_date,
            p.category,
            t.amount AS revenue
        FROM orders o
        JOIN transactions t ON o.order_id = t.order_id
        JOIN products p ON t.product_id = p.product_id
        WHERE o.order_status = ''completed''
    ) base
    GROUP BY DATE_TRUNC(''month'', order_date), category
    ORDER BY month DESC, category'
)
TO 's3://redshift-exports-{student_id}/monthly_summary/'
IAM_ROLE 'arn:aws:iam::{account_id}:role/RedshiftS3ExportRole-{student_id}'
FORMAT AS PARQUET
PARTITION BY (month)
ALLOWOVERWRITE
PARALLEL OFF;
```

**Create export bucket**:
```bash
aws s3 mb s3://redshift-exports-{student_id}
```

**Verify export**:
```bash
aws s3 ls s3://redshift-exports-{student_id}/monthly_summary/ --recursive
```

---

### Task 10: Time Series Analysis with LAG/LEAD
**Objective**: Use window functions for period-over-period comparisons.

Create query `monthly_growth_analysis.sql`:
```sql
-- Save as: queries/monthly_growth_analysis.sql
WITH monthly_metrics AS (
    SELECT 
        DATE_TRUNC('month', order_date)::DATE AS month,
        COUNT(DISTINCT customer_id) AS active_customers,
        COUNT(*) AS order_count,
        SUM(order_total) AS revenue
    FROM orders
    WHERE order_status = 'completed'
    GROUP BY DATE_TRUNC('month', order_date)
)
SELECT 
    month,
    active_customers,
    order_count,
    revenue,
    LAG(revenue, 1) OVER (ORDER BY month) AS prev_month_revenue,
    revenue - LAG(revenue, 1) OVER (ORDER BY month) AS revenue_change,
    ROUND(
        (revenue - LAG(revenue, 1) OVER (ORDER BY month)) * 100.0 / 
        NULLIF(LAG(revenue, 1) OVER (ORDER BY month), 0), 
        2
    ) AS revenue_growth_pct,
    LEAD(revenue, 1) OVER (ORDER BY month) AS next_month_revenue,
    AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS three_month_avg
FROM monthly_metrics
ORDER BY month;
```

---

## Validation Commands

```bash
# Test all queries exist
ls -la queries/

# Run query monitoring
aws redshift-data execute-statement \
  --workgroup-name analytics-workgroup-{student_id} \
  --database analyticsdb \
  --sql "$(cat queries/query_monitoring.sql)"

# Verify materialized view
aws redshift-data execute-statement \
  --workgroup-name analytics-workgroup-{student_id} \
  --database analyticsdb \
  --sql "SELECT COUNT(*) FROM mv_daily_sales_summary"

# Check UNLOAD results
aws s3 ls s3://redshift-exports-{student_id}/ --recursive
```

---

## Success Criteria

✅ **Queries Created**: All 10 SQL query files in `queries/` directory  
✅ **Complex Joins**: Multi-table joins execute successfully  
✅ **Window Functions**: ROW_NUMBER, RANK, LAG, LEAD used correctly  
✅ **CTEs**: Queries use CTEs for organization  
✅ **EXPLAIN Plans**: Performance analysis documented  
✅ **Materialized Views**: MV created and refreshed  
✅ **Result Caching**: Cache behavior verified and documented  
✅ **UNLOAD**: Data exported to S3 successfully  
✅ **Performance**: Queries complete in reasonable time (<30 seconds)  

---

## Testing Your Work

Run the validation script:
```bash
python validate_tasks.py redshift_analytics
```

The script will verify:
- Query files exist in correct location
- Materialized views are created
- UNLOAD export bucket has data
- Query execution history
- Performance metrics are reasonable

**Minimum passing score**: 70% (7 out of 10 tasks)

---

## Additional Resources

- [Redshift SQL Reference](https://docs.aws.amazon.com/redshift/latest/dg/cm_chap_SQLCommandRef.html)
- [Window Functions in Redshift](https://docs.aws.amazon.com/redshift/latest/dg/c_Window_functions.html)
- [Query Performance Tuning](https://docs.aws.amazon.com/redshift/latest/dg/c-optimizing-query-performance.html)
- [Materialized Views](https://docs.aws.amazon.com/redshift/latest/dg/materialized-view-overview.html)
- [UNLOAD Command](https://docs.aws.amazon.com/redshift/latest/dg/r_UNLOAD.html)

---

## Cost Considerations

**Redshift Serverless Pricing**:
- Charged for RPU-hours (Redshift Processing Units)
- Complex queries consume more RPUs
- Result caching reduces costs
- Auto-pause when idle (no charge)

**Estimated Cost**: $2-5 for this assessment (2-3 hours of active querying)

---

## Troubleshooting

**Query runs too long**:
- Check EXPLAIN plan for sequential scans
- Verify distribution and sort keys
- Run VACUUM and ANALYZE

**Out of memory errors**:
- Reduce result set size with LIMIT
- Break complex queries into smaller CTEs
- Increase workgroup capacity (RPUs)

**Cache not working**:
- Ensure exact same query (whitespace matters)
- Check result cache settings
- Verify query completion

---

## Next Steps

After completing this assessment:
1. ✅ Review query performance metrics
2. ✅ Experiment with different window functions
3. ✅ Create additional materialized views for common queries
4. ✅ Set up scheduled query execution with Lambda
5. ✅ Explore integration with BI tools (QuickSight, Tableau)

**Good luck with your Redshift Querying & Analytics assessment!** 🚀
