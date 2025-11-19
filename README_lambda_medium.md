# AWS Lambda Assessment - Advanced Serverless Patterns (Medium)

github-repo: https://github.com/sharedlabs1/s3assessment

## Difficulty Level: 🟡 Medium

## Scenario
You are a Senior Cloud Engineer at TechScale building production-grade serverless applications. Implement advanced Lambda patterns including layers for code reuse, VPC integration for private resources, destinations for async workflows, DLQ for error handling, and comprehensive monitoring.

## Prerequisites
- Completed Lambda Easy assessment
- Understanding of VPC networking
- Familiarity with async programming
- Knowledge of error handling patterns
- Python 3.8+ and boto3
- GitHub CLI (`gh`)

## Setup

1. **Download the assessment files**:
   - `validate_tasks.py`
   - `requirements.txt`
   - `README_lambda_medium.md`

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Tasks to Complete

### Task 1: Create Lambda Layer for Shared Dependencies
Create a Lambda Layer to share common libraries across functions:

**Layer Name**: `common-utils-layer-${your-student-id}`
**Compatible Runtimes**: python3.12
**Description**: Common utilities and dependencies for Lambda functions

**Create layer structure:**
```bash
mkdir -p lambda-layer/python/lib/python3.12/site-packages
cd lambda-layer

# Install dependencies
pip install requests boto3 python-dateutil -t python/lib/python3.12/site-packages/

# Create utils module
cat > python/utils.py << 'EOF'
"""Common utilities for Lambda functions"""
import json
import logging
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def format_response(status_code, body, headers=None):
    """Format standard API response"""
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps(body) if not isinstance(body, str) else body
    }

def log_event(event, context):
    """Log event details"""
    logger.info(f"Function: {context.function_name}")
    logger.info(f"Request ID: {context.request_id}")
    logger.info(f"Event: {json.dumps(event)}")

def validate_input(data, required_fields):
    """Validate required fields in input"""
    missing = [field for field in required_fields if field not in data]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
    return True

class Timer:
    """Context manager for timing operations"""
    def __enter__(self):
        self.start = datetime.now()
        return self
    
    def __exit__(self, *args):
        self.end = datetime.now()
        self.duration = (self.end - self.start).total_seconds()
        logger.info(f"Operation took {self.duration:.2f} seconds")
EOF

# Zip layer
zip -r layer.zip python/
```

**Upload layer:**
```bash
aws lambda publish-layer-version \
    --layer-name common-utils-layer-STUDENTID \
    --description "Common utilities and dependencies" \
    --zip-file fileb://layer.zip \
    --compatible-runtimes python3.12
```

### Task 2: Create Lambda Function Using Layer
Create a Lambda function that uses your layer:

**Function Name**: `layer-consumer-${your-student-id}`
**Runtime**: Python 3.12
**Memory**: 256 MB
**Layers**: Add your `common-utils-layer-${your-student-id}` layer

**Code** (`lambda_function.py`):
```python
import json
from utils import format_response, log_event, validate_input, Timer

def lambda_handler(event, context):
    """Lambda function using shared layer"""
    
    # Use layer utilities
    log_event(event, context)
    
    try:
        # Parse input
        body = json.loads(event.get('body', '{}'))
        
        # Validate input using layer utility
        validate_input(body, ['name', 'operation'])
        
        # Process with timer
        with Timer() as timer:
            result = process_data(body)
        
        # Format response using layer utility
        return format_response(200, {
            'message': 'Success',
            'result': result,
            'duration': f"{timer.duration:.2f}s"
        })
        
    except ValueError as e:
        return format_response(400, {'error': str(e)})
    except Exception as e:
        return format_response(500, {'error': 'Internal server error'})

def process_data(data):
    """Process the data"""
    name = data['name']
    operation = data['operation']
    return f"Processed {operation} for {name}"
```

### Task 3: Configure VPC Access for Lambda
Create Lambda function with VPC access to private resources:

**Prerequisites:**
- Create or identify existing VPC with private subnets
- Create security group for Lambda: `lambda-sg-${your-student-id}`
- Allow outbound traffic to necessary services

**Function Name**: `vpc-lambda-${your-student-id}`
**Runtime**: Python 3.12
**Memory**: 512 MB
**VPC Configuration**:
- Select your VPC
- Select 2+ private subnets in different AZs
- Select Lambda security group

