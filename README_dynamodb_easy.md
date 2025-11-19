# AWS DynamoDB Assessment - NoSQL Database Basics (Easy)

github-repo: https://github.com/sharedlabs1/s3assessment

## Difficulty Level: 🟢 Easy

## Scenario
You are a backend engineer at StartupCo. Set up a DynamoDB table to store user data and implement basic CRUD operations for a web application.

## Prerequisites
- Access to the shared AWS training account
- Python 3.8+ installed
- GitHub CLI (`gh`) installed
- Basic understanding of NoSQL databases and key-value stores

## Setup

1. **Download the assessment files** (you only need these 3 files):
   - `validate_tasks.py`
   - `requirements.txt`
   - `README_dynamodb_easy.md`

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

That's it! You're ready to start the assessment.

## Tasks to Complete

### Task 1: Create DynamoDB Table
Create a DynamoDB table for user data:
- **Table Name**: `users-${your-student-id}`
- **Partition Key**: `user_id` (String)
- **Billing Mode**: On-Demand (PAY_PER_REQUEST)
- **Table Class**: Standard
- **Deletion Protection**: Disabled (for learning purposes)

Add tags: `Environment=Development`, `Application=UserManagement`, `StudentID=${your-student-id}`

### Task 2: Add Items to Table
Insert sample user records using AWS Console or AWS CLI:

**User 1:**
```json
{
  "user_id": "user001",
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "age": 30,
  "city": "New York",
  "status": "active",
  "created_at": "2024-01-15T10:00:00Z"
}
```

**User 2:**
```json
{
  "user_id": "user002",
  "username": "jane_smith",
  "email": "jane@example.com",
  "full_name": "Jane Smith",
  "age": 28,
  "city": "San Francisco",
  "status": "active",
  "created_at": "2024-02-20T14:30:00Z"
}
```

**User 3:**
```json
{
  "user_id": "user003",
  "username": "bob_johnson",
  "email": "bob@example.com",
  "full_name": "Bob Johnson",
  "age": 35,
  "city": "Chicago",
  "status": "inactive",
  "created_at": "2024-03-10T09:15:00Z"
}
```

Insert at least 3 user records.

### Task 3: Perform Query Operations
Use AWS CLI or SDK to query data:

**Get item by user_id:**
```bash
aws dynamodb get-item \
    --table-name users-STUDENTID \
    --key '{"user_id": {"S": "user001"}}'
```

**Scan table (retrieve all items):**
```bash
aws dynamodb scan \
    --table-name users-STUDENTID
```

Verify you can retrieve items successfully.

### Task 4: Update Item
Update a user's information:

**Update user status:**
```bash
aws dynamodb update-item \
    --table-name users-STUDENTID \
    --key '{"user_id": {"S": "user001"}}' \
    --update-expression "SET #status = :new_status, age = :new_age" \
    --expression-attribute-names '{"#status": "status"}' \
    --expression-attribute-values '{":new_status": {"S": "premium"}, ":new_age": {"N": "31"}}'
```

Verify the item was updated successfully.

### Task 5: Delete Item
Delete a user from the table:

```bash
aws dynamodb delete-item \
    --table-name users-STUDENTID \
    --key '{"user_id": {"S": "user003"}}'
```

Verify the item was deleted.

### Task 6: Enable Point-in-Time Recovery
Enable point-in-time recovery for backup protection:
- Go to DynamoDB console → Select table → Backups tab
- Enable Point-in-Time Recovery (PITR)
- This allows restoration to any point within the last 35 days

### Task 7: Create Python Script for CRUD Operations
Create a Python script to perform CRUD operations:

**File**: `dynamodb_operations.py`

```python
import boto3
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table_name = 'users-STUDENTID'  # Replace with your student ID
table = dynamodb.Table(table_name)

# Create (Put Item)
def create_user(user_id, username, email, full_name, age, city):
    response = table.put_item(
        Item={
            'user_id': user_id,
            'username': username,
            'email': email,
            'full_name': full_name,
            'age': age,
            'city': city,
            'status': 'active',
            'created_at': datetime.utcnow().isoformat()
        }
    )
    print(f"User {user_id} created successfully")
    return response

# Read (Get Item)
def get_user(user_id):
    response = table.get_item(Key={'user_id': user_id})
    if 'Item' in response:
        print(f"User found: {response['Item']}")
        return response['Item']
    else:
        print(f"User {user_id} not found")
        return None

# Update (Update Item)
def update_user_status(user_id, new_status):
    response = table.update_item(
        Key={'user_id': user_id},
        UpdateExpression='SET #status = :status',
        ExpressionAttributeNames={'#status': 'status'},
        ExpressionAttributeValues={':status': new_status},
        ReturnValues='ALL_NEW'
    )
    print(f"User {user_id} updated: {response['Attributes']}")
    return response

# Delete (Delete Item)
def delete_user(user_id):
    response = table.delete_item(Key={'user_id': user_id})
    print(f"User {user_id} deleted successfully")
    return response

# List all users (Scan)
def list_all_users():
    response = table.scan()
    users = response['Items']
    print(f"Total users: {len(users)}")
    for user in users:
        print(f"  - {user['username']} ({user['email']})")
    return users

# Example usage
if __name__ == "__main__":
    # Create
    create_user('user004', 'alice_wonder', 'alice@example.com', 'Alice Wonder', 26, 'Boston')
    
    # Read
    get_user('user004')
    
    # Update
    update_user_status('user004', 'premium')
    
    # List
    list_all_users()
    
    # Delete (commented out to preserve data)
    # delete_user('user004')
```

Upload this script to S3 or save locally and test it.

### Task 8: Monitor Table Metrics
Check table metrics in CloudWatch:
- Go to DynamoDB console → Select table → Metrics tab
- Review metrics:
  - Read/Write Capacity Units consumed
  - Throttled requests (should be 0)
  - User errors
  - System errors

Verify your table is operating without errors.

## Validation

Once you've completed all tasks, run the validation script:

```bash
python validate_tasks.py dynamodb_easy
```

The script will verify:
- Table exists with correct configuration
- Partition key is properly configured
- Table has items (at least 2)
- Point-in-Time Recovery is enabled
- Tags are properly set
- Table is accessible and operational

## Cleanup (After Assessment)
1. Delete all items from the table (optional)
2. Disable Point-in-Time Recovery
3. Delete the table
4. Remove any test scripts from S3

## Tips
- DynamoDB is fully managed - no server provisioning needed
- On-Demand billing is great for unpredictable workloads
- Partition key determines data distribution across partitions
- Use UpdateExpression for atomic updates
- Scan operations read entire table - use Query when possible
- Each item can have different attributes (schema-less)
- DynamoDB automatically scales based on demand
- Item size limit is 400 KB
- Use consistent reads when you need latest data immediately

## Common Issues
- **ConditionalCheckFailedException**: Item doesn't meet condition
- **ValidationException**: Invalid attribute names or values
- **ResourceNotFoundException**: Table doesn't exist
- **ProvisionedThroughputExceededException**: Too many requests (shouldn't happen with on-demand)
- **ItemCollectionSizeLimitExceededException**: Collection exceeds 10 GB

## Learning Resources
- DynamoDB core components (tables, items, attributes)
- Primary keys (partition key and sort key)
- Read/write capacity modes (on-demand vs provisioned)
- DynamoDB data types
- Conditional expressions
- Atomic counters
- Time To Live (TTL)
