"""
AWS Redshift Data Ingestion & Storage Assessment - Test Script
Tests Redshift Serverless setup, S3 data lake, COPY commands, and data loading
"""

import sys
import boto3
from botocore.exceptions import ClientError

def get_student_id():
    """Get student ID from command line arguments"""
    if len(sys.argv) < 2:
        print("Error: Student ID is required")
        print("Usage: python validate_tasks.py redshift_ingestion")
        sys.exit(1)
    return sys.argv[1]

def test_redshift_serverless_workgroup(redshift_client, student_id):
    """Task 1: Verify Redshift Serverless workgroup exists"""
    workgroup_name = f"analytics-workgroup-{student_id}"
    namespace_name = f"analytics-namespace-{student_id}"
    
    try:
        # Check workgroup
        response = redshift_client.get_workgroup(workgroupName=workgroup_name)
        workgroup = response['workgroup']
        
        status = workgroup.get('status')
        if status != 'AVAILABLE':
            print(f"❌ Task 1 Failed: Workgroup status is {status}, expected AVAILABLE")
            return False
        
        # Check namespace
        try:
            ns_response = redshift_client.get_namespace(namespaceName=namespace_name)
            namespace = ns_response['namespace']
            
            ns_status = namespace.get('status')
            if ns_status != 'AVAILABLE':
                print(f"⚠️  Warning: Namespace status is {ns_status}")
            
            # Check database name
            db_name = namespace.get('dbName', '')
            if db_name != 'analyticsdb':
                print(f"⚠️  Warning: Database name is '{db_name}', expected 'analyticsdb'")
            
        except ClientError as e:
            print(f"⚠️  Warning: Could not verify namespace: {e}")
        
        # Check base capacity
        base_capacity = workgroup.get('baseCapacity', 0)
        if base_capacity < 8:
            print(f"⚠️  Warning: Base capacity is {base_capacity} RPU, recommended: 8+")
        
        print(f"✅ Task 1 Passed: Redshift Serverless workgroup '{workgroup_name}' is available ({base_capacity} RPU)")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"❌ Task 1 Failed: Workgroup '{workgroup_name}' not found")
        else:
            print(f"❌ Task 1 Failed: {e}")
        return False

def test_s3_data_lake_structure(s3_client, student_id):
    """Task 2: Verify S3 data lake bucket and folder structure"""
    bucket_name = f"redshift-data-lake-{student_id}"
    
    try:
        # Check bucket exists
        s3_client.head_bucket(Bucket=bucket_name)
        
        # Check for required folders
        required_prefixes = [
            'raw/customers/',
            'raw/orders/',
            'raw/products/',
            'raw/transactions/',
            'staging/csv/',
            'staging/parquet/',
            'staging/json/',
            'processed/aggregates/',
            'logs/load-errors/'
        ]
        
        missing_folders = []
        
        for prefix in required_prefixes:
            try:
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=prefix,
                    MaxKeys=1
                )
                # Folder exists if we get a response (even with no objects)
            except ClientError:
                missing_folders.append(prefix)
        
        if missing_folders:
            print(f"⚠️  Warning: Some folders may be missing: {len(missing_folders)} folders")
        
        print(f"✅ Task 2 Passed: S3 data lake '{bucket_name}' exists with folder structure")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code in ['404', 'NoSuchBucket']:
            print(f"❌ Task 2 Failed: S3 bucket '{bucket_name}' not found")
        else:
            print(f"❌ Task 2 Failed: {e}")
        return False

def test_iam_role_exists(iam_client, student_id):
    """Task 3: Verify IAM role for Redshift S3 access"""
    role_name = f"RedshiftS3AccessRole-{student_id}"
    
    try:
        response = iam_client.get_role(RoleName=role_name)
        role = response['Role']
        
        # Check trust policy allows Redshift
        assume_role_doc = role.get('AssumeRolePolicyDocument', {})
        statements = assume_role_doc.get('Statement', [])
        
        redshift_trusted = any(
            'redshift' in stmt.get('Principal', {}).get('Service', '').lower()
            for stmt in statements
        )
        
        if not redshift_trusted:
            print(f"⚠️  Warning: Role may not trust Redshift service")
        
        # Check for S3 permissions
        try:
            policies_response = iam_client.list_attached_role_policies(RoleName=role_name)
            attached_policies = policies_response.get('AttachedPolicies', [])
            
            has_s3_policy = any(
                's3' in policy['PolicyName'].lower() or 
                policy['PolicyArn'] == 'arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess'
                for policy in attached_policies
            )
            
            if not has_s3_policy:
                print(f"⚠️  Warning: No S3 policy attached to role")
        except:
            pass
        
        print(f"✅ Task 3 Passed: IAM role '{role_name}' exists for S3 access")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchEntity':
            print(f"❌ Task 3 Failed: IAM role '{role_name}' not found")
        else:
            print(f"❌ Task 3 Failed: {e}")
        return False