**Code** (`lambda_function.py`):
```python
import json
import boto3
import os

def lambda_handler(event, context):
    """Lambda function with VPC access"""
    
    # Access RDS, ElastiCache, or other VPC resources
    # This is a simulation - replace with actual VPC resource access
    
    vpc_config = {
        'vpc_id': os.environ.get('VPC_ID', 'unknown'),
        'subnets': os.environ.get('SUBNET_IDS', 'unknown'),
        'security_group': os.environ.get('SECURITY_GROUP_ID', 'unknown')
    }
    
    # Example: Connect to RDS database in VPC
    # db_endpoint = "mydb.abc123.us-east-1.rds.amazonaws.com"
    # connection = connect_to_database(db_endpoint)
    
    # For this demo, just show VPC configuration
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Lambda running in VPC',
            'vpc_config': vpc_config,
            'function_name': context.function_name
        })
    }
```

**Environment Variables**:
- `VPC_ID`: Your VPC ID
- `SUBNET_IDS`: Comma-separated subnet IDs
- `SECURITY_GROUP_ID`: Security group ID

**IAM Permissions** (add to execution role):
- `ec2:CreateNetworkInterface`
- `ec2:DescribeNetworkInterfaces`
- `ec2:DeleteNetworkInterface`

### Task 4: Implement Async Invocation with Destinations
Create Lambda with success and failure destinations:

**Function Name**: `async-processor-${your-student-id}`
**Runtime**: Python 3.12
**Memory**: 256 MB

**Code** (`lambda_function.py`):
```python
import json
import random
import time

def lambda_handler(event, context):
    """Async Lambda with success/failure handling"""
    
    print(f"Processing event: {json.dumps(event)}")
    
    # Get task from event
    task_id = event.get('task_id', 'unknown')
    should_fail = event.get('simulate_failure', False)
    
    # Simulate processing time
    time.sleep(2)
    
    # Simulate random failures if not explicitly set
    if should_fail or (not event.get('force_success') and random.random() < 0.2):
        raise Exception(f"Task {task_id} failed during processing")
    
    # Success case
    result = {
        'task_id': task_id,
        'status': 'completed',
        'processed_at': time.time(),
        'function': context.function_name
    }
    
    print(f"Task completed: {json.dumps(result)}")
    return result
```

**Configure Destinations:**

1. **Create SQS Queues for Destinations:**
```bash
# Success queue
aws sqs create-queue \
    --queue-name lambda-success-queue-STUDENTID \
    --attributes MessageRetentionPeriod=86400

# Failure queue (Dead Letter Queue)
aws sqs create-queue \
    --queue-name lambda-failure-queue-STUDENTID \
    --attributes MessageRetentionPeriod=86400
```

2. **Add Destinations to Lambda:**
   - Go to Lambda console → Configuration → Asynchronous invocation
   - **Maximum age of event**: 6 hours
   - **Retry attempts**: 2
   - **On success**: Send to SQS queue `lambda-success-queue-STUDENTID`
   - **On failure**: Send to SQS queue `lambda-failure-queue-STUDENTID`

### Task 5: Create SQS Trigger for Lambda
Process messages from SQS queue:

**Create SQS Queue:**
```bash
aws sqs create-queue \
    --queue-name task-queue-STUDENTID \
    --attributes VisibilityTimeout=300,MessageRetentionPeriod=345600
```

**Function Name**: `sqs-consumer-${your-student-id}`
**Runtime**: Python 3.12
**Memory**: 256 MB

**Code** (`lambda_function.py`):
```python
import json

def lambda_handler(event, context):
    """Process messages from SQS queue"""
    
    processed = []
    failed = []
    
    for record in event['Records']:
        message_id = record['messageId']
        body = json.loads(record['body'])
        
        try:
            print(f"Processing message {message_id}: {body}")
            
            # Process message
            result = process_message(body)
            processed.append(message_id)
            
            print(f"Successfully processed: {message_id}")
            
        except Exception as e:
            print(f"Failed to process {message_id}: {e}")
            failed.append({'messageId': message_id, 'error': str(e)})
    
    # Return batch item failures for partial batch response
    if failed:
        return {
            'batchItemFailures': [{'itemIdentifier': f['messageId']} for f in failed]
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Processed {len(processed)} messages')
    }

def process_message(message):
    """Process individual message"""
    action = message.get('action')
    data = message.get('data')
    
    if action == 'process':
        return f"Processed: {data}"
    elif action == 'validate':
        return f"Validated: {data}"
    else:
        raise ValueError(f"Unknown action: {action}")
```

**Configure SQS Trigger:**
- Add trigger: SQS
- SQS queue: `task-queue-STUDENTID`
- Batch size: 10
- Enable batch window: 5 seconds
- Enable report batch item failures

### Task 6: Implement Error Handling with Dead Letter Queue
Configure DLQ for async Lambda:

**Create DLQ:**
```bash
aws sqs create-queue \
    --queue-name lambda-dlq-STUDENTID \
    --attributes MessageRetentionPeriod=1209600  # 14 days
```

