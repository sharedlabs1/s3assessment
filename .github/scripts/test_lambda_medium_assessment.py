"""
AWS Lambda Medium Assessment - Test Script
Tests layers, VPC config, destinations, SQS triggers, DLQ, concurrency, aliases
"""

import sys
import boto3
from botocore.exceptions import ClientError

def get_student_id():
    """Get student ID from command line arguments"""
    if len(sys.argv) < 2:
        print("Error: Student ID is required")
        print("Usage: python validate_tasks.py lambda_medium")
        sys.exit(1)
    return sys.argv[1]

def test_lambda_layer_exists(lambda_client, student_id):
    """Task 1: Verify Lambda layer exists"""
    layer_name = f"common-utils-layer-{student_id}"
    
    try:
        response = lambda_client.list_layer_versions(LayerName=layer_name)
        
        layer_versions = response.get('LayerVersions', [])
        if not layer_versions:
            print(f"❌ Task 1 Failed: No versions found for layer '{layer_name}'")
            return False
        
        latest_version = layer_versions[0]
        compatible_runtimes = latest_version.get('CompatibleRuntimes', [])
        
        if not any('python3' in runtime for runtime in compatible_runtimes):
            print(f"⚠️  Warning: Layer may not be compatible with Python 3")
        
        print(f"✅ Task 1 Passed: Lambda layer '{layer_name}' exists (version {latest_version['Version']})")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"❌ Task 1 Failed: Lambda layer '{layer_name}' not found")
        else:
            print(f"❌ Task 1 Failed: {e}")
        return False

def test_layer_consumer_function(lambda_client, student_id):
    """Task 2: Verify function uses layer"""
    function_name = f"layer-consumer-{student_id}"
    layer_name = f"common-utils-layer-{student_id}"
    
    try:
        response = lambda_client.get_function(FunctionName=function_name)
        config = response['Configuration']
        
        layers = config.get('Layers', [])
        if not layers:
            print(f"❌ Task 2 Failed: Function has no layers configured")
            return False
        
        # Check if our layer is used
        layer_arns = [layer['Arn'] for layer in layers]
        layer_found = any(layer_name in arn for arn in layer_arns)
        
        if not layer_found:
            print(f"❌ Task 2 Failed: Function does not use layer '{layer_name}'")
            return False
        
        print(f"✅ Task 2 Passed: Function uses layer (total layers: {len(layers)})")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"❌ Task 2 Failed: Function '{function_name}' not found")
        else:
            print(f"❌ Task 2 Failed: {e}")
        return False

def test_vpc_lambda_configuration(lambda_client, student_id):
    """Task 3: Verify VPC configuration"""
    function_name = f"vpc-lambda-{student_id}"
    
    try:
        response = lambda_client.get_function_configuration(FunctionName=function_name)
        
        vpc_config = response.get('VpcConfig', {})
        
        if not vpc_config or not vpc_config.get('VpcId'):
            print(f"❌ Task 3 Failed: Function not configured with VPC")
            return False
        
        # Check subnets
        subnets = vpc_config.get('SubnetIds', [])
        if len(subnets) < 2:
            print(f"⚠️  Warning: Function should have at least 2 subnets for HA, found {len(subnets)}")
        
        # Check security groups
        security_groups = vpc_config.get('SecurityGroupIds', [])
        if not security_groups:
            print(f"⚠️  Warning: No security groups configured")
        
        print(f"✅ Task 3 Passed: VPC Lambda configured (VPC: {vpc_config['VpcId']}, Subnets: {len(subnets)})")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"❌ Task 3 Failed: Function '{function_name}' not found")
        else:
            print(f"❌ Task 3 Failed: {e}")
        return False

