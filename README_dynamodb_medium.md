# AWS DynamoDB Assessment - Advanced Indexing & Streams (Medium)

github-repo: https://github.com/sharedlabs1/s3assessment

## Difficulty Level: 🟡 Medium

## Scenario
You are a senior backend engineer at GrowthCo building a high-performance order management system. Implement advanced DynamoDB features including secondary indexes, streams, caching, and batch operations to support complex queries and real-time data processing.

## Prerequisites
- Completed DynamoDB Easy assessment
- Understanding of DynamoDB indexes (GSI, LSI)
- Familiarity with DynamoDB Streams
- Python 3.8+ and boto3
- GitHub CLI (`gh`)

## Setup

1. **Download the assessment files**:
   - `validate_tasks.py`
   - `requirements.txt`
   - `README_dynamodb_medium.md`

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Tasks to Complete

### Task 1: Create Orders Table with Composite Key
Create a DynamoDB table for order management:
- **Table Name**: `orders-${your-student-id}`
- **Partition Key**: `customer_id` (String)
- **Sort Key**: `order_id` (String)
- **Billing Mode**: On-Demand
- **Table Class**: Standard

Add tags: `Environment=Production`, `Application=OrderManagement`, `StudentID=${your-student-id}`

### Task 2: Create Global Secondary Index (GSI)
Add a Global Secondary Index to query orders by status and date:
- **Index Name**: `StatusDateIndex`
- **Partition Key**: `status` (String)
- **Sort Key**: `order_date` (String)
- **Projection Type**: ALL (include all attributes)

This allows querying orders by status (e.g., "pending", "shipped", "delivered") ordered by date.

### Task 3: Create Local Secondary Index (LSI)
Add a Local Secondary Index to query orders by customer and total amount:
- **Index Name**: `CustomerAmountIndex`
- **Partition Key**: `customer_id` (same as table)
- **Sort Key**: `total_amount` (Number)
- **Projection Type**: ALL

**Note**: LSI must be created at table creation time. If your table already exists, you'll need to:
1. Export data
2. Delete table
3. Recreate with LSI
4. Import data back

### Task 4: Populate Table with Sample Data
Insert sample orders using batch write:

```python
import boto3
from datetime import datetime, timedelta
import random

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('orders-STUDENTID')

# Generate sample orders
orders = []
customers = ['CUST001', 'CUST002', 'CUST003', 'CUST004', 'CUST005']
statuses = ['pending', 'processing', 'shipped', 'delivered']
products = ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Headphones']

for i in range(1, 21):  # Create 20 orders
    order_date = (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d')
    order = {
        'customer_id': random.choice(customers),
        'order_id': f'ORD{i:04d}',
        'status': random.choice(statuses),
        'order_date': order_date,
        'product': random.choice(products),
        'quantity': random.randint(1, 5),
        'total_amount': round(random.uniform(50, 1500), 2),
        'shipping_address': f'{random.randint(100, 999)} Main St, City, State',
        'created_at': datetime.now().isoformat()
    }
    orders.append(order)

# Batch write (25 items max per batch)
with table.batch_writer() as batch:
    for order in orders:
        batch.put_item(Item=order)

print(f"Inserted {len(orders)} orders")
```

Insert at least 15 orders with varying statuses and customers.

### Task 5: Query Using GSI
Query orders by status using the Global Secondary Index:

```python
# Query all "pending" orders sorted by date
response = table.query(
    IndexName='StatusDateIndex',
    KeyConditionExpression='#status = :status',
    ExpressionAttributeNames={'#status': 'status'},
    ExpressionAttributeValues={':status': 'pending'}
)

print(f"Pending orders: {len(response['Items'])}")
for order in response['Items']:
    print(f"  Order {order['order_id']}: {order['order_date']} - ${order['total_amount']}")
```

### Task 6: Query Using LSI
Query orders for a specific customer sorted by amount:

```python
# Query orders for CUST001 sorted by total_amount
response = table.query(
    IndexName='CustomerAmountIndex',
    KeyConditionExpression='customer_id = :cust_id',
    ExpressionAttributeValues={':cust_id': 'CUST001'},
    ScanIndexForward=False  # Descending order (highest amount first)
)

print(f"Orders for CUST001 (by amount):")
for order in response['Items']:
    print(f"  Order {order['order_id']}: ${order['total_amount']}")
```

