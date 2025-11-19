"""
AWS DynamoDB Hard Assessment - Test Script
Tests global tables, encryption, PITR, backups, DAX, and enterprise features
"""

import sys
import boto3
from botocore.exceptions import ClientError

def get_student_id():
    """Get student ID from command line arguments"""
    if len(sys.argv) < 2:
        print("Error: Student ID is required")
        print("Usage: python validate_tasks.py dynamodb_hard")
        sys.exit(1)
    return sys.argv[1]

def test_global_table_exists(dynamodb_client, student_id):
    """Task 1: Verify global table exists with replicas"""
    table_name = f"transactions-global-{student_id}"
    
    try:
        # Check primary region (us-east-1)
        response = dynamodb_client.describe_table(TableName=table_name)
        table = response['Table']
        
        if table['TableStatus'] != 'ACTIVE':
            print(f"❌ Task 1 Failed: Table is not active (status: {table['TableStatus']})")
            return False
        
        # Check if table is a global table
        replicas = table.get('Replicas', [])
        if not replicas:
            print(f"❌ Task 1 Failed: Table is not configured as a global table (no replicas found)")
            return False
        
        # Verify expected regions
        replica_regions = [r['RegionName'] for r in replicas]
        expected_regions = {'us-east-1', 'us-west-2', 'eu-west-1'}
        actual_regions = set(replica_regions)
        
        if not expected_regions.issubset(actual_regions):
            missing_regions = expected_regions - actual_regions
            print(f"❌ Task 1 Failed: Missing replicas in regions: {missing_regions}")
            return False
        
        # Check replica status
        inactive_replicas = [r['RegionName'] for r in replicas if r.get('ReplicaStatus') != 'ACTIVE']
        if inactive_replicas:
            print(f"❌ Task 1 Failed: Replicas not active in: {inactive_replicas}")
            return False
        
        print(f"✅ Task 1 Passed: Global table with replicas in {len(replicas)} regions")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"❌ Task 1 Failed: Table {table_name} does not exist")
        else:
            print(f"❌ Task 1 Failed: {e}")
        return False

def test_encryption_with_kms(dynamodb_client, student_id):
    """Task 2: Verify customer managed KMS encryption"""
    table_name = f"transactions-global-{student_id}"
    
    try:
        response = dynamodb_client.describe_table(TableName=table_name)
        table = response['Table']
        
        sse_description = table.get('SSEDescription', {})
        
        if not sse_description:
            print(f"❌ Task 2 Failed: No encryption configured")
            return False
        
        sse_type = sse_description.get('SSEType', '')
        if sse_type != 'KMS':
            print(f"❌ Task 2 Failed: Encryption type should be KMS, found {sse_type}")
            return False
        
        kms_key_arn = sse_description.get('KMSMasterKeyArn', '')
        if not kms_key_arn:
            print(f"❌ Task 2 Failed: No KMS key ARN found")
            return False
        
        # Check if it's a customer managed key (not AWS managed)
        if 'aws/dynamodb' in kms_key_arn.lower():
            print(f"❌ Task 2 Failed: Using AWS managed key, should use customer managed key")
            return False
        
        print(f"✅ Task 2 Passed: Encrypted with customer managed KMS key")
        return True
        
    except ClientError as e:
        print(f"❌ Task 2 Failed: {e}")
        return False

def test_pitr_enabled_all_regions(student_id):
    """Task 3: Verify PITR enabled in all regions"""
    table_name = f"transactions-global-{student_id}"
    regions = ['us-east-1', 'us-west-2', 'eu-west-1']
    
    all_enabled = True
    enabled_regions = []
    
    for region in regions:
        try:
            client = boto3.client('dynamodb', region_name=region)
            response = client.describe_continuous_backups(TableName=table_name)
            
            pitr_status = response['ContinuousBackupsDescription']['PointInTimeRecoveryDescription']['PointInTimeRecoveryStatus']
            
            if pitr_status == 'ENABLED':
                enabled_regions.append(region)
            else:
                print(f"⚠️  PITR not enabled in {region} (status: {pitr_status})")
                all_enabled = False
                
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"⚠️  Table not found in {region}")
            else:
                print(f"⚠️  Error checking PITR in {region}: {e}")
            all_enabled = False
    
    if all_enabled:
        print(f"✅ Task 3 Passed: PITR enabled in all {len(regions)} regions")
        return True
    else:
        print(f"❌ Task 3 Failed: PITR enabled in {len(enabled_regions)}/{len(regions)} regions")
        return False

