# AWS DynamoDB Assessment - Global Tables & Enterprise Features (Hard)

github-repo: https://github.com/sharedlabs1/s3assessment

## Difficulty Level: 🔴 Hard

## Scenario
You are a Principal Engineer at GlobalCorp designing a multi-region, highly available, enterprise-grade DynamoDB architecture. Implement global tables for disaster recovery, advanced backup strategies, encryption at rest, cross-region replication, and comprehensive monitoring for a mission-critical financial application.

## Prerequisites
- Completed DynamoDB Easy and Medium assessments
- Deep understanding of DynamoDB architecture
- Experience with multi-region AWS deployments
- Knowledge of encryption and compliance requirements
- Python 3.8+ and boto3
- GitHub CLI (`gh`)
- Access to at least 2 AWS regions

## Setup

1. **Download the assessment files**:
   - `validate_tasks.py`
   - `requirements.txt`
   - `README_dynamodb_hard.md`

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Tasks to Complete

### Task 1: Create Global Table for Multi-Region Replication
Create a global table that replicates across multiple regions:

**Primary Region**: us-east-1
**Replica Regions**: us-west-2, eu-west-1

**Table Configuration:**
- **Table Name**: `transactions-global-${your-student-id}`
- **Partition Key**: `account_id` (String)
- **Sort Key**: `transaction_id` (String)
- **Billing Mode**: On-Demand
- **Stream**: Enabled (required for global tables)

**Steps:**
1. Create table in primary region (us-east-1)
2. Enable streams with NEW_AND_OLD_IMAGES
3. Add replica in us-west-2
4. Add replica in eu-west-1
5. Verify replication status is ACTIVE

```bash
# Create global table using AWS CLI
aws dynamodb create-global-table \
    --global-table-name transactions-global-STUDENTID \
    --replication-group RegionName=us-east-1 RegionName=us-west-2 RegionName=eu-west-1 \
    --region us-east-1
```

Or use DynamoDB console:
- Create table in us-east-1
- Go to "Global Tables" tab
- Click "Create replica"
- Select regions: us-west-2, eu-west-1

Add tags: `Environment=Production`, `Application=GlobalTransactions`, `Compliance=PCI-DSS`, `StudentID=${your-student-id}`

### Task 2: Enable Encryption at Rest with Customer Managed KMS Key
Use AWS KMS for enhanced security and compliance:

1. **Create KMS Key**:
```bash
aws kms create-key \
    --description "DynamoDB encryption key for transactions-global-STUDENTID" \
    --region us-east-1
```

2. **Create key alias**:
```bash
aws kms create-alias \
    --alias-name alias/dynamodb-transactions-STUDENTID \
    --target-key-id <key-id> \
    --region us-east-1
```

3. **Update table encryption**:
- Go to DynamoDB console → Select table
- Additional settings → Encryption at rest
- Change from AWS owned key to Customer managed key
- Select your KMS key

Repeat for replica tables in us-west-2 and eu-west-1 (create separate KMS keys per region).

### Task 3: Configure Point-in-Time Recovery (PITR) for All Replicas
Enable PITR for disaster recovery:

```bash
# Enable PITR in primary region
aws dynamodb update-continuous-backups \
    --table-name transactions-global-STUDENTID \
    --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true \
    --region us-east-1

# Enable PITR in us-west-2
aws dynamodb update-continuous-backups \
    --table-name transactions-global-STUDENTID \
    --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true \
    --region us-west-2

# Enable PITR in eu-west-1
aws dynamodb update-continuous-backups \
    --table-name transactions-global-STUDENTID \
    --point-in-time-recovery-specification PointInTimeRecoveryEnabled=true \
    --region eu-west-1
```

PITR allows restoration to any second within the last 35 days.

### Task 4: Create On-Demand Backup
Create manual backup snapshots:

```bash
aws dynamodb create-backup \
    --table-name transactions-global-STUDENTID \
    --backup-name transactions-backup-$(date +%Y%m%d-%H%M%S)-STUDENTID \
    --region us-east-1
```

Create at least 2 backups in the primary region.

### Task 5: Implement Backup Automation with Lambda
Create a Lambda function to automate daily backups:

**Function Name**: `dynamodb-backup-automation-${your-student-id}`
**Runtime**: Python 3.12
**Trigger**: EventBridge (CloudWatch Events) - Daily at 2 AM UTC