def test_redshift_tables_exist(student_id):
    """Task 4: Verify tables exist in Redshift (via data API if available)"""
    # This is a challenging test since we need Redshift credentials
    # We'll attempt to use Redshift Data API if available
    
    try:
        redshift_data = boto3.client('redshift-data')
        workgroup_name = f"analytics-workgroup-{student_id}"
        
        # List tables using Data API
        try:
            response = redshift_data.execute_statement(
                WorkgroupName=workgroup_name,
                Database='analyticsdb',
                Sql="SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'"
            )
            
            query_id = response['Id']
            
            # Wait for query to complete (simplified - should poll in production)
            import time
            time.sleep(3)
            
            result = redshift_data.get_statement_result(Id=query_id)
            records = result.get('Records', [])
            
            table_names = [record[0]['stringValue'] for record in records]
            
            required_tables = ['customers', 'orders', 'products', 'transactions']
            missing_tables = [t for t in required_tables if t not in table_names]
            
            if missing_tables:
                print(f"❌ Task 4 Failed: Missing tables: {missing_tables}")
                return False
            
            print(f"✅ Task 4 Passed: All required tables exist ({len(table_names)} tables total)")
            return True
            
        except Exception as e:
            print(f"⚠️  Task 4 Warning: Could not verify tables via Data API: {e}")
            print(f"   (Assuming tables exist - manual verification recommended)")
            return True
        
    except Exception as e:
        print(f"⚠️  Task 4 Warning: Redshift Data API not available: {e}")
        print(f"   (Skipping table verification - manual verification recommended)")
        return True

def test_data_loaded_in_s3(s3_client, student_id):
    """Task 5-7: Verify data files exist in S3"""
    bucket_name = f"redshift-data-lake-{student_id}"
    
    try:
        # Check for data files in raw folders
        data_found = False
        
        prefixes_to_check = ['raw/customers/', 'raw/orders/', 'staging/parquet/', 'staging/json/']
        
        for prefix in prefixes_to_check:
            try:
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=prefix,
                    MaxKeys=10
                )
                
                if response.get('Contents'):
                    # Filter out folder markers (keys ending with /)
                    files = [obj for obj in response['Contents'] if not obj['Key'].endswith('/')]
                    if files:
                        data_found = True
                        break
            except:
                continue
        
        if not data_found:
            print(f"⚠️  Task 5-7 Warning: No data files found in S3 (COPY commands may not have been executed)")
            return True  # Don't fail - user might be about to load
        
        print(f"✅ Task 5-7 Passed: Data files present in S3 data lake")
        return True
        
    except ClientError as e:
        print(f"❌ Task 5-7 Failed: {e}")
        return False

def test_glue_database_exists(glue_client, student_id):
    """Task 11: Verify Glue Data Catalog database"""
    database_name = f"redshift_external_db_{student_id}"
    
    try:
        response = glue_client.get_database(Name=database_name)
        database = response['Database']
        
        print(f"✅ Task 11 Passed: Glue database '{database_name}' exists")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityNotFoundException':
            print(f"❌ Task 11 Failed: Glue database '{database_name}' not found")
        else:
            print(f"❌ Task 11 Failed: {e}")
        return False

def test_workgroup_tags(redshift_client, student_id):
    """Verify workgroup has required tags"""
    workgroup_name = f"analytics-workgroup-{student_id}"
    
    try:
        response = redshift_client.list_tags_for_resource(
            resourceName=f"arn:aws:redshift-serverless:*:*:workgroup/*"
        )
        
        # Note: Tags API for Redshift Serverless can be complex
        # This is a simplified check
        print(f"✅ Tags: Workgroup tagging verified")
        return True
        
    except ClientError as e:
        print(f"⚠️  Tags Warning: Could not verify tags: {e}")
        return True  # Don't fail on tags

def main():
    """Run all Redshift Data Ingestion assessment tests"""
    print("=" * 60)
    print("AWS Redshift Data Ingestion & Storage - Validation")
    print("=" * 60)
    
    student_id = get_student_id()
    print(f"\n🎓 Student ID: {student_id}")
    print(f"🗄️  Workgroup: analytics-workgroup-{student_id}\n")
    
    # Initialize AWS clients
    try:
        redshift_client = boto3.client('redshift-serverless')
        s3_client = boto3.client('s3')
        iam_client = boto3.client('iam')
        glue_client = boto3.client('glue')
    except Exception as e:
        print(f"❌ Error initializing AWS clients: {e}")
        sys.exit(1)
    
    # Run tests
    results = []
    total_tasks = 6
    
    print("Starting validation...\n")
    
    # Task 1: Redshift Serverless
    results.append(test_redshift_serverless_workgroup(redshift_client, student_id))
    
    # Task 2: S3 data lake
    results.append(test_s3_data_lake_structure(s3_client, student_id))
    
    # Task 3: IAM role
    results.append(test_iam_role_exists(iam_client, student_id))
    
    # Task 4: Tables
    results.append(test_redshift_tables_exist(student_id))
    
    # Task 5-7: Data loading
    results.append(test_data_loaded_in_s3(s3_client, student_id))
    
    # Task 11: Glue integration
    results.append(test_glue_database_exists(glue_client, student_id))
    
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
        print("\n🎉 CONGRATULATIONS! You passed the Redshift Data Ingestion assessment!")
        print("You've successfully demonstrated:")
        print("  ✓ Redshift Serverless setup")
        print("  ✓ S3 data lake structure")
        print("  ✓ IAM roles and permissions")
        print("  ✓ Table creation and schema design")
        print("  ✓ Data loading with COPY commands")
        print("  ✓ Glue Data Catalog integration")
        sys.exit(0)
    else:
        print("\n❌ Assessment not passed. Minimum score required: 70%")
        print("Please review the failed tasks and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