### Task 7: Enable DynamoDB Streams
Enable DynamoDB Streams to capture changes:
- Go to DynamoDB console → Select table → Exports and streams
- Click "Turn on" for DynamoDB stream
- **View Type**: NEW_AND_OLD_IMAGES (captures both before and after)
- This enables real-time change tracking for audit logs, replication, or triggers

### Task 8: Create Lambda Function for Stream Processing
Create a Lambda function to process stream events:

**Function Name**: `process-orders-stream-${your-student-id}`
**Runtime**: Python 3.12
**Execution Role**: Create new role with DynamoDB stream permissions

**Code** (`lambda_function.py`):
```python
import json
import boto3

def lambda_handler(event, context):
    """Process DynamoDB stream events"""
    
    for record in event['Records']:
        event_name = record['eventName']  # INSERT, MODIFY, REMOVE
        
        if event_name == 'INSERT':
            new_image = record['dynamodb']['NewImage']
            order_id = new_image['order_id']['S']
            customer_id = new_image['customer_id']['S']
            status = new_image['status']['S']
            
            print(f"New order created: {order_id} for customer {customer_id} with status {status}")
            
        elif event_name == 'MODIFY':
            old_image = record['dynamodb']['OldImage']
            new_image = record['dynamodb']['NewImage']
            
            old_status = old_image.get('status', {}).get('S', 'unknown')
            new_status = new_image.get('status', {}).get('S', 'unknown')
            
            if old_status != new_status:
                order_id = new_image['order_id']['S']
                print(f"Order {order_id} status changed: {old_status} → {new_status}")
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Processed {len(event["Records"])} records')
    }
```

**Event Source Mapping**:
- Add trigger: DynamoDB
- DynamoDB table: `orders-${your-student-id}`
- Batch size: 10
- Starting position: LATEST

### Task 9: Implement Batch Operations
Create a script for batch read and write operations:

**File**: `batch_operations.py`

```python
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('orders-STUDENTID')

# Batch Get Items
def batch_get_orders(order_keys):
    """Get multiple orders in a single batch request"""
    response = dynamodb.batch_get_item(
        RequestItems={
            'orders-STUDENTID': {
                'Keys': order_keys
            }
        }
    )
    
    items = response['Responses']['orders-STUDENTID']
    print(f"Retrieved {len(items)} orders")
    return items

# Batch Write Items
def batch_update_status(order_keys, new_status):
    """Update multiple orders' status in batch"""
    with table.batch_writer() as batch:
        for key in order_keys:
            # Get current item
            response = table.get_item(Key=key)
            if 'Item' in response:
                item = response['Item']
                item['status'] = new_status
                batch.put_item(Item=item)
    
    print(f"Updated {len(order_keys)} orders to status: {new_status}")

# Example usage
if __name__ == "__main__":
    # Batch get
    keys_to_get = [
        {'customer_id': 'CUST001', 'order_id': 'ORD0001'},
        {'customer_id': 'CUST002', 'order_id': 'ORD0002'},
        {'customer_id': 'CUST003', 'order_id': 'ORD0003'}
    ]
    orders = batch_get_orders(keys_to_get)
    
    # Batch update
    keys_to_update = [
        {'customer_id': 'CUST001', 'order_id': 'ORD0001'}
    ]
    batch_update_status(keys_to_update, 'shipped')
```

### Task 10: Configure Time To Live (TTL)
Enable TTL for automatic data expiration:
- Go to DynamoDB console → Select table → Additional settings
- Click "Enable" for Time to Live
- **TTL Attribute**: `expiry_date`
- Items with `expiry_date` (Unix timestamp) will be automatically deleted after that time

Add TTL to some orders:
```python
import time

# Add TTL to an order (expires in 90 days)
expiry_timestamp = int(time.time()) + (90 * 24 * 60 * 60)

table.update_item(
    Key={'customer_id': 'CUST001', 'order_id': 'ORD0001'},
    UpdateExpression='SET expiry_date = :expiry',
    ExpressionAttributeValues={':expiry': expiry_timestamp}
)
```

### Task 11: Set Up CloudWatch Alarms
Create CloudWatch alarms for table monitoring:

**Alarm 1: High Read Throttling**
- Metric: `UserErrors` (ConsumedReadCapacityUnits throttling)
- Threshold: > 5 errors in 5 minutes
- Action: SNS notification

**Alarm 2: High Write Throttling**
- Metric: `UserErrors` (ConsumedWriteCapacityUnits throttling)
- Threshold: > 5 errors in 5 minutes
- Action: SNS notification

**Alarm 3: GSI Throttling**
- Metric: `ReadThrottleEvents` on StatusDateIndex
- Threshold: > 10 throttles in 5 minutes
- Action: SNS notification

### Task 12: Implement Conditional Writes
Add conditional write operations for data consistency:

```python
# Update order only if status is 'pending'
try:
    response = table.update_item(
        Key={'customer_id': 'CUST001', 'order_id': 'ORD0001'},
        UpdateExpression='SET #status = :new_status',
        ConditionExpression='#status = :current_status',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={
            ':new_status': 'processing',
            ':current_status': 'pending'
        },
        ReturnValues='ALL_NEW'
    )
    print("Order status updated successfully")
except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
    print("Condition failed: Order is not in 'pending' status")

# Prevent duplicate orders (put item only if it doesn't exist)
try:
    table.put_item(
        Item={
            'customer_id': 'CUST001',
            'order_id': 'ORD0001',
            'status': 'pending',
            'order_date': '2024-04-01',
            'total_amount': 299.99
        },
        ConditionExpression='attribute_not_exists(order_id)'
    )
except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
    print("Order already exists")
```

### Task 13: Create Read-Heavy Application Pattern
Implement eventually consistent reads for better performance:

```python
# Strong consistent read (default, latest data)
response = table.get_item(
    Key={'customer_id': 'CUST001', 'order_id': 'ORD0001'},
    ConsistentRead=True
)

# Eventually consistent read (faster, lower cost, may be stale)
response = table.get_item(
    Key={'customer_id': 'CUST001', 'order_id': 'ORD0001'},
    ConsistentRead=False  # Or omit (False is default)
)

# Query with eventually consistent read
response = table.query(
    KeyConditionExpression='customer_id = :cust_id',
    ExpressionAttributeValues={':cust_id': 'CUST001'},
    ConsistentRead=False  # Use for read-heavy workloads
)
```

## Validation

Run the validation script:

```bash
python validate_tasks.py dynamodb_medium
```

The script will verify:
- Table exists with composite key (partition + sort)
- Global Secondary Index (StatusDateIndex) is configured
- Local Secondary Index (CustomerAmountIndex) is configured
- Table has at least 15 items
- DynamoDB Streams is enabled (NEW_AND_OLD_IMAGES)
- Lambda function exists and is connected to stream
- TTL is enabled on table
- CloudWatch alarms are configured
- Tags are properly set

## Cleanup (After Assessment)
1. Delete Lambda function and its execution role
2. Delete CloudWatch alarms
3. Disable DynamoDB Streams
4. Delete table (this will also delete GSI and LSI)

## Tips
- **GSI vs LSI**:
  - GSI: Different partition key, created anytime, eventually consistent
  - LSI: Same partition key, must create with table, strongly consistent option
- Use GSI for queries with different access patterns
- LSI shares throughput with base table
- Streams have 24-hour retention
- Batch operations reduce API calls (up to 25 items)
- TTL deletes happen within 48 hours after expiration
- On-demand mode automatically handles capacity (no throttling)
- Use conditional writes to prevent race conditions
- Eventually consistent reads are 50% cheaper than consistent reads
- Project only required attributes in indexes to save storage

## Common Issues
- **ValidationException on LSI**: Must be created with table
- **GSI not queryable**: Wait for index to become ACTIVE
- **Stream Lambda not triggering**: Check event source mapping status
- **ConditionalCheckFailedException**: Condition expression not met
- **ProvisionedThroughputExceededException**: Shouldn't happen with on-demand, but possible during rapid scaling

## Learning Resources
- Global Secondary Indexes (GSI) for flexible querying
- Local Secondary Indexes (LSI) for alternate sort keys
- DynamoDB Streams for change data capture
- Lambda triggers for stream processing
- Batch operations for efficiency
- Time To Live (TTL) for automatic data expiration
- Conditional expressions for consistency
- Eventually consistent vs strongly consistent reads
- Projection expressions to reduce data transfer
