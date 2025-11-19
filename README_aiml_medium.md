# AWS AI/ML Services Assessment - Medium

## Overview
Dive deeper into AWS machine learning by building, training, and deploying custom models with Amazon SageMaker. Learn to use built-in algorithms, create training jobs, deploy models to endpoints, and integrate ML predictions into applications.

**Difficulty**: Medium  
**Prerequisites**: Completion of AI/ML Easy assessment, Python programming  
**Estimated Time**: 3-4 hours  

## Learning Objectives
- Use Amazon SageMaker for custom ML model training
- Work with SageMaker built-in algorithms
- Train models using provided datasets
- Deploy models to real-time endpoints
- Make predictions via SageMaker endpoints
- Manage SageMaker notebook instances
- Use SageMaker Feature Store
- Implement model versioning

## Prerequisites
- Completed AI/ML Easy assessment
- Python 3.8+ with boto3, pandas, scikit-learn
- S3 bucket for training data and model artifacts
- Basic understanding of machine learning concepts

---

## Tasks

### Task 1: SageMaker S3 Bucket Setup
**Objective**: Create S3 bucket structure for SageMaker training data and models.

```bash
# Create SageMaker bucket
aws s3 mb s3://sagemaker-{student_id}

# Create folder structure
aws s3api put-object --bucket sagemaker-{student_id} --key data/training/
aws s3api put-object --bucket sagemaker-{student_id} --key data/validation/
aws s3api put-object --bucket sagemaker-{student_id} --key data/test/
aws s3api put-object --bucket sagemaker-{student_id} --key models/
aws s3api put-object --bucket sagemaker-{student_id} --key output/
aws s3api put-object --bucket sagemaker-{student_id} --key features/
```

---

### Task 2: Prepare Training Dataset
**Objective**: Create and upload a sample dataset for ML training.

**Python script** (`scripts/prepare_dataset.py`):
```python
import pandas as pd
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
import boto3
import io

def create_sample_dataset(student_id):
    """Create a binary classification dataset"""
    
    # Generate synthetic dataset
    X, y = make_classification(
        n_samples=1000,
        n_features=10,
        n_informative=8,
        n_redundant=2,
        n_classes=2,
        random_state=42
    )
    
    # Create DataFrame
    feature_names = [f'feature_{i}' for i in range(10)]
    df = pd.DataFrame(X, columns=feature_names)
    df['target'] = y
    
    # Split data
    train_df, temp_df = train_test_split(df, test_size=0.3, random_state=42)
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42)
    
    print(f"Training samples: {len(train_df)}")
    print(f"Validation samples: {len(val_df)}")
    print(f"Test samples: {len(test_df)}")
    
    # Upload to S3
    s3 = boto3.client('s3')
    bucket = f"sagemaker-{student_id}"
    
    for name, data in [('training', train_df), ('validation', val_df), ('test', test_df)]:
        csv_buffer = io.StringIO()
        data.to_csv(csv_buffer, index=False, header=False)
        
        s3.put_object(
            Bucket=bucket,
            Key=f'data/{name}/data.csv',
            Body=csv_buffer.getvalue()
        )
        print(f"Uploaded: s3://{bucket}/data/{name}/data.csv")
    
    return train_df, val_df, test_df

if __name__ == "__main__":
    import sys
    student_id = sys.argv[1]
    create_sample_dataset(student_id)
```

**Run**:
```bash
python scripts/prepare_dataset.py {student_id}
```

---

### Task 3: IAM Role for SageMaker
**Objective**: Create IAM role with permissions for SageMaker operations.

```bash
# Trust policy
cat > sagemaker-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "sagemaker.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name SageMakerExecutionRole-{student_id} \
  --assume-role-policy-document file://sagemaker-trust-policy.json

# Attach managed policy
aws iam attach-role-policy \
  --role-name SageMakerExecutionRole-{student_id} \
  --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess

# Add S3 access
aws iam attach-role-policy \
  --role-name SageMakerExecutionRole-{student_id} \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# Get role ARN
aws iam get-role \
  --role-name SageMakerExecutionRole-{student_id} \
  --query 'Role.Arn' \
  --output text
```

---

### Task 4: SageMaker Training Job with Built-in Algorithm
**Objective**: Train a model using SageMaker's built-in XGBoost algorithm.

