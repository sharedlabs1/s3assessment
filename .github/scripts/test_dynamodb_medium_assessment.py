"""
AWS DynamoDB Medium Assessment - Test Script
Tests advanced DynamoDB features: GSI, LSI, Streams, Lambda, TTL, CloudWatch
"""

import sys
import boto3
from botocore.exceptions import ClientError

def get_student_id():
    """Get student ID from command line arguments"""
    if len(sys.argv) < 2:
        print("Error: Student ID is required")
        print("Usage: python validate_tasks.py dynamodb_medium")
        sys.exit(1)
    return sys.argv[1]

def test_table_with_composite_key(dynamodb_client, student_id):
    """Task 1: Verify table exists with partition and sort key"""
    table_name = f"orders-{student_id}"
    try:
        response = dynamodb_client.describe_table(TableName=table_name)
        table = response['Table']
        
        # Check table status
        if table['TableStatus'] != 'ACTIVE':
            print(f"❌ Task 1 Failed: Table {table_name} is not active")
            return False
        
        # Check key schema (should have 2 keys)
        key_schema = table['KeySchema']
        if len(key_schema) != 2:
            print(f"❌ Task 1 Failed: Table should have partition and sort key, found {len(key_schema)} keys")
            return False
        
        # Verify partition key
        partition_key = next((k for k in key_schema if k['KeyType'] == 'HASH'), None)
        if not partition_key or partition_key['AttributeName'] != 'customer_id':
            print(f"❌ Task 1 Failed: Partition key should be 'customer_id'")
            return False
        
        # Verify sort key
        sort_key = next((k for k in key_schema if k['KeyType'] == 'RANGE'), None)
        if not sort_key or sort_key['AttributeName'] != 'order_id':
            print(f"❌ Task 1 Failed: Sort key should be 'order_id'")
            return False
        
        # Check billing mode
        billing_mode = table.get('BillingModeSummary', {}).get('BillingMode', 'PROVISIONED')
        if billing_mode != 'PAY_PER_REQUEST':
            print(f"❌ Task 1 Failed: Billing mode should be PAY_PER_REQUEST")
            return False
        
        print(f"✅ Task 1 Passed: Table with composite key (customer_id, order_id)")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"❌ Task 1 Failed: Table {table_name} does not exist")
        else:
            print(f"❌ Task 1 Failed: {e}")
        return False

def test_global_secondary_index(dynamodb_client, student_id):
    """Task 2: Verify GSI exists with correct configuration"""
    table_name = f"orders-{student_id}"
    try:
        response = dynamodb_client.describe_table(TableName=table_name)
        table = response['Table']
        
        gsi_list = table.get('GlobalSecondaryIndexes', [])
        if not gsi_list:
            print(f"❌ Task 2 Failed: No Global Secondary Indexes found")
            return False
        
        # Find StatusDateIndex
        status_index = next((idx for idx in gsi_list if idx['IndexName'] == 'StatusDateIndex'), None)
        if not status_index:
            print(f"❌ Task 2 Failed: GSI 'StatusDateIndex' not found")
            return False
        
        # Check index status
        if status_index['IndexStatus'] != 'ACTIVE':
            print(f"❌ Task 2 Failed: StatusDateIndex is not active")
            return False
        
        # Check key schema
        index_keys = status_index['KeySchema']
        partition_key = next((k for k in index_keys if k['KeyType'] == 'HASH'), None)
        sort_key = next((k for k in index_keys if k['KeyType'] == 'RANGE'), None)
        
        if not partition_key or partition_key['AttributeName'] != 'status':
            print(f"❌ Task 2 Failed: GSI partition key should be 'status'")
            return False
        
        if not sort_key or sort_key['AttributeName'] != 'order_date':
            print(f"❌ Task 2 Failed: GSI sort key should be 'order_date'")
            return False
        
        # Check projection
        projection = status_index.get('Projection', {}).get('ProjectionType', '')
        if projection != 'ALL':
            print(f"⚠️  Warning: GSI projection is {projection}, recommended: ALL")
        
        print(f"✅ Task 2 Passed: GSI 'StatusDateIndex' (status, order_date)")
        return True
        
    except ClientError as e:
        print(f"❌ Task 2 Failed: {e}")
        return False

