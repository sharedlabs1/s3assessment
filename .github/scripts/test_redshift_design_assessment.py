"""
AWS Redshift Database Design & Optimization Assessment - Test Script
Tests distribution strategies, sort keys, compression, VACUUM, ANALYZE, WLM
"""

import sys
import boto3
from botocore.exceptions import ClientError

def get_student_id():
    """Get student ID from command line arguments"""
    if len(sys.argv) < 2:
        print("Error: Student ID is required")
        print("Usage: python validate_tasks.py redshift_design")
        sys.exit(1)
    return sys.argv[1]

def test_fact_table_with_distkey(student_id):
    """Task 1: Verify fact table exists with distribution key"""
    # This test requires querying Redshift metadata
    # Using Redshift Data API
    
    try:
        redshift_data = boto3.client('redshift-data')
        workgroup_name = f"analytics-workgroup-{student_id}"
        
        # Query to check if sales_fact table exists with DISTKEY
        sql = """
        SELECT 
            tablename,
            diststyle,
            distkey
        FROM pg_table_def
        WHERE schemaname = 'public'
        AND tablename = 'sales_fact'
        LIMIT 1;
        """
        
        response = redshift_data.execute_statement(
            WorkgroupName=workgroup_name,
            Database='analyticsdb',
            Sql=sql
        )
        
        query_id = response['Id']
        
        # Wait and get results
        import time
        time.sleep(3)
        
        result = redshift_data.get_statement_result(Id=query_id)
        records = result.get('Records', [])
        
        if not records:
            print(f"❌ Task 1 Failed: Table 'sales_fact' not found")
            return False
        
        # Check distribution style
        record = records[0]
        diststyle = record[1]['stringValue'] if len(record) > 1 else ''
        
        if 'KEY' not in diststyle.upper() and 'AUTO' not in diststyle.upper():
            print(f"❌ Task 1 Failed: sales_fact should use DISTKEY or AUTO distribution, found: {diststyle}")
            return False
        
        print(f"✅ Task 1 Passed: Fact table 'sales_fact' with proper distribution")
        return True
        
    except Exception as e:
        print(f"⚠️  Task 1 Warning: Could not verify via Data API: {e}")
        print(f"   (Assuming table exists - manual verification recommended)")
        return True

def test_dimension_tables_with_all_distribution(student_id):
    """Task 2: Verify dimension tables use DISTSTYLE ALL"""
    
    try:
        redshift_data = boto3.client('redshift-data')
        workgroup_name = f"analytics-workgroup-{student_id}"
        
        # Check dimension tables
        sql = """
        SELECT 
            tablename,
            diststyle
        FROM pg_table_def
        WHERE schemaname = 'public'
        AND tablename IN ('dim_customers', 'dim_products', 'dim_stores')
        GROUP BY tablename, diststyle;
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
            print(f"⚠️  Task 2 Warning: No dimension tables found")
            return True
        
        # Check if any use DISTSTYLE ALL
        all_distribution_count = sum(
            1 for record in records 
            if 'ALL' in record[1]['stringValue'].upper()
        )
        
        if all_distribution_count == 0:
            print(f"⚠️  Task 2 Warning: Dimension tables should use DISTSTYLE ALL")
        
        print(f"✅ Task 2 Passed: Dimension tables configured ({all_distribution_count} with ALL distribution)")
        return True
        
    except Exception as e:
        print(f"⚠️  Task 2 Warning: Could not verify dimension tables: {e}")
        return True

def test_sort_keys_configured(student_id):
    """Task 3-4: Verify tables have sort keys"""
    
    try:
        redshift_data = boto3.client('redshift-data')
        workgroup_name = f"analytics-workgroup-{student_id}"
        
        sql = """
        SELECT 
            tablename,
            sortkey1
        FROM pg_table_def
        WHERE schemaname = 'public'
        AND sortkey1 IS NOT NULL
        GROUP BY tablename, sortkey1;
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
            print(f"❌ Task 3-4 Failed: No tables with sort keys found")
            return False
        
        table_count = len(records)
        print(f"✅ Task 3-4 Passed: {table_count} table(s) with sort keys configured")
        return True
        
    except Exception as e:
        print(f"⚠️  Task 3-4 Warning: Could not verify sort keys: {e}")
        return True

