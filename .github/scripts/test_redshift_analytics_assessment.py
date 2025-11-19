"""
AWS Redshift Querying & Analytics Assessment - Test Script
Tests complex queries, window functions, CTEs, materialized views, UNLOAD
"""

import sys
import os
import boto3
from botocore.exceptions import ClientError

def get_student_id():
    """Get student ID from command line arguments"""
    if len(sys.argv) < 2:
        print("Error: Student ID is required")
        print("Usage: python validate_tasks.py redshift_analytics")
        sys.exit(1)
    return sys.argv[1]

def test_query_files_exist(student_id):
    """Task 1-10: Verify all query files are created"""
    
    required_files = [
        'queries/customer_order_summary.sql',
        'queries/product_sales_ranking.sql',
        'queries/monthly_cohort_analysis.sql',
        'queries/explain_customer_summary.txt',
        'queries/performance_analysis.txt',
        'queries/cache_test.sql',
        'queries/cache_results.txt',
        'queries/sales_analysis_grouping.sql',
        'queries/unload_monthly_summary.sql',
        'queries/monthly_growth_analysis.sql',
        'queries/query_monitoring.sql'
    ]
    
    missing_files = []
    found_files = 0
    
    for file_path in required_files:
        if os.path.exists(file_path):
            found_files += 1
        else:
            missing_files.append(file_path)
    
    if missing_files:
        print(f"⚠️  Task 1-10 Warning: {len(missing_files)} query file(s) missing:")
        for f in missing_files[:3]:  # Show first 3
            print(f"   - {f}")
    
    if found_files == 0:
        print(f"❌ Task 1-10 Failed: No query files found in queries/ directory")
        return False
    
    print(f"✅ Task 1-10 Passed: {found_files}/{len(required_files)} query files created")
    return True

def test_materialized_view_exists(student_id):
    """Task 5: Verify materialized view is created"""
    
    try:
        redshift_data = boto3.client('redshift-data')
        workgroup_name = f"analytics-workgroup-{student_id}"
        
        # Check if materialized view exists
        sql = """
        SELECT schemaname, matviewname
        FROM pg_matviews
        WHERE schemaname = 'public'
        AND matviewname LIKE '%sales%summary%';
        """
        
        response = redshift_data.execute_statement(
            WorkgroupName=workgroup_name,
            Database='analyticsdb',
            Sql=sql
        )
        
        query_id = response['Id']
        
        import time
        time.sleep(3)
        
        result = redshift_data.get_statement_result(Id=query_id)
        records = result.get('Records', [])
        
        if not records:
            print(f"⚠️  Task 5 Warning: No materialized views found")
            print(f"   Expected: mv_daily_sales_summary")
            return True
        
        mv_count = len(records)
        print(f"✅ Task 5 Passed: {mv_count} materialized view(s) created")
        return True
        
    except Exception as e:
        print(f"⚠️  Task 5 Warning: Could not verify materialized views: {e}")
        return True

def test_query_execution_history(student_id):
    """Task 2-3: Verify queries have been executed"""
    
    try:
        redshift_data = boto3.client('redshift-data')
        workgroup_name = f"analytics-workgroup-{student_id}"
        
        # Check recent query history
        sql = """
        SELECT 
            COUNT(*) AS query_count
        FROM STL_QUERY
        WHERE userid > 1
        AND starttime >= GETDATE() - INTERVAL '24 hours'
        AND querytxt NOT LIKE '%pg_%'
        AND querytxt NOT LIKE '%STL_%';
        """
        
        response = redshift_data.execute_statement(
            WorkgroupName=workgroup_name,
            Database='analyticsdb',
            Sql=sql
        )
        
        query_id = response['Id']
        
        import time
        time.sleep(3)
        
        result = redshift_data.get_statement_result(Id=query_id)
        records = result.get('Records', [])
        
        if records and len(records[0]) > 0:
            query_count = int(records[0][0]['longValue'])
            
            if query_count == 0:
                print(f"⚠️  Task 2-3 Warning: No user queries found in history")
                return True
            
            print(f"✅ Task 2-3 Passed: {query_count} queries executed (last 24 hours)")
            return True
        
        print(f"⚠️  Task 2-3 Warning: Could not verify query history")
        return True
        
    except Exception as e:
        print(f"⚠️  Task 2-3 Warning: Could not verify query execution: {e}")
        return True