def test_local_secondary_index(dynamodb_client, student_id):
    """Task 3: Verify LSI exists with correct configuration"""
    table_name = f"orders-{student_id}"
    try:
        response = dynamodb_client.describe_table(TableName=table_name)
        table = response['Table']
        
        lsi_list = table.get('LocalSecondaryIndexes', [])
        if not lsi_list:
            print(f"❌ Task 3 Failed: No Local Secondary Indexes found")
            return False
        
        # Find CustomerAmountIndex
        amount_index = next((idx for idx in lsi_list if idx['IndexName'] == 'CustomerAmountIndex'), None)
        if not amount_index:
            print(f"❌ Task 3 Failed: LSI 'CustomerAmountIndex' not found")
            return False
        
        # Check key schema
        index_keys = amount_index['KeySchema']
        partition_key = next((k for k in index_keys if k['KeyType'] == 'HASH'), None)
        sort_key = next((k for k in index_keys if k['KeyType'] == 'RANGE'), None)
        
        if not partition_key or partition_key['AttributeName'] != 'customer_id':
            print(f"❌ Task 3 Failed: LSI partition key should be 'customer_id'")
            return False
        
        if not sort_key or sort_key['AttributeName'] != 'total_amount':
            print(f"❌ Task 3 Failed: LSI sort key should be 'total_amount'")
            return False
        
        print(f"✅ Task 3 Passed: LSI 'CustomerAmountIndex' (customer_id, total_amount)")
        return True
        
    except ClientError as e:
        print(f"❌ Task 3 Failed: {e}")
        return False

def test_table_has_items(dynamodb_client, student_id):
    """Task 4: Verify table has sufficient items"""
    table_name = f"orders-{student_id}"
    try:
        response = dynamodb_client.scan(
            TableName=table_name,
            Select='COUNT'
        )
        
        item_count = response['Count']
        if item_count < 15:
            print(f"❌ Task 4 Failed: Table should have at least 15 items, found {item_count}")
            return False
        
        print(f"✅ Task 4 Passed: Table contains {item_count} orders")
        return True
        
    except ClientError as e:
        print(f"❌ Task 4 Failed: {e}")
        return False

def test_streams_enabled(dynamodb_client, student_id):
    """Task 7: Verify DynamoDB Streams is enabled"""
    table_name = f"orders-{student_id}"
    try:
        response = dynamodb_client.describe_table(TableName=table_name)
        table = response['Table']
        
        stream_spec = table.get('StreamSpecification', {})
        
        if not stream_spec.get('StreamEnabled', False):
            print(f"❌ Task 7 Failed: DynamoDB Streams is not enabled")
            return False
        
        stream_view_type = stream_spec.get('StreamViewType', '')
        if stream_view_type != 'NEW_AND_OLD_IMAGES':
            print(f"❌ Task 7 Failed: Stream view type should be NEW_AND_OLD_IMAGES, found {stream_view_type}")
            return False
        
        # Check if stream ARN exists
        stream_arn = table.get('LatestStreamArn', '')
        if not stream_arn:
            print(f"❌ Task 7 Failed: Stream ARN not found")
            return False
        
        print(f"✅ Task 7 Passed: DynamoDB Streams enabled (NEW_AND_OLD_IMAGES)")
        return True
        
    except ClientError as e:
        print(f"❌ Task 7 Failed: {e}")
        return False

def test_lambda_stream_trigger(lambda_client, dynamodb_client, student_id):
    """Task 8: Verify Lambda function exists and is connected to stream"""
    function_name = f"process-orders-stream-{student_id}"
    table_name = f"orders-{student_id}"
    
    try:
        # Check if Lambda function exists
        try:
            lambda_response = lambda_client.get_function(FunctionName=function_name)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"❌ Task 8 Failed: Lambda function '{function_name}' not found")
                return False
            raise
        
        # Get table stream ARN
        table_response = dynamodb_client.describe_table(TableName=table_name)
        stream_arn = table_response['Table'].get('LatestStreamArn', '')
        
        if not stream_arn:
            print(f"❌ Task 8 Failed: Table has no stream ARN")
            return False
        
        # Check event source mappings
        mappings = lambda_client.list_event_source_mappings(
            FunctionName=function_name,
            EventSourceArn=stream_arn
        )
        
        if not mappings.get('EventSourceMappings'):
            print(f"❌ Task 8 Failed: No event source mapping found between Lambda and DynamoDB stream")
            return False
        
        mapping = mappings['EventSourceMappings'][0]
        if mapping['State'] not in ['Enabled', 'Enabling']:
            print(f"❌ Task 8 Failed: Event source mapping is not enabled (state: {mapping['State']})")
            return False
        
        print(f"✅ Task 8 Passed: Lambda function connected to DynamoDB stream")
        return True
        
    except ClientError as e:
        print(f"❌ Task 8 Failed: {e}")
        return False