**Code** (`lambda_function.py`):
```python
import boto3
import os
from datetime import datetime

dynamodb = boto3.client('dynamodb')
table_name = os.environ['TABLE_NAME']

def lambda_handler(event, context):
    """Create daily backup of DynamoDB table"""
    
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_name = f"{table_name}-daily-backup-{timestamp}"
    
    try:
        response = dynamodb.create_backup(
            TableName=table_name,
            BackupName=backup_name
        )
        
        backup_arn = response['BackupDetails']['BackupArn']
        print(f"Backup created successfully: {backup_arn}")
        
        # Delete old backups (keep last 7 days)
        cleanup_old_backups(table_name)
        
        return {
            'statusCode': 200,
            'body': f'Backup created: {backup_name}'
        }
    except Exception as e:
        print(f"Error creating backup: {e}")
        raise

def cleanup_old_backups(table_name):
    """Delete backups older than 7 days"""
    try:
        backups = dynamodb.list_backups(
            TableName=table_name,
            TimeRangeLowerBound=datetime(2020, 1, 1),
            TimeRangeUpperBound=datetime.now()
        )
        
        backup_list = backups.get('BackupSummaries', [])
        
        for backup in backup_list:
            backup_age_days = (datetime.now() - backup['BackupCreationDateTime'].replace(tzinfo=None)).days
            
            if backup_age_days > 7:
                backup_arn = backup['BackupArn']
                dynamodb.delete_backup(BackupArn=backup_arn)
                print(f"Deleted old backup: {backup['BackupName']}")
                
    except Exception as e:
        print(f"Error cleaning up backups: {e}")
```

**Environment Variables**:
- `TABLE_NAME`: `transactions-global-${your-student-id}`

**IAM Permissions**:
- `dynamodb:CreateBackup`
- `dynamodb:ListBackups`
- `dynamodb:DeleteBackup`
- `dynamodb:DescribeTable`

**EventBridge Rule**:
- Name: `daily-dynamodb-backup-${your-student-id}`
- Schedule: `cron(0 2 * * ? *)` (2 AM UTC daily)
- Target: Lambda function

### Task 6: Test Point-in-Time Recovery
Perform PITR restore to verify disaster recovery capability:

1. **Insert test data**:
```python
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('transactions-global-STUDENTID')

# Insert test transaction
table.put_item(Item={
    'account_id': 'ACC001',
    'transaction_id': 'TXN001',
    'amount': 1000.00,
    'timestamp': datetime.now().isoformat(),
    'type': 'deposit'
})
```

2. **Wait 5 minutes** (for PITR to capture the state)

3. **Delete the item**:
```python
table.delete_item(Key={'account_id': 'ACC001', 'transaction_id': 'TXN001'})
```

4. **Restore to a point before deletion**:
```bash
aws dynamodb restore-table-to-point-in-time \
    --source-table-name transactions-global-STUDENTID \
    --target-table-name transactions-restored-STUDENTID \
    --use-latest-restorable-time \
    --region us-east-1
```

5. **Verify the restored table** contains the deleted item.

6. **Clean up** the restored table after verification.

### Task 7: Implement Global Secondary Index with Sparse Index Pattern
Create a GSI for querying high-value transactions:

**Index Configuration:**
- **Index Name**: `HighValueTransactionsIndex`
- **Partition Key**: `high_value_flag` (String)
- **Sort Key**: `amount` (Number)
- **Projection**: Include only: account_id, transaction_id, amount, timestamp

**Sparse Index Pattern**: Only items with `high_value_flag` attribute will appear in index (e.g., transactions > $10,000).

```python
# Add items with conditional high_value_flag
def add_transaction(account_id, transaction_id, amount):
    item = {
        'account_id': account_id,
        'transaction_id': transaction_id,
        'amount': amount,
        'timestamp': datetime.now().isoformat()
    }
    
    # Only set high_value_flag for large transactions
    if amount > 10000:
        item['high_value_flag'] = 'YES'
    
    table.put_item(Item=item)

# Query high-value transactions
response = table.query(
    IndexName='HighValueTransactionsIndex',
    KeyConditionExpression='high_value_flag = :flag',
    ExpressionAttributeValues={':flag': 'YES'},
    ScanIndexForward=False  # Descending order by amount
)
```

### Task 8: Configure DynamoDB Contributor Insights
Enable Contributor Insights for identifying hot partitions:

1. Go to DynamoDB console → Select table
2. Additional settings → Contributor Insights
3. Enable for base table
4. Enable for all Global Secondary Indexes
5. Monitor for hot keys and skewed access patterns

This helps identify:
- Most accessed partition keys
- Most throttled keys
- Uneven data distribution

### Task 9: Implement Advanced Monitoring with CloudWatch
Create comprehensive monitoring dashboards and alarms:

**Dashboard Name**: `DynamoDB-GlobalTable-${your-student-id}`

**Metrics to Monitor**:
1. **Replication Metrics**:
   - ReplicationLatency (us-west-2, eu-west-1)
   - PendingReplicationCount
   
2. **Performance Metrics**:
   - ConsumedReadCapacityUnits
   - ConsumedWriteCapacityUnits
   - SuccessfulRequestLatency
   
3. **Error Metrics**:
   - UserErrors
   - SystemErrors
   - ThrottledRequests
   
4. **Backup Metrics**:
   - BackupRetentionPeriod
   - BackupSize

**Critical Alarms**:

1. **High Replication Lag**:
```bash
aws cloudwatch put-metric-alarm \
    --alarm-name "DynamoDB-HighReplicationLag-STUDENTID" \
    --alarm-description "Replication lag > 5 minutes" \
    --metric-name ReplicationLatency \
    --namespace AWS/DynamoDB \
    --statistic Average \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 300000 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=TableName,Value=transactions-global-STUDENTID Name=ReceivingRegion,Value=us-west-2
```

2. **Failed Backups**:
```bash
aws cloudwatch put-metric-alarm \
    --alarm-name "DynamoDB-BackupFailed-STUDENTID" \
    --alarm-description "Backup failure detected" \
    --metric-name NumberOfBackupsFailed \
    --namespace AWS/DynamoDB \
    --statistic Sum \
    --period 3600 \
    --evaluation-periods 1 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold
```

3. **Transaction Volume Anomaly**:
```bash
aws cloudwatch put-metric-alarm \
    --alarm-name "DynamoDB-AnomalousWrites-STUDENTID" \
    --alarm-description "Unusual write activity" \
    --metric-name ConsumedWriteCapacityUnits \
    --namespace AWS/DynamoDB \
    --statistic Sum \
    --period 60 \
    --evaluation-periods 3 \
    --threshold 1000 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=TableName,Value=transactions-global-STUDENTID
```

Create at least 5 alarms covering replication, performance, and errors.

### Task 10: Implement Export to S3 for Analytics
Configure table export to S3 for data warehousing:

1. **Create S3 bucket**:
```bash
aws s3 mb s3://dynamodb-exports-STUDENTID --region us-east-1
```

2. **Export table to S3**:
```bash
aws dynamodb export-table-to-point-in-time \
    --table-arn arn:aws:dynamodb:us-east-1:ACCOUNT:table/transactions-global-STUDENTID \
    --s3-bucket dynamodb-exports-STUDENTID \
    --s3-prefix transactions-export/ \
    --export-format DYNAMODB_JSON \
    --region us-east-1
```

3. **Create Lambda function** to automate weekly exports:
   - Trigger: EventBridge (weekly on Sunday 3 AM)
   - Action: Export table to S3
   - Compression: GZIP
   - Format: DYNAMODB_JSON or ION

### Task 11: Configure VPC Endpoints for Private Access
Set up VPC endpoints for secure, private DynamoDB access:

1. **Create VPC Endpoint**:
```bash
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-XXXXX \
    --service-name com.amazonaws.us-east-1.dynamodb \
    --route-table-ids rtb-XXXXX \
    --region us-east-1
```

2. **Update route tables** to use VPC endpoint

3. **Configure security groups** to allow DynamoDB traffic

4. **Test private connectivity** from EC2 instance in VPC

This ensures DynamoDB traffic never leaves AWS network.

### Task 12: Implement Fine-Grained Access Control with IAM
Create granular IAM policies for least privilege access:

**Read-Only Policy** (for analysts):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:DescribeTable"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/transactions-global-STUDENTID"
    }
  ]
}
```

**Row-Level Security** (users can only access their own data):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/transactions-global-STUDENTID",
      "Condition": {
        "ForAllValues:StringEquals": {
          "dynamodb:LeadingKeys": ["${aws:username}"]
        }
      }
    }
  ]
}
```

Create 3 IAM policies:
- Admin (full access)
- Application (read/write)
- Analyst (read-only)

### Task 13: Implement DynamoDB Accelerator (DAX) for Caching
Deploy DAX cluster for microsecond read latency:

**Cluster Configuration:**
- **Cluster Name**: `transactions-dax-${your-student-id}`
- **Node Type**: dax.t3.small (2 nodes for HA)
- **Subnet Group**: Create in private subnets
- **Security Group**: Allow port 8111 from application servers
- **IAM Role**: Access to DynamoDB table