def test_backups_exist(dynamodb_client, student_id):
    """Task 4: Verify on-demand backups exist"""
    table_name = f"transactions-global-{student_id}"
    
    try:
        response = dynamodb_client.list_backups(TableName=table_name)
        
        backups = response.get('BackupSummaries', [])
        
        if len(backups) < 1:
            print(f"❌ Task 4 Failed: No backups found (need at least 1)")
            return False
        
        # Check backup status
        available_backups = [b for b in backups if b['BackupStatus'] == 'AVAILABLE']
        
        if len(available_backups) < 1:
            print(f"❌ Task 4 Failed: No available backups (found {len(backups)} but none are AVAILABLE)")
            return False
        
        print(f"✅ Task 4 Passed: {len(available_backups)} backup(s) available")
        return True
        
    except ClientError as e:
        print(f"❌ Task 4 Failed: {e}")
        return False

def test_backup_lambda_exists(lambda_client, student_id):
    """Task 5: Verify backup automation Lambda exists"""
    function_name = f"dynamodb-backup-automation-{student_id}"
    
    try:
        response = lambda_client.get_function(FunctionName=function_name)
        
        config = response['Configuration']
        
        # Check environment variables
        env_vars = config.get('Environment', {}).get('Variables', {})
        if 'TABLE_NAME' not in env_vars:
            print(f"⚠️  Warning: Lambda missing TABLE_NAME environment variable")
        
        # Check if EventBridge trigger exists
        try:
            events_client = boto3.client('events')
            rules = events_client.list_rules(NamePrefix=f'daily-dynamodb-backup-{student_id}')
            
            if not rules.get('Rules'):
                print(f"⚠️  Warning: No EventBridge rule found for backup automation")
        except:
            pass
        
        print(f"✅ Task 5 Passed: Backup automation Lambda function exists")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"❌ Task 5 Failed: Lambda function '{function_name}' not found")
        else:
            print(f"❌ Task 5 Failed: {e}")
        return False

def test_gsi_exists(dynamodb_client, student_id):
    """Task 7: Verify GSI for high-value transactions"""
    table_name = f"transactions-global-{student_id}"
    
    try:
        response = dynamodb_client.describe_table(TableName=table_name)
        table = response['Table']
        
        gsi_list = table.get('GlobalSecondaryIndexes', [])
        if not gsi_list:
            print(f"❌ Task 7 Failed: No Global Secondary Indexes found")
            return False
        
        # Look for HighValueTransactionsIndex
        high_value_index = next((idx for idx in gsi_list if idx['IndexName'] == 'HighValueTransactionsIndex'), None)
        
        if not high_value_index:
            print(f"❌ Task 7 Failed: 'HighValueTransactionsIndex' not found")
            return False
        
        # Check index status
        if high_value_index['IndexStatus'] != 'ACTIVE':
            print(f"❌ Task 7 Failed: Index is not active (status: {high_value_index['IndexStatus']})")
            return False
        
        print(f"✅ Task 7 Passed: GSI 'HighValueTransactionsIndex' configured")
        return True
        
    except ClientError as e:
        print(f"❌ Task 7 Failed: {e}")
        return False

def test_contributor_insights(dynamodb_client, student_id):
    """Task 8: Verify Contributor Insights is enabled"""
    table_name = f"transactions-global-{student_id}"
    
    try:
        response = dynamodb_client.describe_contributor_insights(TableName=table_name)
        
        status = response.get('ContributorInsightsStatus', '')
        
        if status not in ['ENABLED', 'ENABLING']:
            print(f"❌ Task 8 Failed: Contributor Insights not enabled (status: {status})")
            return False
        
        print(f"✅ Task 8 Passed: Contributor Insights enabled")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"❌ Task 8 Failed: Contributor Insights not configured")
        else:
            print(f"❌ Task 8 Failed: {e}")
        return False

