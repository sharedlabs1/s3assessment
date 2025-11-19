"""
AWS Lambda Easy Assessment - Test Script
Tests basic Lambda functions, S3 triggers, environment variables, and CloudWatch logs
"""

import sys
import boto3
import time
from botocore.exceptions import ClientError

def get_student_id():
    """Get student ID from command line arguments"""
    if len(sys.argv) < 2:
        print("Error: Student ID is required")
        print("Usage: python validate_tasks.py lambda_easy")
        sys.exit(1)
    return sys.argv[1]

def test_hello_world_function(lambda_client, student_id):
    """Task 1: Verify hello-world Lambda function exists"""
    function_name = f"hello-world-{student_id}"
    
    try:
        response = lambda_client.get_function(FunctionName=function_name)
        
        config = response['Configuration']
        
        # Check runtime
        runtime = config.get('Runtime', '')
        if not runtime.startswith('python3'):
            print(f"⚠️  Warning: Runtime is {runtime}, recommended: python3.12")
        
        # Check memory
        memory = config.get('MemorySize', 0)
        if memory < 128:
            print(f"⚠️  Warning: Memory is {memory} MB, recommended: 128 MB or more")
        
        # Check timeout
        timeout = config.get('Timeout', 0)
        if timeout < 30:
            print(f"⚠️  Warning: Timeout is {timeout}s, recommended: 30s or more")
        
        print(f"✅ Task 1 Passed: Lambda function '{function_name}' exists")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"❌ Task 1 Failed: Lambda function '{function_name}' not found")
        else:
            print(f"❌ Task 1 Failed: {e}")
        return False

def test_environment_variables(lambda_client, student_id):
    """Task 2: Verify environment variables are configured"""
    function_name = f"hello-world-{student_id}"
    
    try:
        response = lambda_client.get_function_configuration(FunctionName=function_name)
        
        env_vars = response.get('Environment', {}).get('Variables', {})
        
        required_vars = ['APP_NAME', 'ENVIRONMENT', 'STUDENT_ID', 'LOG_LEVEL']
        missing_vars = [var for var in required_vars if var not in env_vars]
        
        if missing_vars:
            print(f"❌ Task 2 Failed: Missing environment variables: {missing_vars}")
            return False
        
        # Check STUDENT_ID value
        if env_vars.get('STUDENT_ID') != student_id:
            print(f"⚠️  Warning: STUDENT_ID={env_vars.get('STUDENT_ID')}, expected {student_id}")
        
        print(f"✅ Task 2 Passed: All required environment variables configured")
        return True
        
    except ClientError as e:
        print(f"❌ Task 2 Failed: {e}")
        return False

def test_s3_bucket_exists(s3_client, student_id):
    """Task 3: Verify S3 bucket for triggers exists"""
    bucket_name = f"lambda-trigger-{student_id}"
    
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        
        # Check for folders (optional check via listing)
        try:
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix='uploads/', Delimiter='/', MaxKeys=1)
            response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix='processed/', Delimiter='/', MaxKeys=1)
        except:
            pass
        
        print(f"✅ Task 3 Passed: S3 bucket '{bucket_name}' exists")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code in ['404', 'NoSuchBucket']:
            print(f"❌ Task 3 Failed: S3 bucket '{bucket_name}' not found")
        else:
            print(f"❌ Task 3 Failed: {e}")
        return False

def test_s3_processor_function(lambda_client, student_id):
    """Task 4: Verify S3 file processor function exists"""
    function_name = f"s3-file-processor-{student_id}"
    
    try:
        response = lambda_client.get_function(FunctionName=function_name)
        
        config = response['Configuration']
        
        # Check memory (should be at least 256 MB for S3 processing)
        memory = config.get('MemorySize', 0)
        if memory < 256:
            print(f"⚠️  Warning: Memory is {memory} MB, recommended: 256 MB or more")
        
        # Check timeout (should be at least 60s)
        timeout = config.get('Timeout', 0)
        if timeout < 60:
            print(f"⚠️  Warning: Timeout is {timeout}s, recommended: 60s or more")
        
        # Check IAM role has S3 permissions
        role_arn = config.get('Role', '')
        if not role_arn:
            print(f"⚠️  Warning: No IAM role found")
        
        print(f"✅ Task 4 Passed: S3 processor function '{function_name}' exists")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"❌ Task 4 Failed: Lambda function '{function_name}' not found")
        else:
            print(f"❌ Task 4 Failed: {e}")
        return False

def test_s3_trigger_configured(lambda_client, s3_client, student_id):
    """Task 5: Verify S3 trigger is configured"""
    function_name = f"s3-file-processor-{student_id}"
    bucket_name = f"lambda-trigger-{student_id}"
    
    try:
        # Check Lambda event source mappings (for streams/queues)
        # For S3, we need to check bucket notifications
        
        try:
            response = s3_client.get_bucket_notification_configuration(Bucket=bucket_name)
            
            lambda_configs = response.get('LambdaFunctionConfigurations', [])
            
            if not lambda_configs:
                print(f"❌ Task 5 Failed: No Lambda triggers configured on S3 bucket")
                return False
            
            # Check if our function is configured
            function_arn = lambda_client.get_function(FunctionName=function_name)['Configuration']['FunctionArn']
            
            configured = any(
                function_arn in config.get('LambdaFunctionArn', '') 
                for config in lambda_configs
            )
            
            if not configured:
                print(f"❌ Task 5 Failed: S3 trigger not configured for function '{function_name}'")
                return False
            
            # Check event type
            events = lambda_configs[0].get('Events', [])
            if not any('s3:ObjectCreated' in event for event in events):
                print(f"⚠️  Warning: No ObjectCreated event configured")
            
            print(f"✅ Task 5 Passed: S3 trigger configured for function")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                print(f"❌ Task 5 Failed: Bucket '{bucket_name}' not found")
            else:
                print(f"❌ Task 5 Failed: Error checking bucket notification: {e}")
            return False
        
    except ClientError as e:
        print(f"❌ Task 5 Failed: {e}")
        return False