**Python script** (`scripts/train_xgboost.py`):
```python
import boto3
import sagemaker
from sagemaker import get_execution_role
from sagemaker.inputs import TrainingInput
import time

def train_xgboost_model(student_id, role_arn):
    """Train XGBoost model using SageMaker"""
    
    # Initialize SageMaker session
    sagemaker_session = sagemaker.Session()
    region = boto3.Session().region_name
    
    # Get XGBoost container
    from sagemaker import image_uris
    container = image_uris.retrieve('xgboost', region, version='1.5-1')
    
    # S3 paths
    bucket = f"sagemaker-{student_id}"
    s3_train = f's3://{bucket}/data/training/'
    s3_val = f's3://{bucket}/data/validation/'
    s3_output = f's3://{bucket}/output/'
    
    # Create SageMaker client
    sagemaker_client = boto3.client('sagemaker')
    
    # Training job configuration
    training_job_name = f'xgboost-training-{student_id}-{int(time.time())}'
    
    training_params = {
        'TrainingJobName': training_job_name,
        'RoleArn': role_arn,
        'AlgorithmSpecification': {
            'TrainingImage': container,
            'TrainingInputMode': 'File'
        },
        'InputDataConfig': [
            {
                'ChannelName': 'train',
                'DataSource': {
                    'S3DataSource': {
                        'S3DataType': 'S3Prefix',
                        'S3Uri': s3_train,
                        'S3DataDistributionType': 'FullyReplicated'
                    }
                },
                'ContentType': 'text/csv'
            },
            {
                'ChannelName': 'validation',
                'DataSource': {
                    'S3DataSource': {
                        'S3DataType': 'S3Prefix',
                        'S3Uri': s3_val,
                        'S3DataDistributionType': 'FullyReplicated'
                    }
                },
                'ContentType': 'text/csv'
            }
        ],
        'OutputDataConfig': {
            'S3OutputPath': s3_output
        },
        'ResourceConfig': {
            'InstanceType': 'ml.m5.xlarge',
            'InstanceCount': 1,
            'VolumeSizeInGB': 10
        },
        'HyperParameters': {
            'objective': 'binary:logistic',
            'num_round': '100',
            'max_depth': '5',
            'eta': '0.2',
            'subsample': '0.8',
            'colsample_bytree': '0.8'
        },
        'StoppingCondition': {
            'MaxRuntimeInSeconds': 3600
        }
    }
    
    # Start training job
    print(f"Starting training job: {training_job_name}")
    sagemaker_client.create_training_job(**training_params)
    
    # Wait for completion
    print("Waiting for training to complete...")
    while True:
        response = sagemaker_client.describe_training_job(
            TrainingJobName=training_job_name
        )
        status = response['TrainingJobStatus']
        print(f"Status: {status}")
        
        if status in ['Completed', 'Failed', 'Stopped']:
            break
        
        time.sleep(30)
    
    if status == 'Completed':
        print(f"\n✅ Training completed successfully!")
        print(f"Model artifact: {response['ModelArtifacts']['S3ModelArtifacts']}")
        
        # Save training job info
        import json
        with open(f'training-job-{student_id}.json', 'w') as f:
            json.dump({
                'job_name': training_job_name,
                'status': status,
                'model_artifact': response['ModelArtifacts']['S3ModelArtifacts']
            }, f, indent=2)
        
        return training_job_name
    else:
        print(f"\n❌ Training failed with status: {status}")
        if 'FailureReason' in response:
            print(f"Reason: {response['FailureReason']}")
        return None

if __name__ == "__main__":
    import sys
    student_id = sys.argv[1]
    role_arn = sys.argv[2]  # Pass role ARN from Task 3
    train_xgboost_model(student_id, role_arn)
```

**Run**:
```bash
# Get role ARN first
ROLE_ARN=$(aws iam get-role --role-name SageMakerExecutionRole-{student_id} --query 'Role.Arn' --output text)

# Train model
python scripts/train_xgboost.py {student_id} $ROLE_ARN
```

---

### Task 5: Create SageMaker Model
**Objective**: Create a SageMaker model from trained artifacts.