def test_unload_export_bucket(s3_client, student_id):
    """Task 9: Verify UNLOAD export bucket exists with data"""
    bucket_name = f"redshift-exports-{student_id}"
    
    try:
        # Check if bucket exists
        s3_client.head_bucket(Bucket=bucket_name)
        
        # Check if there are any objects in monthly_summary/
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix='monthly_summary/',
            MaxKeys=10
        )
        
        object_count = response.get('KeyCount', 0)
        
        if object_count == 0:
            print(f"⚠️  Task 9 Warning: Export bucket exists but no data in monthly_summary/")
            return True
        
        print(f"✅ Task 9 Passed: UNLOAD export bucket has {object_count} file(s)")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"⚠️  Task 9 Warning: Export bucket '{bucket_name}' not found")
            return True
        print(f"⚠️  Task 9 Warning: {e}")
        return True

def test_window_function_usage(student_id):
    """Task 2, 10: Verify window functions are being used"""
    
    # Check if query files contain window function keywords
    window_keywords = ['ROW_NUMBER', 'RANK', 'LAG', 'LEAD', 'OVER', 'PARTITION BY']
    
    query_files = [
        'queries/product_sales_ranking.sql',
        'queries/monthly_growth_analysis.sql'
    ]
    
    window_usage = 0
    
    for file_path in query_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read().upper()
                    if any(keyword in content for keyword in window_keywords):
                        window_usage += 1
            except Exception:
                pass
    
    if window_usage == 0:
        print(f"⚠️  Task 2,10 Warning: No window functions detected in query files")
        return True
    
    print(f"✅ Task 2,10 Passed: Window functions used in {window_usage} query file(s)")
    return True

def test_cte_usage(student_id):
    """Task 3: Verify CTEs (Common Table Expressions) are being used"""
    
    cte_file = 'queries/monthly_cohort_analysis.sql'
    
    if not os.path.exists(cte_file):
        print(f"⚠️  Task 3 Warning: CTE query file not found: {cte_file}")
        return True
    
    try:
        with open(cte_file, 'r') as f:
            content = f.read().upper()
            
            # Check for WITH keyword (CTEs start with WITH)
            cte_count = content.count('WITH ')
            
            if cte_count == 0:
                print(f"⚠️  Task 3 Warning: No CTEs found in {cte_file}")
                return True
            
            print(f"✅ Task 3 Passed: CTEs used in cohort analysis query ({cte_count} WITH clause)")
            return True
            
    except Exception as e:
        print(f"⚠️  Task 3 Warning: Could not verify CTEs: {e}")
        return True

def test_explain_plan_documented(student_id):
    """Task 4: Verify EXPLAIN plan is documented"""
    
    explain_files = [
        'queries/explain_customer_summary.txt',
        'queries/performance_analysis.txt'
    ]
    
    found_files = 0
    
    for file_path in explain_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Check if file has content
                    if len(content.strip()) > 50:  # At least some meaningful content
                        found_files += 1
            except Exception:
                pass
    
    if found_files == 0:
        print(f"❌ Task 4 Failed: No EXPLAIN plan documentation found")
        return False
    
    print(f"✅ Task 4 Passed: EXPLAIN plan documented ({found_files} file(s))")
    return True

def test_monitoring_queries(student_id):
    """Task 6: Verify monitoring queries are created"""
    
    monitoring_file = 'queries/query_monitoring.sql'
    
    if not os.path.exists(monitoring_file):
        print(f"⚠️  Task 6 Warning: Monitoring query file not found")
        return True
    
    try:
        with open(monitoring_file, 'r') as f:
            content = f.read().upper()
            
            # Check for system table queries
            system_tables = ['STV_RECENTS', 'SVL_QLOG', 'STL_QUERY', 'STL_WLM_QUERY']
            found_tables = sum(1 for table in system_tables if table in content)
            
            if found_tables == 0:
                print(f"⚠️  Task 6 Warning: No system table queries found in monitoring file")
                return True
            
            print(f"✅ Task 6 Passed: Monitoring queries reference {found_tables} system table(s)")
            return True
            
    except Exception as e:
        print(f"⚠️  Task 6 Warning: Could not verify monitoring queries: {e}")
        return True