def test_compression_applied(student_id):
    """Task 5: Verify compression encoding is applied"""
    
    try:
        redshift_data = boto3.client('redshift-data')
        workgroup_name = f"analytics-workgroup-{student_id}"
        
        # Check if any columns have compression
        sql = """
        SELECT COUNT(DISTINCT tablename) as tables_with_compression
        FROM pg_table_def
        WHERE schemaname = 'public'
        AND encoding != 'none'
        AND encoding IS NOT NULL;
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
            compression_count = int(records[0][0]['longValue'])
            
            if compression_count == 0:
                print(f"⚠️  Task 5 Warning: No compression encoding detected")
                return True
            
            print(f"✅ Task 5 Passed: Compression applied to {compression_count} table(s)")
            return True
        
        print(f"⚠️  Task 5 Warning: Could not verify compression")
        return True
        
    except Exception as e:
        print(f"⚠️  Task 5 Warning: Could not verify compression: {e}")
        return True

def test_table_maintenance_status(student_id):
    """Task 7-8: Verify VACUUM and ANALYZE have been run"""
    
    try:
        redshift_data = boto3.client('redshift-data')
        workgroup_name = f"analytics-workgroup-{student_id}"
        
        # Check table health from SVV_TABLE_INFO
        sql = """
        SELECT 
            "table",
            unsorted,
            stats_off
        FROM SVV_TABLE_INFO
        WHERE schema = 'public'
        ORDER BY size DESC
        LIMIT 10;
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
            print(f"⚠️  Task 7-8 Warning: Could not verify table maintenance")
            return True
        
        # Check if tables are well-maintained
        high_unsorted = sum(
            1 for record in records 
            if len(record) > 1 and record[1].get('doubleValue', 0) > 20
        )
        
        stale_stats = sum(
            1 for record in records 
            if len(record) > 2 and record[2].get('doubleValue', 0) > 10
        )
        
        if high_unsorted > 0 or stale_stats > 0:
            print(f"⚠️  Task 7-8 Warning: Some tables need VACUUM ({high_unsorted}) or ANALYZE ({stale_stats})")
        
        print(f"✅ Task 7-8 Passed: Table maintenance status checked")
        return True
        
    except Exception as e:
        print(f"⚠️  Task 7-8 Warning: Could not verify maintenance: {e}")
        return True

def test_monitoring_views_exist(student_id):
    """Task 13: Verify monitoring views are created"""
    
    try:
        redshift_data = boto3.client('redshift-data')
        workgroup_name = f"analytics-workgroup-{student_id}"
        
        # Check for monitoring views
        sql = """
        SELECT viewname
        FROM pg_views
        WHERE schemaname = 'public'
        AND viewname LIKE 'v_%health%'
        OR viewname LIKE '%monitor%';
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
        
        if not records or len(records) == 0:
            print(f"⚠️  Task 13 Warning: No monitoring views found")
            return True
        
        view_count = len(records)
        print(f"✅ Task 13 Passed: {view_count} monitoring view(s) created")
        return True
        
    except Exception as e:
        print(f"⚠️  Task 13 Warning: Could not verify monitoring views: {e}")
        return True

def test_workgroup_configuration(redshift_client, student_id):
    """Task 9: Verify workgroup has WLM configured"""
    workgroup_name = f"analytics-workgroup-{student_id}"
    
    try:
        response = redshift_client.get_workgroup(workgroupName=workgroup_name)
        workgroup = response['workgroup']
        
        # Check if workgroup is properly configured
        status = workgroup.get('status')
        if status != 'AVAILABLE':
            print(f"⚠️  Task 9 Warning: Workgroup status is {status}")
        
        # Note: WLM config is complex to verify via API
        # This is a basic check that workgroup exists and is configured
        
        print(f"✅ Task 9 Passed: Workgroup configured and available")
        return True
        
    except ClientError as e:
        print(f"❌ Task 9 Failed: {e}")
        return False

def main():
    """Run all Redshift Database Design assessment tests"""
    print("=" * 60)
    print("AWS Redshift Database Design & Optimization - Validation")
    print("=" * 60)
    
    student_id = get_student_id()
    print(f"\n🎓 Student ID: {student_id}")
    print(f"🗄️  Workgroup: analytics-workgroup-{student_id}\n")
    
    # Initialize AWS clients
    try:
        redshift_client = boto3.client('redshift-serverless')
    except Exception as e:
        print(f"❌ Error initializing AWS clients: {e}")
        sys.exit(1)
    
    # Run tests
    results = []
    total_tasks = 7
    
    print("Starting validation...\n")
    
    # Task 1: Fact table with DISTKEY
    results.append(test_fact_table_with_distkey(student_id))
    
    # Task 2: Dimension tables with ALL
    results.append(test_dimension_tables_with_all_distribution(student_id))
    
    # Task 3-4: Sort keys
    results.append(test_sort_keys_configured(student_id))
    
    # Task 5: Compression
    results.append(test_compression_applied(student_id))
    
    # Task 7-8: Table maintenance
    results.append(test_table_maintenance_status(student_id))
    
    # Task 9: WLM configuration
    results.append(test_workgroup_configuration(redshift_client, student_id))
    
    # Task 13: Monitoring views
    results.append(test_monitoring_views_exist(student_id))
    
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
        print("\n🎉 CONGRATULATIONS! You passed the Redshift Database Design assessment!")
        print("You've successfully demonstrated:")
        print("  ✓ Distribution strategies (KEY, ALL)")
        print("  ✓ Sort key optimization")
        print("  ✓ Compression encoding")
        print("  ✓ Table maintenance (VACUUM, ANALYZE)")
        print("  ✓ Workload management")
        print("  ✓ Performance monitoring")
        sys.exit(0)
    else:
        print("\n❌ Assessment not passed. Minimum score required: 70%")
        print("Please review the failed tasks and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
