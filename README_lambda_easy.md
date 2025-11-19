# AWS Lambda Assessment - Serverless Functions Basics (Easy)

github-repo: https://github.com/sharedlabs1/s3assessment

## Difficulty Level: 🟢 Easy

## Scenario
You are a developer at CloudTech building serverless applications. Create Lambda functions to process data from S3, respond to events, and integrate with other AWS services for automated workflows.

## Prerequisites
- Access to the shared AWS training account
- Python 3.8+ installed
- GitHub CLI (`gh`) installed
- Basic understanding of serverless computing
- Familiarity with Python or Node.js

## Setup

1. **Download the assessment files**:
   - `validate_tasks.py`
   - `requirements.txt`
   - `README_lambda_easy.md`

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Tasks to Complete

### Task 1: Create Your First Lambda Function
Create a simple Lambda function that returns a greeting:

**Function Configuration:**
- **Function Name**: `hello-world-${your-student-id}`
- **Runtime**: Python 3.12
- **Architecture**: x86_64
- **Timeout**: 30 seconds
- **Memory**: 128 MB

**Code** (`lambda_function.py`):
```python
import json

def lambda_handler(event, context):
    """Simple Hello World Lambda function"""
    
    name = event.get('name', 'World')
    
    message = f"Hello, {name}! This is Lambda function from student {context.function_name}"
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': message,
            'requestId': context.request_id
        })
    }
```

**Tags**: `Environment=Development`, `Application=HelloWorld`, `StudentID=${your-student-id}`

### Task 2: Configure Environment Variables
Add environment variables to your Lambda function:

Go to Lambda console → Configuration → Environment variables

Add the following:
- `APP_NAME`: `CloudTech Application`
- `ENVIRONMENT`: `Development`
- `STUDENT_ID`: `${your-student-id}`
- `LOG_LEVEL`: `INFO`

Update your function code to use these variables:
```python
import json
import os

def lambda_handler(event, context):
    """Lambda function using environment variables"""
    
    app_name = os.environ.get('APP_NAME', 'Unknown')
    environment = os.environ.get('ENVIRONMENT', 'Unknown')
    student_id = os.environ.get('STUDENT_ID', 'Unknown')
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    
    response = {
        'message': f'Welcome to {app_name}',
        'environment': environment,
        'student_id': student_id,
        'log_level': log_level
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
```

### Task 3: Create S3 Bucket for Lambda Triggers
Create an S3 bucket to trigger your Lambda function:

**Bucket Name**: `lambda-trigger-${your-student-id}`
**Region**: Same as your Lambda function
**Bucket Versioning**: Disabled
**Public Access**: Block all public access

Create folders:
- `/uploads/` - for incoming files
- `/processed/` - for processed files

### Task 4: Create Lambda Function for S3 Event Processing
Create a Lambda function to process files uploaded to S3:

**Function Name**: `s3-file-processor-${your-student-id}`
**Runtime**: Python 3.12
**Memory**: 256 MB
**Timeout**: 60 seconds

**Code** (`lambda_function.py`):
```python
import json
import boto3
import os
from datetime import datetime

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """Process S3 upload events"""
    
    # Parse S3 event
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']
        event_name = record['eventName']
        
        print(f"Processing {event_name} for {object_key} in bucket {bucket_name}")
        
        # Get object metadata
        try:
            response = s3_client.head_object(Bucket=bucket_name, Key=object_key)
            file_size = response['ContentLength']
            content_type = response.get('ContentType', 'unknown')
            
            print(f"File details: Size={file_size} bytes, Type={content_type}")
            
            # Create processing log
            log_key = f"processed/{object_key}.log"
            log_content = f"""
Processing Log
--------------
File: {object_key}
Size: {file_size} bytes
Content Type: {content_type}
Processed At: {datetime.now().isoformat()}
Event: {event_name}
Function: {context.function_name}
Request ID: {context.request_id}
            """
            
            # Upload log to processed folder
            s3_client.put_object(
                Bucket=bucket_name,
                Key=log_key,
                Body=log_content.encode('utf-8'),
                ContentType='text/plain'
            )
            
            print(f"Created processing log: {log_key}")
            
        except Exception as e:
            print(f"Error processing {object_key}: {e}")
            raise
    
    return {
        'statusCode': 200,
        'body': json.dumps('Processing complete')
    }
```

**IAM Role Permissions** (add to execution role):
- `s3:GetObject`
- `s3:PutObject`
- `s3:HeadObject`
- `logs:CreateLogGroup`
- `logs:CreateLogStream`
- `logs:PutLogEvents`

### Task 5: Configure S3 Event Trigger
Add an S3 trigger to your Lambda function:

1. Go to Lambda console → Select `s3-file-processor-${your-student-id}`
2. Click "Add trigger"
3. Select trigger: **S3**
4. **Bucket**: `lambda-trigger-${your-student-id}`
5. **Event type**: All object create events (s3:ObjectCreated:*)
6. **Prefix**: `uploads/`
7. **Suffix**: (leave empty to trigger for all files)
8. Acknowledge the permission changes