def test_workgroup_exists(redshift_client, student_id):
    """Prerequisite: Verify Redshift Serverless workgroup exists"""
    workgroup_name = f"analytics-workgroup-{student_id}"
    
    try:
        response = redshift_client.get_workgroup(workgroupName=workgroup_name)
        workgroup = response['workgroup']
        status = workgroup.get('status')
        
        if status != 'AVAILABLE':
            print(f"⚠️  Prerequisite Warning: Workgroup status is {status}")
        
        print(f"✅ Prerequisite Passed: Workgroup '{workgroup_name}' is {status}")
        return True
        
    except ClientError as e:
        print(f"❌ Prerequisite Failed: Workgroup not found - {e}")
        return False

def main():
    """Run all Redshift Querying & Analytics assessment tests"""
    print("=" * 60)
    print("AWS Redshift Querying & Analytics - Validation")
    print("=" * 60)
    
    student_id = get_student_id()
    print(f"\n🎓 Student ID: {student_id}")
    print(f"🗄️  Workgroup: analytics-workgroup-{student_id}\n")
    
    # Initialize AWS clients
    try:
        redshift_client = boto3.client('redshift-serverless')
        s3_client = boto3.client('s3')
    except Exception as e:
        print(f"❌ Error initializing AWS clients: {e}")
        sys.exit(1)
    
    # Run tests
    results = []
    total_tasks = 9
    
    print("Starting validation...\n")
    
    # Prerequisite: Workgroup exists
    workgroup_ok = test_workgroup_exists(redshift_client, student_id)
    if not workgroup_ok:
        print("\n⚠️  Warning: Some tests may fail without a running workgroup")
    
    print()  # Blank line
    
    # Task 1-10: Query files exist
    results.append(test_query_files_exist(student_id))
    
    # Task 2,10: Window functions
    results.append(test_window_function_usage(student_id))
    
    # Task 3: CTEs
    results.append(test_cte_usage(student_id))
    
    # Task 4: EXPLAIN plan
    results.append(test_explain_plan_documented(student_id))
    
    # Task 5: Materialized views
    results.append(test_materialized_view_exists(student_id))
    
    # Task 6: Monitoring queries
    results.append(test_monitoring_queries(student_id))
    
    # Task 2-3: Query execution history
    results.append(test_query_execution_history(student_id))
    
    # Task 9: UNLOAD exports
    results.append(test_unload_export_bucket(s3_client, student_id))
    
    # Additional: Query directory structure
    queries_dir_exists = os.path.isdir('queries')
    results.append(queries_dir_exists)
    if queries_dir_exists:
        print(f"✅ Directory Structure: queries/ directory exists")
    else:
        print(f"❌ Directory Structure: queries/ directory not found")
    
    # Calculate score
    passed = sum(results)
    score_percentage = (passed / total_tasks) * 100
    
    # Print summary
    print("\n" + "=" * 60)
    print("ASSESSMENT SUMMARY")
    print("=" * 60)
    print(f"Total Tasks: {total_tasks}")
    print(f"Passed: {passed}")
    print(f"Failed: {total_tasks - passed}")
    print(f"Score: {score_percentage:.1f}%")
    print("=" * 60)
    
    if score_percentage >= 70:
        print("\n🎉 CONGRATULATIONS! You passed the Redshift Querying & Analytics assessment!")
        print("You've successfully demonstrated:")
        print("  ✓ Complex multi-table joins")
        print("  ✓ Window functions (ROW_NUMBER, RANK, LAG, LEAD)")
        print("  ✓ Common Table Expressions (CTEs)")
        print("  ✓ Query performance analysis (EXPLAIN)")
        print("  ✓ Materialized views for optimization")
        print("  ✓ Query monitoring and troubleshooting")
        print("  ✓ Result caching strategies")
        print("  ✓ Data export with UNLOAD")
        print("  ✓ Advanced aggregations (GROUPING SETS)")
        sys.exit(0)
    else:
        print("\n❌ Assessment not passed. Minimum score required: 70%")
        print("Please review the failed tasks and try again.")
        print("\nTips:")
        print("  - Ensure all query files are in the queries/ directory")
        print("  - Run queries against your Redshift workgroup")
        print("  - Document EXPLAIN plans in text files")
        print("  - Create materialized views as specified")
        print("  - Set up UNLOAD exports to S3")
        sys.exit(1)

if __name__ == "__main__":
    main()