def test_async_function_with_destinations(lambda_client, student_id):
    """Task 4: Verify async function has destinations configured"""
    function_name = f"async-processor-{student_id}"
    
    try:
        response = lambda_client.get_function_event_invoke_config(FunctionName=function_name)
        
        # Check destinations
        destination_config = response.get('DestinationConfig', {})
        
        on_success = destination_config.get('OnSuccess', {}).get('Destination', '')
        on_failure = destination_config.get('OnFailure', {}).get('Destination', '')
        
        if not on_success and not on_failure:
            print(f"❌ Task 4 Failed: No destinations configured")
            return False
        
        if not on_success:
            print(f"⚠️  Warning: No success destination configured")
        if not on_failure:
            print(f"⚠️  Warning: No failure destination configured")
        
        # Check retry configuration
        max_retry = response.get('MaximumRetryAttempts', -1)
        if max_retry < 0:
            print(f"⚠️  Warning: Retry attempts not configured")
        
        print(f"✅ Task 4 Passed: Async function with destinations configured")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"❌ Task 4 Failed: Function '{function_name}' or invoke config not found")
        else:
            print(f"❌ Task 4 Failed: {e}")
        return False

def test_sqs_consumer_function(lambda_client, sqs_client, student_id):
    """Task 5: Verify SQS consumer function and queue exist"""
    function_name = f"sqs-consumer-{student_id}"
    queue_name = f"task-queue-{student_id}"
    
    try:
        # Check function exists
        lambda_client.get_function(FunctionName=function_name)
        
        # Check SQS queue exists
        try:
            queue_url = sqs_client.get_queue_url(QueueName=queue_name)['QueueUrl']
        except ClientError:
            print(f"❌ Task 5 Failed: SQS queue '{queue_name}' not found")
            return False
        
        # Check event source mapping
        mappings = lambda_client.list_event_source_mappings(FunctionName=function_name)
        
        sqs_mappings = [m for m in mappings['EventSourceMappings'] if 'sqs' in m.get('EventSourceArn', '').lower()]
        
        if not sqs_mappings:
            print(f"❌ Task 5 Failed: No SQS trigger configured for function")
            return False
        
        # Check if enabled
        enabled_mappings = [m for m in sqs_mappings if m['State'] in ['Enabled', 'Enabling']]
        if not enabled_mappings:
            print(f"⚠️  Warning: SQS trigger exists but is not enabled")
        
        print(f"✅ Task 5 Passed: SQS consumer function with queue trigger")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"❌ Task 5 Failed: Function '{function_name}' not found")
        else:
            print(f"❌ Task 5 Failed: {e}")
        return False

def test_dlq_configured(lambda_client, sqs_client, student_id):
    """Task 6: Verify DLQ configured"""
    function_name = f"async-processor-{student_id}"
    dlq_name = f"lambda-dlq-{student_id}"
    
    try:
        # Check if DLQ exists
        try:
            dlq_url = sqs_client.get_queue_url(QueueName=dlq_name)['QueueUrl']
        except ClientError:
            print(f"❌ Task 6 Failed: DLQ '{dlq_name}' not found")
            return False
        
        # Check function configuration
        response = lambda_client.get_function_configuration(FunctionName=function_name)
        
        dead_letter_config = response.get('DeadLetterConfig', {})
        target_arn = dead_letter_config.get('TargetArn', '')
        
        if not target_arn:
            print(f"❌ Task 6 Failed: No DLQ configured on function")
            return False
        
        if dlq_name not in target_arn:
            print(f"⚠️  Warning: Function DLQ may not be '{dlq_name}'")
        
        print(f"✅ Task 6 Passed: DLQ configured for function")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"❌ Task 6 Failed: Function '{function_name}' not found")
        else:
            print(f"❌ Task 6 Failed: {e}")
        return False

def test_reserved_concurrency(lambda_client, student_id):
    """Task 7: Verify reserved concurrency configured"""
    function_name = f"rate-limited-function-{student_id}"
    
    try:
        response = lambda_client.get_function_concurrency(FunctionName=function_name)
        
        reserved_concurrency = response.get('ReservedConcurrentExecutions')
        
        if reserved_concurrency is None:
            print(f"❌ Task 7 Failed: No reserved concurrency configured")
            return False
        
        if reserved_concurrency <= 0:
            print(f"❌ Task 7 Failed: Reserved concurrency is {reserved_concurrency} (should be > 0)")
            return False
        
        print(f"✅ Task 7 Passed: Reserved concurrency set to {reserved_concurrency}")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"❌ Task 7 Failed: Function '{function_name}' not found")
        else:
            print(f"❌ Task 7 Failed: {e}")
        return False