Now when you upload a file to `s3://lambda-trigger-STUDENTID/uploads/`, your Lambda will automatically process it.

### Task 6: Test Lambda Function
Test your S3 processor function:

**Upload a test file:**
```bash
echo "Hello Lambda!" > test-file.txt
aws s3 cp test-file.txt s3://lambda-trigger-STUDENTID/uploads/test-file.txt
```

**Verify**:
1. Check CloudWatch Logs for function execution
2. Verify processing log created in `/processed/` folder
3. Review function metrics in Lambda console

### Task 7: View CloudWatch Logs
Access logs for your Lambda function:

1. Go to Lambda console → Select function
2. Click "Monitor" tab
3. Click "View CloudWatch logs"
4. Select the latest log stream
5. Verify you see:
   - Function invocation logs
   - Processing details
   - File information
   - Any errors (should be none)

Or use AWS CLI:
```bash
aws logs tail /aws/lambda/s3-file-processor-STUDENTID --follow
```

### Task 8: Create Lambda Function with API Integration
Create a Lambda function to be invoked via API:

**Function Name**: `api-handler-${your-student-id}`
**Runtime**: Python 3.12
**Memory**: 128 MB

**Code** (`lambda_function.py`):
```python
import json

def lambda_handler(event, context):
    """Lambda function for API Gateway"""
    
    # Parse request
    http_method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', 'UNKNOWN'))
    path = event.get('path', event.get('rawPath', '/'))
    
    # Simple routing
    if http_method == 'GET':
        response_body = {
            'message': 'GET request received',
            'path': path,
            'timestamp': context.get_remaining_time_in_millis()
        }
    elif http_method == 'POST':
        body = event.get('body', '{}')
        response_body = {
            'message': 'POST request received',
            'data': json.loads(body) if body else {},
            'path': path
        }
    else:
        response_body = {
            'message': f'{http_method} request not supported',
            'path': path
        }
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(response_body)
    }
```

### Task 9: Test Lambda Function Manually
Test your functions using the Lambda console test feature:

1. Go to Lambda console → Select `hello-world-${your-student-id}`
2. Click "Test" tab
3. Create new test event:
   - **Event name**: `TestEvent`
   - **Template**: hello-world
   - **Event JSON**:
     ```json
     {
       "name": "Student",
       "message": "Testing Lambda function"
     }
     ```
4. Click "Test"
5. Verify response shows:
   - Status code 200
   - Message with greeting
   - Request ID

### Task 10: Monitor Function Metrics
Review Lambda function metrics in CloudWatch:

1. Go to Lambda console → Select function → Monitor tab
2. Review key metrics:
   - **Invocations**: Number of times function was called
   - **Duration**: Average execution time
   - **Error count**: Failed invocations (should be 0)
   - **Throttles**: Rate-limited invocations (should be 0)
   - **Concurrent executions**: Number of simultaneous runs

3. Create a CloudWatch alarm for errors:
   - Metric: Errors
   - Threshold: > 0 errors in 5 minutes
   - Action: SNS notification (optional)

## Validation

Run the validation script:

```bash
python validate_tasks.py lambda_easy
```

The script will verify:
- `hello-world-${your-student-id}` function exists
- Function has required environment variables
- S3 bucket `lambda-trigger-${your-student-id}` exists
- `s3-file-processor-${your-student-id}` function exists
- S3 trigger is configured on the function
- Function has been invoked successfully (check logs)
- `api-handler-${your-student-id}` function exists
- Tags are properly set

## Cleanup (After Assessment)
1. Delete Lambda functions
2. Delete S3 bucket and all objects
3. Delete CloudWatch log groups
4. Delete IAM roles created by Lambda
5. Delete CloudWatch alarms

## Tips
- Lambda automatically scales based on incoming requests
- First invocation may be slower (cold start)
- Keep functions small and focused (single responsibility)
- Use environment variables for configuration
- CloudWatch Logs are created automatically
- Lambda free tier: 1M requests and 400,000 GB-seconds per month
- Timeout maximum is 15 minutes
- Package size limit: 50 MB (zipped), 250 MB (unzipped)
- Use layers for shared code/dependencies
- Enable X-Ray tracing for detailed monitoring
- Set appropriate memory (CPU scales with memory)
- Monitor concurrency limits (default: 1000 per region)

## Common Issues
- **Access Denied**: Check IAM role permissions
- **Timeout**: Increase timeout or optimize code
- **Cold Start**: Use provisioned concurrency (advanced)
- **Memory Error**: Increase memory allocation
- **S3 Event not triggering**: Check event configuration and permissions
- **Import Error**: Package dependencies in deployment package
- **Environment variable not found**: Check spelling and case

## Learning Resources
- Lambda function basics and handlers
- Event-driven architecture
- S3 event notifications
- CloudWatch Logs and metrics
- IAM roles and policies for Lambda
- Environment variables
- Lambda execution context
- Cold starts vs warm starts
- Asynchronous vs synchronous invocation
- Error handling and retries
