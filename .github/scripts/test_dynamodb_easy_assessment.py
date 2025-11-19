"""
AWS DynamoDB Easy Assessment - Test Script
Tests basic DynamoDB table setup, CRUD operations, and configuration
"""

import sys
import boto3
from botocore.exceptions import ClientError

def get_student_id():
    """Get student ID from command line arguments"""
    if len(sys.argv) < 2:
        print("Error: Student ID is required")
        print("Usage: python validate_tasks.py dynamodb_easy")
        sys.exit(1)
    return sys.argv[1]

def test_table_exists_and_configuration(dynamodb_client, student_id):
    """Task 1: Verify DynamoDB table exists with correct configuration"""
    table_name = f"users-{student_id}"
    try:
        response = dynamodb_client.describe_table(TableName=table_name)
        table = response['Table']
        
        # Check table status
        if table['TableStatus'] != 'ACTIVE':
            print(f"❌ Task 1 Failed: Table {table_name} is not active (status: {table['TableStatus']})")
            return False
        
        # Check partition key
        key_schema = table['KeySchema']
        if len(key_schema) != 1:
            print(f"❌ Task 1 Failed: Table should have only partition key, found {len(key_schema)} keys")
            return False
        
        partition_key = key_schema[0]
        if partition_key['AttributeName'] != 'user_id' or partition_key['KeyType'] != 'HASH':
            print(f"❌ Task 1 Failed: Partition key should be 'user_id' (HASH), found '{partition_key['AttributeName']}' ({partition_key['KeyType']})")
            return False
        
        # Check attribute type
        attributes = table['AttributeDefinitions']
        user_id_attr = next((attr for attr in attributes if attr['AttributeName'] == 'user_id'), None)
        if not user_id_attr or user_id_attr['AttributeType'] != 'S':
            print(f"❌ Task 1 Failed: user_id should be String type (S)")
            return False
        
        # Check billing mode
        billing_mode = table.get('BillingModeSummary', {}).get('BillingMode', 'PROVISIONED')
        if billing_mode != 'PAY_PER_REQUEST':
            print(f"❌ Task 1 Failed: Billing mode should be PAY_PER_REQUEST (on-demand), found {billing_mode}")
            return False
        
        print(f"✅ Task 1 Passed: Table {table_name} exists with correct configuration (partition key: user_id, billing: on-demand)")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"❌ Task 1 Failed: Table {table_name} does not exist")
        else:
            print(f"❌ Task 1 Failed: Error checking table: {e}")
        return False

def test_table_has_items(dynamodb_client, student_id):
    """Task 2: Verify table contains items"""
    table_name = f"users-{student_id}"
    try:
        response = dynamodb_client.scan(
            TableName=table_name,
            Select='COUNT'
        )
        
        item_count = response['Count']
        if item_count < 2:
            print(f"❌ Task 2 Failed: Table should have at least 2 items, found {item_count}")
            return False
        
        # Get actual items to verify structure
        items_response = dynamodb_client.scan(
            TableName=table_name,
            Limit=5
        )
        
        items = items_response.get('Items', [])
        if not items:
            print(f"❌ Task 2 Failed: No items found in table")
            return False
        
        # Check first item has expected attributes
        first_item = items[0]
        required_attrs = ['user_id', 'username', 'email']
        missing_attrs = [attr for attr in required_attrs if attr not in first_item]
        
        if missing_attrs:
            print(f"❌ Task 2 Failed: Items missing required attributes: {missing_attrs}")
            return False
        
        print(f"✅ Task 2 Passed: Table contains {item_count} items with correct structure")
        return True
        
    except ClientError as e:
        print(f"❌ Task 2 Failed: Error scanning table: {e}")
        return False

def test_query_operations(dynamodb_client, student_id):
    """Task 3: Verify query operations work (get item)"""
    table_name = f"users-{student_id}"
    try:
        # First scan to get a valid user_id
        scan_response = dynamodb_client.scan(
            TableName=table_name,
            Limit=1
        )
        
        if not scan_response.get('Items'):
            print(f"❌ Task 3 Failed: No items in table to query")
            return False
        
        test_user_id = scan_response['Items'][0]['user_id']['S']
        
        # Try to get the item
        response = dynamodb_client.get_item(
            TableName=table_name,
            Key={'user_id': {'S': test_user_id}}
        )
        
        if 'Item' not in response:
            print(f"❌ Task 3 Failed: Could not retrieve item with user_id: {test_user_id}")
            return False
        
        item = response['Item']
        if 'user_id' not in item or item['user_id']['S'] != test_user_id:
            print(f"❌ Task 3 Failed: Retrieved item does not match queried user_id")
            return False
        
        print(f"✅ Task 3 Passed: Query operations work correctly (retrieved user_id: {test_user_id})")
        return True
        
    except ClientError as e:
        print(f"❌ Task 3 Failed: Error performing query: {e}")
        return False