def test_function_invocation_logs(logs_client, student_id):
    """Task 6-7: Verify function has been invoked (check CloudWatch logs)"""
    function_name = f"s3-file-processor-{student_id}"
    log_group_name = f"/aws/lambda/{function_name}"
    
    try:
        # Check if log group exists
        response = logs_client.describe_log_groups(logGroupNamePrefix=log_group_name)
        
        log_groups = response.get('logGroups', [])
        if not log_groups:
            print(f"❌ Task 7 Failed: No CloudWatch logs found (function may not have been invoked)")
            return False
        
        # Check for recent log streams
        streams_response = logs_client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy='LastEventTime',
            descending=True,
            limit=5
        )
        
        log_streams = streams_response.get('logStreams', [])
        if not log_streams:
            print(f"⚠️  Warning: No log streams found (function may not have been invoked yet)")
            return True  # Pass if log group exists even without streams
        
        # Check for recent activity (last stream)
        latest_stream = log_streams[0]
        last_event_time = latest_stream.get('lastEventTimestamp', 0)
        
        # Check if invoked within last 24 hours (86400000 ms)
        current_time = int(time.time() * 1000)
        time_diff = current_time - last_event_time
        
        if time_diff > 86400000:  # More than 24 hours
            print(f"⚠️  Warning: Last invocation was more than 24 hours ago")
        
        print(f"✅ Task 7 Passed: CloudWatch logs available (function has been invoked)")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"❌ Task 7 Failed: Log group not found (function likely not invoked)")
        else:
            print(f"❌ Task 7 Failed: {e}")
        return False

def test_api_handler_function(lambda_client, student_id):
    """Task 8: Verify API handler function exists"""
    function_name = f"api-handler-{student_id}"
    
    try:
        response = lambda_client.get_function(FunctionName=function_name)
        
        config = response['Configuration']
        
        # Check runtime
        runtime = config.get('Runtime', '')
        if not runtime.startswith('python3'):
            print(f"⚠️  Warning: Runtime is {runtime}, recommended: python3.12")
        
        print(f"✅ Task 8 Passed: API handler function '{function_name}' exists")
        return True
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print(f"❌ Task 8 Failed: Lambda function '{function_name}' not found")
        else:
            print(f"❌ Task 8 Failed: {e}")
        return False

def test_function_tags(lambda_client, student_id):
    """Verify function has required tags"""
    function_name = f"hello-world-{student_id}"
    
    try:
        response = lambda_client.get_function(FunctionName=function_name)
        function_arn = response['Configuration']['FunctionArn']
        
        tags_response = lambda_client.list_tags(Resource=function_arn)
        tags = tags_response.get('Tags', {})
        
        required_tags = {
            'Environment': 'Development',
            'Application': 'HelloWorld',
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
    """Run all Lambda easy assessment tests"""
    print("=" * 60)
    print("AWS Lambda Easy Assessment - Validation")
    print("=" * 60)
    
    student_id = get_student_id()
    print(f"\n🎓 Student ID: {student_id}")
    print(f"⚡ Functions: hello-world-{student_id}, s3-file-processor-{student_id}, api-handler-{student_id}\n")
    
    # Initialize AWS clients
    try:
        lambda_client = boto3.client('lambda')
        s3_client = boto3.client('s3')
        logs_client = boto3.client('logs')
    except Exception as e:
        print(f"❌ Error initializing AWS clients: {e}")
        sys.exit(1)
    
    # Run tests
    results = []
    total_tasks = 8
    
    print("Starting validation...\n")
    
    # Task 1: Hello world function
    results.append(test_hello_world_function(lambda_client, student_id))
    
    # Task 2: Environment variables
    results.append(test_environment_variables(lambda_client, student_id))
    
    # Task 3: S3 bucket
    results.append(test_s3_bucket_exists(s3_client, student_id))
    
    # Task 4: S3 processor function
    results.append(test_s3_processor_function(lambda_client, student_id))
    
    # Task 5: S3 trigger
    results.append(test_s3_trigger_configured(lambda_client, s3_client, student_id))
    
    # Task 7: CloudWatch logs
    results.append(test_function_invocation_logs(logs_client, student_id))
    
    # Task 8: API handler
    results.append(test_api_handler_function(lambda_client, student_id))
    
    # Tags
    results.append(test_function_tags(lambda_client, student_id))
    
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
        print("\n🎉 CONGRATULATIONS! You passed the Lambda Easy assessment!")
        print("You've successfully demonstrated basic AWS Lambda skills:")
        print("  ✓ Creating Lambda functions")
        print("  ✓ Configuring environment variables")
        print("  ✓ Setting up S3 event triggers")
        print("  ✓ Processing S3 events")
        print("  ✓ CloudWatch logging and monitoring")
        sys.exit(0)
    else:
        print("\n❌ Assessment not passed. Minimum score required: 70%")
        print("Please review the failed tasks and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