**Python script** (`scripts/create_model.py`):
```python
import boto3
import json

def create_sagemaker_model(student_id, role_arn, training_job_name):
    """Create SageMaker model from training job"""
    
    sagemaker_client = boto3.client('sagemaker')
    region = boto3.Session().region_name
    
    # Get training job details
    training_job = sagemaker_client.describe_training_job(
        TrainingJobName=training_job_name
    )
    
    model_data = training_job['ModelArtifacts']['S3ModelArtifacts']
    container = training_job['AlgorithmSpecification']['TrainingImage']
    
    # Create model
    model_name = f'xgboost-model-{student_id}'
    
    try:
        response = sagemaker_client.create_model(
            ModelName=model_name,
            PrimaryContainer={
                'Image': container,
                'ModelDataUrl': model_data
            },
            ExecutionRoleArn=role_arn
        )
        
        print(f"✅ Model created: {model_name}")
        print(f"Model ARN: {response['ModelArn']}")
        
        # Save model info
        with open(f'sagemaker-model-{student_id}.json', 'w') as f:
            json.dump({
                'model_name': model_name,
                'model_arn': response['ModelArn'],
                'model_data': model_data
            }, f, indent=2)
        
        return model_name
        
    except Exception as e:
        print(f"❌ Error creating model: {e}")
        return None

if __name__ == "__main__":
    import sys
    student_id = sys.argv[1]
    role_arn = sys.argv[2]
    training_job_name = sys.argv[3]
    
    create_sagemaker_model(student_id, role_arn, training_job_name)
```

---

### Task 6: Deploy Model to Endpoint
**Objective**: Deploy the trained model to a real-time inference endpoint.

**Python script** (`scripts/deploy_endpoint.py`):
```python
import boto3
import time
import json

def deploy_endpoint(student_id, model_name, role_arn):
    """Deploy model to SageMaker endpoint"""
    
    sagemaker_client = boto3.client('sagemaker')
    
    endpoint_config_name = f'xgboost-config-{student_id}'
    endpoint_name = f'xgboost-endpoint-{student_id}'
    
    # Create endpoint configuration
    try:
        print(f"Creating endpoint configuration: {endpoint_config_name}")
        sagemaker_client.create_endpoint_config(
            EndpointConfigName=endpoint_config_name,
            ProductionVariants=[
                {
                    'VariantName': 'AllTraffic',
                    'ModelName': model_name,
                    'InstanceType': 'ml.m5.xlarge',
                    'InitialInstanceCount': 1,
                    'InitialVariantWeight': 1.0
                }
            ]
        )
        print("✅ Endpoint configuration created")
        
    except Exception as e:
        if 'already exists' in str(e):
            print("⚠️  Endpoint configuration already exists")
        else:
            print(f"❌ Error creating endpoint config: {e}")
            return None
    
    # Create endpoint
    try:
        print(f"\nCreating endpoint: {endpoint_name}")
        sagemaker_client.create_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=endpoint_config_name
        )
        
        # Wait for endpoint to be in service
        print("Waiting for endpoint to be in service...")
        while True:
            response = sagemaker_client.describe_endpoint(
                EndpointName=endpoint_name
            )
            status = response['EndpointStatus']
            print(f"Status: {status}")
            
            if status in ['InService', 'Failed']:
                break
            
            time.sleep(30)
        
        if status == 'InService':
            print(f"\n✅ Endpoint is in service!")
            print(f"Endpoint name: {endpoint_name}")
            
            # Save endpoint info
            with open(f'sagemaker-endpoint-{student_id}.json', 'w') as f:
                json.dump({
                    'endpoint_name': endpoint_name,
                    'endpoint_config': endpoint_config_name,
                    'status': status
                }, f, indent=2)
            
            return endpoint_name
        else:
            print(f"\n❌ Endpoint deployment failed")
            if 'FailureReason' in response:
                print(f"Reason: {response['FailureReason']}")
            return None
            
    except Exception as e:
        if 'already exists' in str(e):
            print("⚠️  Endpoint already exists")
            return endpoint_name
        else:
            print(f"❌ Error creating endpoint: {e}")
            return None

if __name__ == "__main__":
    import sys
    student_id = sys.argv[1]
    model_name = sys.argv[2]
    role_arn = sys.argv[3]
    
    deploy_endpoint(student_id, model_name, role_arn)
```

---

### Task 7: Make Predictions
**Objective**: Use the deployed endpoint for real-time predictions.