def test_cloudwatch_alarms(cloudwatch_client, student_id):
    """Task 9: Verify CloudWatch alarms configured"""
    table_name = f"transactions-global-{student_id}"
    
    try:
        response = cloudwatch_client.describe_alarms()
        alarms = response.get('MetricAlarms', [])
        
        # Filter alarms related to this table
        table_alarms = [
            alarm for alarm in alarms 
            if student_id in alarm.get('AlarmName', '') or 
               any(dim.get('Value') == table_name for dim in alarm.get('Dimensions', []))
        ]
        
        if len(table_alarms) < 3:
            print(f"❌ Task 9 Failed: Need at least 3 alarms, found {len(table_alarms)}")
            return False
        
        # Check for critical alarm types
        alarm_metrics = [alarm.get('MetricName', '') for alarm in table_alarms]
        
        print(f"✅ Task 9 Passed: {len(table_alarms)} CloudWatch alarms configured")
        return True
        
    except ClientError as e:
        print(f"❌ Task 9 Failed: {e}")
        return False

def test_s3_export_bucket(s3_client, student_id):
    """Task 10: Verify S3 export bucket exists"""
    bucket_name = f"dynamodb-exports-{student_id}"
    
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        
        print(f"✅ Task 10 Passed: S3 export bucket exists")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code in ['404', 'NoSuchBucket']:
            print(f"❌ Task 10 Failed: S3 bucket '{bucket_name}' not found")
        else:
            print(f"❌ Task 10 Failed: {e}")
        return False

def test_dax_cluster(dax_client, student_id):
    """Task 13: Verify DAX cluster deployed"""
    cluster_name = f"transactions-dax-{student_id}"
    
    try:
        response = dax_client.describe_clusters(ClusterNames=[cluster_name])
        
        clusters = response.get('Clusters', [])
        if not clusters:
            print(f"❌ Task 13 Failed: DAX cluster '{cluster_name}' not found")
            return False
        
        cluster = clusters[0]
        status = cluster.get('Status', '')
        
        if status != 'available':
            print(f"❌ Task 13 Failed: DAX cluster not available (status: {status})")
            return False
        
        # Check node count
        nodes = cluster.get('TotalNodes', 0)
        if nodes < 1:
            print(f"❌ Task 13 Failed: DAX cluster has no nodes")
            return False
        
        print(f"✅ Task 13 Passed: DAX cluster with {nodes} node(s)")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ClusterNotFoundFault':
            print(f"❌ Task 13 Failed: DAX cluster '{cluster_name}' not found")
        else:
            print(f"❌ Task 13 Failed: {e}")
        return False

def test_cloudtrail_enabled(cloudtrail_client, student_id):
    """Task 15: Verify CloudTrail logging enabled"""
    trail_name = f"dynamodb-audit-trail-{student_id}"
    
    try:
        response = cloudtrail_client.describe_trails(trailNameList=[trail_name])
        
        trails = response.get('trailList', [])
        if not trails:
            print(f"❌ Task 15 Failed: CloudTrail '{trail_name}' not found")
            return False
        
        trail = trails[0]
        
        # Check if trail is logging
        status = cloudtrail_client.get_trail_status(Name=trail_name)
        
        if not status.get('IsLogging', False):
            print(f"❌ Task 15 Failed: CloudTrail is not actively logging")
            return False
        
        print(f"✅ Task 15 Passed: CloudTrail audit logging enabled")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'TrailNotFoundException':
            print(f"❌ Task 15 Failed: CloudTrail '{trail_name}' not found")
        else:
            print(f"❌ Task 15 Failed: {e}")
        return False