def test_pitr_enabled(dynamodb_client, student_id):
    """Task 6: Verify Point-in-Time Recovery is enabled"""
    table_name = f"users-{student_id}"
    try:
        response = dynamodb_client.describe_continuous_backups(
            TableName=table_name
        )
        
        pitr_status = response['ContinuousBackupsDescription']['PointInTimeRecoveryDescription']['PointInTimeRecoveryStatus']
        
        if pitr_status != 'ENABLED':
            print(f"❌ Task 6 Failed: Point-in-Time Recovery is not enabled (status: {pitr_status})")
            return False
        
        print(f"✅ Task 6 Passed: Point-in-Time Recovery is enabled")
        return True
        
    except ClientError as e:
        print(f"❌ Task 6 Failed: Error checking PITR: {e}")
        return False

def test_table_tags(dynamodb_client, student_id):
    """Verify table has required tags"""
    table_name = f"users-{student_id}"
    try:
        response = dynamodb_client.describe_table(TableName=table_name)
        table_arn = response['Table']['TableArn']
        
        tags_response = dynamodb_client.list_tags_of_resource(ResourceArn=table_arn)
        tags = {tag['Key']: tag['Value'] for tag in tags_response.get('Tags', [])}
        
        required_tags = {
            'Environment': 'Development',
            'Application': 'UserManagement',
            'StudentID': student_id
        }
        
        missing_tags = []
        incorrect_tags = []
        
        for key, expected_value in required_tags.items():
            if key not in tags:
                missing_tags.append(key)
            elif tags[key] != expected_value:
                incorrect_tags.append(f"{key}={tags[key]} (expected: {expected_value})")
        
        if missing_tags:
            print(f"❌ Tags Failed: Missing required tags: {missing_tags}")
            return False
        
        if incorrect_tags:
            print(f"❌ Tags Failed: Incorrect tag values: {incorrect_tags}")
            return False
        
        print(f"✅ Tags Passed: All required tags are present and correct")
        return True
        
    except ClientError as e:
        print(f"❌ Tags Failed: Error checking tags: {e}")
        return False

def test_table_accessibility(dynamodb_client, student_id):
    """Task 8: Verify table is accessible and operational"""
    table_name = f"users-{student_id}"
    try:
        # Try a simple describe operation
        response = dynamodb_client.describe_table(TableName=table_name)
        
        # Check table class
        table_class = response['Table'].get('TableClassSummary', {}).get('TableClass', 'STANDARD')
        if table_class != 'STANDARD':
            print(f"⚠️  Warning: Table class is {table_class}, expected STANDARD")
        
        # Try a simple scan to verify read access
        scan_response = dynamodb_client.scan(
            TableName=table_name,
            Limit=1
        )
        
        print(f"✅ Task 8 Passed: Table is accessible and operational")
        return True
        
    except ClientError as e:
        print(f"❌ Task 8 Failed: Table is not accessible: {e}")
        return False

def main():
    """Run all DynamoDB easy assessment tests"""
    print("=" * 60)
    print("AWS DynamoDB Easy Assessment - Validation")
    print("=" * 60)
    
    student_id = get_student_id()
    print(f"\n🎓 Student ID: {student_id}")
    print(f"📊 Table Name: users-{student_id}\n")
    
    # Initialize AWS clients
    try:
        dynamodb_client = boto3.client('dynamodb')
    except Exception as e:
        print(f"❌ Error initializing AWS clients: {e}")
        print("Make sure AWS credentials are configured")
        sys.exit(1)
    
    # Run tests
    results = []
    total_tasks = 6
    
    print("Starting validation...\n")
    
    # Task 1: Table configuration
    results.append(test_table_exists_and_configuration(dynamodb_client, student_id))
    
    # Task 2: Items in table
    results.append(test_table_has_items(dynamodb_client, student_id))
    
    # Task 3: Query operations
    results.append(test_query_operations(dynamodb_client, student_id))
    
    # Task 6: PITR enabled
    results.append(test_pitr_enabled(dynamodb_client, student_id))
    
    # Tags
    results.append(test_table_tags(dynamodb_client, student_id))
    
    # Task 8: Accessibility
    results.append(test_table_accessibility(dynamodb_client, student_id))
    
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
        print("\n🎉 CONGRATULATIONS! You passed the DynamoDB Easy assessment!")
        print("You've successfully demonstrated basic DynamoDB skills:")
        print("  ✓ Table creation and configuration")
        print("  ✓ Adding and querying items")
        print("  ✓ Backup configuration (PITR)")
        print("  ✓ Resource tagging")
        sys.exit(0)
    else:
        print("\n❌ Assessment not passed. Minimum score required: 70%")
        print("Please review the failed tasks and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