**Add DLQ to Lambda:**
- Go to Lambda → Configuration → Asynchronous invocation
- **Dead-letter queue service**: SQS
- **Queue**: `lambda-dlq-STUDENTID`

**Create Lambda to Process DLQ:**

**Function Name**: `dlq-processor-${your-student-id}`
**Runtime**: Python 3.12

**Code**:
```python
import json
import boto3

sns_client = boto3.client('sns')

def lambda_handler(event, context):
    """Process messages from DLQ and alert"""
    
    for record in event['Records']:
        body = json.loads(record['body'])
        
        # Extract original event
        original_event = body.get('requestPayload', {})
        error_message = body.get('responsePayload', {}).get('errorMessage', 'Unknown error')
        
        print(f"DLQ Message: {json.dumps(body)}")
        print(f"Original event: {json.dumps(original_event)}")
        print(f"Error: {error_message}")
        
        # Alert via SNS (optional)
        # sns_client.publish(
        #     TopicArn='arn:aws:sns:region:account:lambda-alerts',
        #     Subject='Lambda DLQ Alert',
        #     Message=f'Failed event: {json.dumps(original_event)}\nError: {error_message}'
        # )
    
    return {'statusCode': 200}
```

**Configure SQS Trigger** for DLQ processor.

### Task 7: Implement Reserved Concurrency
Control concurrent executions:

**Function Name**: `rate-limited-function-${your-student-id}`
**Runtime**: Python 3.12

**Configure Reserved Concurrency:**
1. Go to Lambda → Configuration → Concurrency
2. **Reserved concurrency**: 5
   - This function will never exceed 5 concurrent executions
   - Prevents it from consuming all account concurrency
   - Additional invocations will be throttled

**Code**:
```python
import time
import json

def lambda_handler(event, context):
    """Function with limited concurrency"""
    
    # Simulate long-running task
    print(f"Starting execution: {context.request_id}")
    time.sleep(10)  # 10 second task
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Task completed',
            'request_id': context.request_id
        })
    }
```

**Test concurrency:**
```python
import boto3
import json

lambda_client = boto3.client('lambda')

# Invoke 10 times concurrently (only 5 will run at once)
for i in range(10):
    lambda_client.invoke(
        FunctionName='rate-limited-function-STUDENTID',
        InvocationType='Event',  # Async
        Payload=json.dumps({'iteration': i})
    )
```

### Task 8: Configure Lambda Insights for Enhanced Monitoring
Enable CloudWatch Lambda Insights:

1. **Add Lambda Insights Layer** to your functions:
   - Layer ARN: `arn:aws:lambda:REGION:580247275435:layer:LambdaInsightsExtension:VERSION`
   - Get latest version from AWS documentation

2. **Add IAM Policy** to execution role:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "cloudwatch:namespace": "LambdaInsights"
        }
      }
    }
  ]
}
```

3. **View Insights:**
   - Go to CloudWatch → Lambda Insights
   - Select your function
   - View: Cold starts, memory usage, duration, errors

### Task 9: Implement Function Aliases and Versions
Use aliases for blue/green deployments:

**Publish Version:**
```bash
aws lambda publish-version \
    --function-name layer-consumer-STUDENTID \
    --description "Initial production version"
```

**Create Aliases:**
```bash
# Production alias pointing to version 1
aws lambda create-alias \
    --function-name layer-consumer-STUDENTID \
    --name PROD \
    --function-version 1

# Staging alias pointing to $LATEST
aws lambda create-alias \
    --function-name layer-consumer-STUDENTID \
    --name STAGING \
    --function-version \$LATEST
```

**Weighted Alias (Canary Deployment):**
```bash
# Split traffic 90% v1, 10% v2
aws lambda update-alias \
    --function-name layer-consumer-STUDENTID \
    --name PROD \
    --function-version 1 \
    --routing-config AdditionalVersionWeights={"2"=0.1}
```

**Invoke Specific Alias:**
```bash
aws lambda invoke \
    --function-name layer-consumer-STUDENTID:PROD \
    --payload '{"name":"test","operation":"validate"}' \
    output.json
```

### Task 10: Configure Auto Scaling with Provisioned Concurrency
Eliminate cold starts for critical functions:

**Configure Provisioned Concurrency:**
```bash
# Add provisioned concurrency to alias
aws lambda put-provisioned-concurrency-config \
    --function-name layer-consumer-STUDENTID \
    --provisioned-concurrent-executions 2 \
    --qualifier PROD
```

**Application Auto Scaling:**
```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
    --service-namespace lambda \
    --resource-id function:layer-consumer-STUDENTID:PROD \
    --scalable-dimension lambda:function:ProvisionedConcurrentExecutions \
    --min-capacity 2 \
    --max-capacity 10