def test_function_aliases(lambda_client, student_id):
    """Task 9: Verify function aliases exist"""
    function_name = f"layer-consumer-{student_id}"
    
    try:
        response = lambda_client.list_aliases(FunctionName=function_name)
        
        aliases = response.get('Aliases', [])
        alias_names = [alias['Name'] for alias in aliases]
        
        required_aliases = ['PROD', 'STAGING']
        missing_aliases = [name for name in required_aliases if name not in alias_names]
        
        if missing_aliases:
            print(f"❌ Task 9 Failed: Missing aliases: {missing_aliases}")
            return False
        
        print(f"✅ Task 9 Passed: Function aliases configured ({len(aliases)} aliases)")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"❌ Task 9 Failed: Function '{function_name}' not found")
        else:
            print(f"❌ Task 9 Failed: {e}")
        return False

def test_cloudwatch_alarms(cloudwatch_client, student_id):
    """Task 12: Verify CloudWatch alarms exist"""
    
    try:
        response = cloudwatch_client.describe_alarms()
        alarms = response.get('MetricAlarms', [])
        
        # Filter alarms related to student's Lambda functions
        lambda_alarms = [
            alarm for alarm in alarms 
            if student_id in alarm.get('AlarmName', '') or
               any(dim.get('Value', '').endswith(student_id) for dim in alarm.get('Dimensions', []))
        ]
        
        if len(lambda_alarms) < 3:
            print(f"❌ Task 12 Failed: Need at least 3 alarms, found {len(lambda_alarms)}")
            return False
        
        # Check alarm types
        alarm_metrics = set(alarm.get('MetricName', '') for alarm in lambda_alarms)
        
        print(f"✅ Task 12 Passed: {len(lambda_alarms)} CloudWatch alarms configured")
        return True
        
    except ClientError as e:
        print(f"❌ Task 12 Failed: {e}")
        return False

def main():
    """Run all Lambda medium assessment tests"""
    print("=" * 60)
    print("AWS Lambda Medium Assessment - Validation")
    print("=" * 60)
    
    student_id = get_student_id()
    print(f"\n🎓 Student ID: {student_id}\n")
    
    # Initialize AWS clients
    try:
        lambda_client = boto3.client('lambda')
        sqs_client = boto3.client('sqs')
        cloudwatch_client = boto3.client('cloudwatch')
    except Exception as e:
        print(f"❌ Error initializing AWS clients: {e}")
        sys.exit(1)
    
    # Run tests
    results = []
    total_tasks = 9
    
    print("Starting validation...\n")
    
    # Task 1: Layer
    results.append(test_lambda_layer_exists(lambda_client, student_id))
    
    # Task 2: Function using layer
    results.append(test_layer_consumer_function(lambda_client, student_id))
    
    # Task 3: VPC Lambda
    results.append(test_vpc_lambda_configuration(lambda_client, student_id))
    
    # Task 4: Async with destinations
    results.append(test_async_function_with_destinations(lambda_client, student_id))
    
    # Task 5: SQS consumer
    results.append(test_sqs_consumer_function(lambda_client, sqs_client, student_id))
    
    # Task 6: DLQ
    results.append(test_dlq_configured(lambda_client, sqs_client, student_id))
    
    # Task 7: Reserved concurrency
    results.append(test_reserved_concurrency(lambda_client, student_id))
    
    # Task 9: Aliases
    results.append(test_function_aliases(lambda_client, student_id))
    
    # Task 12: CloudWatch alarms
    results.append(test_cloudwatch_alarms(cloudwatch_client, student_id))
    
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
        print("\n🎉 CONGRATULATIONS! You passed the Lambda Medium assessment!")
        print("You've successfully demonstrated advanced Lambda skills:")
        print("  ✓ Lambda layers for code reuse")
        print("  ✓ VPC integration")
        print("  ✓ Async invocation with destinations")
        print("  ✓ SQS event source mappings")
        print("  ✓ Dead Letter Queue (DLQ) configuration")
        print("  ✓ Concurrency management")
        print("  ✓ Function versioning and aliases")
        print("  ✓ CloudWatch monitoring and alarms")
        sys.exit(0)
    else:
        print("\n❌ Assessment not passed. Minimum score required: 70%")
        print("Please review the failed tasks and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