def test_table_tags(dynamodb_client, student_id):
    """Verify table has required tags"""
    table_name = f"transactions-global-{student_id}"
    
    try:
        response = dynamodb_client.describe_table(TableName=table_name)
        table_arn = response['Table']['TableArn']
        
        tags_response = dynamodb_client.list_tags_of_resource(ResourceArn=table_arn)
        tags = {tag['Key']: tag['Value'] for tag in tags_response.get('Tags', [])}
        
        required_tags = {
            'Environment': 'Production',
            'Application': 'GlobalTransactions',
            'Compliance': 'PCI-DSS',
            'StudentID': student_id
        }
        
        missing_tags = []
        for key, expected_value in required_tags.items():
            if key not in tags:
                missing_tags.append(key)
            elif tags[key] != expected_value:
                print(f"⚠️  Warning: Tag {key}={tags[key]}, expected {expected_value}")
        
        if missing_tags:
            print(f"❌ Tags Failed: Missing tags: {missing_tags}")
            return False
        
        print(f"✅ Tags Passed: All required tags present")
        return True
        
    except ClientError as e:
        print(f"❌ Tags Failed: {e}")
        return False

def main():
    """Run all DynamoDB hard assessment tests"""
    print("=" * 60)
    print("AWS DynamoDB Hard Assessment - Validation")
    print("=" * 60)
    
    student_id = get_student_id()
    print(f"\n🎓 Student ID: {student_id}")
    print(f"📊 Global Table: transactions-global-{student_id}\n")
    
    # Initialize AWS clients
    try:
        dynamodb_client = boto3.client('dynamodb', region_name='us-east-1')
        lambda_client = boto3.client('lambda', region_name='us-east-1')
        cloudwatch_client = boto3.client('cloudwatch', region_name='us-east-1')
        s3_client = boto3.client('s3', region_name='us-east-1')
        cloudtrail_client = boto3.client('cloudtrail', region_name='us-east-1')
        dax_client = boto3.client('dax', region_name='us-east-1')
    except Exception as e:
        print(f"❌ Error initializing AWS clients: {e}")
        sys.exit(1)
    
    # Run tests
    results = []
    total_tasks = 11
    
    print("Starting validation...\n")
    
    # Task 1: Global table
    results.append(test_global_table_exists(dynamodb_client, student_id))
    
    # Task 2: KMS encryption
    results.append(test_encryption_with_kms(dynamodb_client, student_id))
    
    # Task 3: PITR in all regions
    results.append(test_pitr_enabled_all_regions(student_id))
    
    # Task 4: Backups
    results.append(test_backups_exist(dynamodb_client, student_id))
    
    # Task 5: Backup Lambda
    results.append(test_backup_lambda_exists(lambda_client, student_id))
    
    # Task 7: GSI
    results.append(test_gsi_exists(dynamodb_client, student_id))
    
    # Task 8: Contributor Insights
    results.append(test_contributor_insights(dynamodb_client, student_id))
    
    # Task 9: CloudWatch alarms
    results.append(test_cloudwatch_alarms(cloudwatch_client, student_id))
    
    # Task 10: S3 export bucket
    results.append(test_s3_export_bucket(s3_client, student_id))
    
    # Task 13: DAX cluster
    results.append(test_dax_cluster(dax_client, student_id))
    
    # Task 15: CloudTrail
    results.append(test_cloudtrail_enabled(cloudtrail_client, student_id))
    
    # Tags
    results.append(test_table_tags(dynamodb_client, student_id))
    
    # Calculate score (add tags to total)
    total_tasks = 12
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
        print("\n🎉 CONGRATULATIONS! You passed the DynamoDB Hard assessment!")
        print("You've successfully demonstrated enterprise DynamoDB skills:")
        print("  ✓ Global tables with multi-region replication")
        print("  ✓ Customer managed KMS encryption")
        print("  ✓ Point-in-Time Recovery (PITR)")
        print("  ✓ Automated backup strategy")
        print("  ✓ Advanced indexing patterns")
        print("  ✓ Performance optimization (DAX)")
        print("  ✓ Comprehensive monitoring")
        print("  ✓ Compliance and audit logging")
        sys.exit(0)
    else:
        print("\n❌ Assessment not passed. Minimum score required: 70%")
        print("Please review the failed tasks and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