# Create scaling policy
aws application-autoscaling put-scaling-policy \
    --service-namespace lambda \
    --resource-id function:layer-consumer-STUDENTID:PROD \
    --scalable-dimension lambda:function:ProvisionedConcurrentExecutions \
    --policy-name target-tracking-policy \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration '{
      "TargetValue": 0.70,
      "PredefinedMetricSpecification": {
        "PredefinedMetricType": "LambdaProvisionedConcurrencyUtilization"
      }
    }'
```

### Task 11: Implement Cross-Account Lambda Invocation
Allow another AWS account to invoke your Lambda:

**Add Resource-Based Policy:**
```bash
aws lambda add-permission \
    --function-name layer-consumer-STUDENTID \
    --statement-id AllowCrossAccountInvoke \
    --action lambda:InvokeFunction \
    --principal TRUSTED_ACCOUNT_ID
```

### Task 12: Create CloudWatch Alarms for Lambda
Monitor critical metrics:

**Alarm 1: High Error Rate**
```bash
aws cloudwatch put-metric-alarm \
    --alarm-name "Lambda-HighErrorRate-STUDENTID" \
    --alarm-description "Lambda error rate > 5%" \
    --metric-name Errors \
    --namespace AWS/Lambda \
    --statistic Sum \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 5 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=FunctionName,Value=layer-consumer-STUDENTID \
    --treat-missing-data notBreaching
```

**Alarm 2: High Duration**
```bash
aws cloudwatch put-metric-alarm \
    --alarm-name "Lambda-HighDuration-STUDENTID" \
    --alarm-description "Lambda duration > 25 seconds" \
    --metric-name Duration \
    --namespace AWS/Lambda \
    --statistic Average \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 25000 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=FunctionName,Value=layer-consumer-STUDENTID
```

**Alarm 3: Throttled Invocations**
```bash
aws cloudwatch put-metric-alarm \
    --alarm-name "Lambda-Throttles-STUDENTID" \
    --alarm-description "Lambda throttles detected" \
    --metric-name Throttles \
    --namespace AWS/Lambda \
    --statistic Sum \
    --period 300 \
    --evaluation-periods 1 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --dimensions Name=FunctionName,Value=layer-consumer-STUDENTID
```

Create at least 3 alarms for your functions.

## Validation

Run the validation script:

```bash
python validate_tasks.py lambda_medium
```

The script will verify:
- Lambda layer `common-utils-layer-${your-student-id}` exists
- Function `layer-consumer-${your-student-id}` uses the layer
- VPC Lambda `vpc-lambda-${your-student-id}` configured with VPC
- Async processor with destinations configured
- SQS queue and consumer function exist
- DLQ configured for async function
- Reserved concurrency set on `rate-limited-function-${your-student-id}`
- Lambda Insights enabled on at least one function
- Function aliases (PROD, STAGING) exist
- CloudWatch alarms configured (at least 3)

## Cleanup (After Assessment)
1. Delete Lambda functions
2. Delete Lambda layers
3. Delete SQS queues (including DLQs)
4. Delete CloudWatch alarms
5. Delete function aliases and versions
6. Remove VPC ENIs (auto-deleted when function deleted)
7. Delete CloudWatch log groups

## Tips
- Layers reduce deployment package size
- VPC Lambda needs NAT Gateway for internet access
- Use destinations instead of polling for async results
- DLQ helps debug failed invocations
- Reserved concurrency prevents runaway costs
- Lambda Insights adds ~$0.0000000025 per request
- Provisioned concurrency eliminates cold starts but costs more
- Use aliases for traffic shifting (blue/green, canary)
- Partial batch failures reduce SQS reprocessing
- EventBridge rules can target specific aliases
- Lambda in VPC has higher cold start time
- Max concurrent executions: 1000 (default, can increase)

## Common Issues
- **ENI creation timeout**: VPC subnet out of IPs
- **Throttling**: Exceeded concurrency limit
- **DLQ not receiving messages**: Check IAM permissions
- **Layer not found**: Incompatible runtime or region mismatch
- **SQS batch failure**: Enable report batch item failures
- **VPC timeout**: No NAT Gateway or route to internet
- **Destinations not working**: Async invocation required

## Learning Resources
- Lambda layers for code reuse
- VPC integration and networking
- Asynchronous invocation patterns
- Destinations for success/failure handling
- Dead Letter Queues (DLQ)
- SQS triggers and batch processing
- Reserved and provisioned concurrency
- Lambda Insights monitoring
- Function versioning and aliases
- Blue/green and canary deployments
- CloudWatch metrics and alarms
- Cross-account permissions