**Python script** (`scripts/make_predictions.py`):
```python
import boto3
import numpy as np
import json

def make_predictions(student_id, endpoint_name):
    """Make predictions using SageMaker endpoint"""
    
    runtime = boto3.client('sagemaker-runtime')
    
    # Generate sample data (10 features)
    sample_data = np.random.randn(5, 10)
    
    predictions = []
    
    print("Making predictions...")
    for i, row in enumerate(sample_data):
        # Format data as CSV (XGBoost expects CSV)
        payload = ','.join(map(str, row))
        
        try:
            response = runtime.invoke_endpoint(
                EndpointName=endpoint_name,
                ContentType='text/csv',
                Body=payload
            )
            
            result = response['Body'].read().decode()
            prediction = float(result)
            
            print(f"Sample {i+1}: Prediction = {prediction:.4f}")
            predictions.append({
                'sample': i+1,
                'input': row.tolist(),
                'prediction': prediction
            })
            
        except Exception as e:
            print(f"❌ Error making prediction for sample {i+1}: {e}")
    
    # Save predictions
    with open(f'predictions-{student_id}.json', 'w') as f:
        json.dump(predictions, f, indent=2)
    
    print(f"\n✅ Predictions saved to predictions-{student_id}.json")
    return predictions

if __name__ == "__main__":
    import sys
    student_id = sys.argv[1]
    endpoint_name = f'xgboost-endpoint-{student_id}'
    
    make_predictions(student_id, endpoint_name)
```

---

### Task 8: SageMaker Notebook Instance (Optional)
**Objective**: Create a SageMaker notebook instance for interactive development.

```bash
# Get role ARN
ROLE_ARN=$(aws iam get-role --role-name SageMakerExecutionRole-{student_id} --query 'Role.Arn' --output text)

# Create notebook instance
aws sagemaker create-notebook-instance \
  --notebook-instance-name notebook-{student_id} \
  --instance-type ml.t3.medium \
  --role-arn $ROLE_ARN

# Wait for instance to be in service
aws sagemaker wait notebook-instance-in-service \
  --notebook-instance-name notebook-{student_id}

# Get notebook URL
aws sagemaker create-presigned-notebook-instance-url \
  --notebook-instance-name notebook-{student_id}
```

---

### Task 9: Model Monitoring Setup
**Objective**: Set up basic model monitoring to track endpoint performance.

**Python script** (`scripts/monitor_endpoint.py`):
```python
import boto3
import json
from datetime import datetime, timedelta

def monitor_endpoint(student_id, endpoint_name):
    """Monitor endpoint metrics"""
    
    cloudwatch = boto3.client('cloudwatch')
    
    # Get metrics for last hour
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)
    
    metrics_to_check = [
        'ModelLatency',
        'Invocations',
        'InvocationErrors'
    ]
    
    results = {}
    
    for metric_name in metrics_to_check:
        try:
            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/SageMaker',
                MetricName=metric_name,
                Dimensions=[
                    {'Name': 'EndpointName', 'Value': endpoint_name},
                    {'Name': 'VariantName', 'Value': 'AllTraffic'}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,  # 5 minutes
                Statistics=['Average', 'Sum', 'Maximum']
            )
            
            if response['Datapoints']:
                latest = sorted(response['Datapoints'], 
                              key=lambda x: x['Timestamp'])[-1]
                results[metric_name] = {
                    'average': latest.get('Average'),
                    'sum': latest.get('Sum'),
                    'maximum': latest.get('Maximum'),
                    'timestamp': latest['Timestamp'].isoformat()
                }
                print(f"{metric_name}:")
                print(f"  Average: {latest.get('Average')}")
                print(f"  Sum: {latest.get('Sum')}")
                print(f"  Maximum: {latest.get('Maximum')}")
            else:
                results[metric_name] = None
                print(f"{metric_name}: No data available")
            
        except Exception as e:
            print(f"Error getting {metric_name}: {e}")
            results[metric_name] = None
    
    # Save monitoring results
    with open(f'endpoint-monitoring-{student_id}.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    return results

if __name__ == "__main__":
    import sys
    student_id = sys.argv[1]
    endpoint_name = f'xgboost-endpoint-{student_id}'
    
    monitor_endpoint(student_id, endpoint_name)
```

---