def test_ttl_enabled(dynamodb_client, student_id):
    """Task 10: Verify Time To Live is enabled"""
    table_name = f"orders-{student_id}"
    try:
        response = dynamodb_client.describe_time_to_live(TableName=table_name)
        
        ttl_status = response['TimeToLiveDescription']['TimeToLiveStatus']
        
        if ttl_status not in ['ENABLED', 'ENABLING']:
            print(f"❌ Task 10 Failed: TTL is not enabled (status: {ttl_status})")
            return False
        
        ttl_attribute = response['TimeToLiveDescription'].get('AttributeName', '')
        if ttl_attribute != 'expiry_date':
            print(f"❌ Task 10 Failed: TTL attribute should be 'expiry_date', found '{ttl_attribute}'")
            return False
        
        print(f"✅ Task 10 Passed: TTL enabled on 'expiry_date' attribute")
        return True
        
    except ClientError as e:
        print(f"❌ Task 10 Failed: {e}")
        return False

def test_cloudwatch_alarms(cloudwatch_client, student_id):
    """Task 11: Verify CloudWatch alarms exist"""
    table_name = f"orders-{student_id}"
    
    try:
        # List all alarms
        response = cloudwatch_client.describe_alarms()
        alarms = response.get('MetricAlarms', [])
        
        # Filter alarms related to this table
        table_alarms = [
            alarm for alarm in alarms 
            if table_name in alarm.get('AlarmName', '') or 
               any(dim.get('Value') == table_name for dim in alarm.get('Dimensions', []))
        ]
        
        if len(table_alarms) < 1:
            print(f"❌ Task 11 Failed: No CloudWatch alarms found for table {table_name}")
            print(f"   Create at least one alarm for throttling or errors")
            return False
        
        print(f"✅ Task 11 Passed: {len(table_alarms)} CloudWatch alarm(s) configured")
        return True
        
    except ClientError as e:
        print(f"❌ Task 11 Failed: {e}")
        return False

def test_table_tags(dynamodb_client, student_id):
    """Verify table has required tags"""
    table_name = f"orders-{student_id}"
    try:
        response = dynamodb_client.describe_table(TableName=table_name)
        table_arn = response['Table']['TableArn']
        
        tags_response = dynamodb_client.list_tags_of_resource(ResourceArn=table_arn)
        tags = {tag['Key']: tag['Value'] for tag in tags_response.get('Tags', [])}
        
        required_tags = {
            'Environment': 'Production',
            'Application': 'OrderManagement',
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
    """Run all DynamoDB medium assessment tests"""
    print("=" * 60)
    print("AWS DynamoDB Medium Assessment - Validation")
    print("=" * 60)
    
    student_id = get_student_id()
    print(f"\n🎓 Student ID: {student_id}")
    print(f"📊 Table Name: orders-{student_id}\n")
    
    # Initialize AWS clients
    try:
        dynamodb_client = boto3.client('dynamodb')
        lambda_client = boto3.client('lambda')
        cloudwatch_client = boto3.client('cloudwatch')
    except Exception as e:
        print(f"❌ Error initializing AWS clients: {e}")
        sys.exit(1)
    
    # Run tests
    results = []
    total_tasks = 9
    
    print("Starting validation...\n")
    
    # Task 1: Composite key
    results.append(test_table_with_composite_key(dynamodb_client, student_id))
    
    # Task 2: GSI
    results.append(test_global_secondary_index(dynamodb_client, student_id))
    
    # Task 3: LSI
    results.append(test_local_secondary_index(dynamodb_client, student_id))
    
    # Task 4: Items
    results.append(test_table_has_items(dynamodb_client, student_id))
    
    # Task 7: Streams
    results.append(test_streams_enabled(dynamodb_client, student_id))
    
    # Task 8: Lambda trigger
    results.append(test_lambda_stream_trigger(lambda_client, dynamodb_client, student_id))
    
    # Task 10: TTL
    results.append(test_ttl_enabled(dynamodb_client, student_id))
    
    # Task 11: CloudWatch alarms
    results.append(test_cloudwatch_alarms(cloudwatch_client, student_id))
    
    # Tags
    results.append(test_table_tags(dynamodb_client, student_id))
    
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
        print("\n🎉 CONGRATULATIONS! You passed the DynamoDB Medium assessment!")
        print("You've successfully demonstrated advanced DynamoDB skills:")
        print("  ✓ Composite keys (partition + sort)")
        print("  ✓ Global Secondary Indexes (GSI)")
        print("  ✓ Local Secondary Indexes (LSI)")
        print("  ✓ DynamoDB Streams for change capture")
        print("  ✓ Lambda stream processing")
        print("  ✓ Time To Live (TTL)")
        print("  ✓ CloudWatch monitoring")
        sys.exit(0)
    else:
        print("\n❌ Assessment not passed. Minimum score required: 70%")
        print("Please review the failed tasks and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