```python
# Application code using DAX
import amazondax

# DAX client endpoint
endpoint = "transactions-dax-STUDENTID.111222.dax-clusters.us-east-1.amazonaws.com:8111"

dax_client = amazondax.AmazonDaxClient(
    endpoints=[endpoint],
    region_name='us-east-1'
)

# Read from DAX (cached)
response = dax_client.get_item(
    TableName='transactions-global-STUDENTID',
    Key={
        'account_id': {'S': 'ACC001'},
        'transaction_id': {'S': 'TXN001'}
    }
)
```

DAX provides:
- 10x read performance improvement
- Microsecond latency
- Eventual consistency
- Automatic cache invalidation

### Task 14: Test Multi-Region Failover
Simulate regional failure and verify failover:

1. **Write data to primary region** (us-east-1)
2. **Verify replication** to us-west-2 and eu-west-1
3. **Simulate primary region failure**:
   - Update application endpoint to us-west-2
   - Continue read/write operations
4. **Monitor replication lag** during failover
5. **Verify data consistency** across all regions
6. **Document RTO (Recovery Time Objective)** and **RPO (Recovery Point Objective)**

Expected results:
- RTO: < 5 minutes (time to switch regions)
- RPO: < 1 minute (replication lag)

### Task 15: Implement Compliance and Audit Logging
Enable comprehensive logging for compliance (PCI-DSS, SOC 2):

1. **Enable CloudTrail** for DynamoDB API calls:
```bash
aws cloudtrail create-trail \
    --name dynamodb-audit-trail-STUDENTID \
    --s3-bucket-name cloudtrail-logs-STUDENTID \
    --is-multi-region-trail \
    --enable-log-file-validation
```

2. **Configure S3 bucket logging** for export bucket

3. **Create CloudWatch Log Group** for stream events

4. **Set up AWS Config** rules:
   - dynamodb-table-encrypted-kms
   - dynamodb-pitr-enabled
   - dynamodb-in-backup-plan
   - dynamodb-throughput-limit-check

5. **Enable AWS Audit Manager** assessment for compliance framework

## Validation

Run the validation script:

```bash
python validate_tasks.py dynamodb_hard
```

The script will verify:
- Global table exists in multiple regions (us-east-1, us-west-2, eu-west-1)
- Encryption with customer managed KMS keys
- PITR enabled in all regions
- On-demand backups exist
- Backup automation Lambda function configured
- Global Secondary Index configured
- Contributor Insights enabled
- CloudWatch alarms configured (at least 3)
- S3 export bucket exists
- DAX cluster deployed
- IAM policies created
- CloudTrail logging enabled
- Tags properly set

## Cleanup (After Assessment)
1. Delete DAX cluster
2. Delete Lambda functions
3. Delete CloudWatch alarms and dashboards
4. Delete backups
5. Disable PITR
6. Delete replica tables in us-west-2 and eu-west-1
7. Delete primary table in us-east-1
8. Delete KMS keys (after 7-day waiting period)
9. Delete S3 buckets with exports
10. Delete VPC endpoints
11. Delete CloudTrail trail

## Tips
- Global tables use "last writer wins" conflict resolution
- Encryption keys must be separate per region
- PITR backups are region-specific
- Global tables require DynamoDB Streams
- DAX is region-specific (no cross-region caching)
- Use sparse indexes to reduce storage costs
- Contributor Insights has additional charges
- Export to S3 is charged separately
- Cross-region replication incurs data transfer costs
- Test failover regularly (chaos engineering)
- Monitor replication lag closely
- Use on-demand billing for unpredictable workloads
- Implement exponential backoff for retries
- Use VPC endpoints to reduce data transfer costs

## Common Issues
- **ReplicationUpdateException**: Replica already exists or wrong state
- **BackupInUseException**: Backup currently being used for restore
- **InvalidRestoreTimeException**: PITR restore time too old or too new
- **ContinuousBackupsUnavailableException**: PITR not enabled
- **TableNotFoundException in replica**: Replication not complete
- **EncryptionKeyUnavailableException**: KMS key disabled or deleted
- **DAX connection timeout**: Security group misconfigured

## Learning Resources
- Global tables for multi-region replication
- Point-in-Time Recovery (PITR)
- Customer managed KMS encryption
- On-demand backups and restore
- DynamoDB Accelerator (DAX)
- Contributor Insights for hot key detection
- CloudWatch metrics and alarms
- Export to S3 for analytics
- VPC endpoints for private access
- Fine-grained access control with IAM
- Compliance and audit logging
- Multi-region failover testing
- Conflict resolution strategies