### Task 10: Cleanup Resources
**Objective**: Delete SageMaker resources to avoid ongoing costs.

**Python script** (`scripts/cleanup_sagemaker.py`):
```python
import boto3

def cleanup_sagemaker_resources(student_id):
    """Delete SageMaker endpoint, config, and model"""
    
    sagemaker_client = boto3.client('sagemaker')
    
    endpoint_name = f'xgboost-endpoint-{student_id}'
    endpoint_config_name = f'xgboost-config-{student_id}'
    model_name = f'xgboost-model-{student_id}'
    notebook_name = f'notebook-{student_id}'
    
    # Delete endpoint
    try:
        print(f"Deleting endpoint: {endpoint_name}")
        sagemaker_client.delete_endpoint(EndpointName=endpoint_name)
        print("✅ Endpoint deleted")
    except Exception as e:
        print(f"⚠️  Endpoint: {e}")
    
    # Delete endpoint config
    try:
        print(f"Deleting endpoint config: {endpoint_config_name}")
        sagemaker_client.delete_endpoint_config(
            EndpointConfigName=endpoint_config_name
        )
        print("✅ Endpoint config deleted")
    except Exception as e:
        print(f"⚠️  Endpoint config: {e}")
    
    # Delete model
    try:
        print(f"Deleting model: {model_name}")
        sagemaker_client.delete_model(ModelName=model_name)
        print("✅ Model deleted")
    except Exception as e:
        print(f"⚠️  Model: {e}")
    
    # Delete notebook instance (if exists)
    try:
        print(f"Deleting notebook: {notebook_name}")
        sagemaker_client.stop_notebook_instance(
            NotebookInstanceName=notebook_name
        )
        sagemaker_client.wait_notebook_instance_stopped(
            NotebookInstanceName=notebook_name
        )
        sagemaker_client.delete_notebook_instance(
            NotebookInstanceName=notebook_name
        )
        print("✅ Notebook deleted")
    except Exception as e:
        print(f"⚠️  Notebook: {e}")
    
    print("\n✅ Cleanup completed!")

if __name__ == "__main__":
    import sys
    student_id = sys.argv[1]
    
    response = input(f"Are you sure you want to delete all SageMaker resources? (yes/no): ")
    if response.lower() == 'yes':
        cleanup_sagemaker_resources(student_id)
    else:
        print("Cleanup cancelled")
```

---

## Validation Commands

```bash
# Check S3 bucket
aws s3 ls s3://sagemaker-{student_id}/ --recursive

# List training jobs
aws sagemaker list-training-jobs --name-contains {student_id}

# List models
aws sagemaker list-models --name-contains {student_id}

# List endpoints
aws sagemaker list-endpoints --name-contains {student_id}

# Check endpoint status
aws sagemaker describe-endpoint --endpoint-name xgboost-endpoint-{student_id}
```

---

## Success Criteria

✅ **S3 Bucket**: sagemaker-{student_id} with training data  
✅ **IAM Role**: SageMakerExecutionRole created  
✅ **Training Job**: XGBoost model trained successfully  
✅ **Model**: SageMaker model created from artifacts  
✅ **Endpoint**: Model deployed to InService endpoint  
✅ **Predictions**: Real-time predictions working  
✅ **Monitoring**: CloudWatch metrics accessible  
✅ **Scripts**: All Python scripts functional  

---

## Testing Your Work

Run the validation script:
```bash
python validate_tasks.py aiml_medium
```

**Minimum passing score**: 70% (7 out of 10 tasks)

---

## Cost Considerations

**SageMaker Pricing**:
- Training: ~$0.30/hour (ml.m5.xlarge)
- Endpoint: ~$0.30/hour (ml.m5.xlarge)
- Notebook: ~$0.06/hour (ml.t3.medium)

**Important**: Delete endpoint when done to avoid ongoing charges!

**Estimated Cost**: $1-3 for this assessment (with cleanup)

---

## Additional Resources

- [Amazon SageMaker Documentation](https://docs.aws.amazon.com/sagemaker/)
- [SageMaker Python SDK](https://sagemaker.readthedocs.io/)
- [Built-in Algorithms](https://docs.aws.amazon.com/sagemaker/latest/dg/algos.html)

---

**Good luck with your AI/ML Medium assessment!** 🚀
