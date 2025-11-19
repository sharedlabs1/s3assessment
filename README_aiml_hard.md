# AWS AI/ML Services Assessment - Hard

## Overview
Master advanced Amazon SageMaker features including ML pipelines, batch transform jobs, model monitoring, hyperparameter tuning, and MLOps best practices. Build production-ready machine learning systems with automated workflows, monitoring, and CI/CD.

**Difficulty**: Hard  
**Prerequisites**: AI/ML Medium completion, SageMaker experience, Python proficiency  
**Estimated Time**: 4-5 hours  

## Learning Objectives
- Build end-to-end ML pipelines with SageMaker Pipelines
- Implement hyperparameter tuning for model optimization
- Deploy batch inference with Batch Transform
- Set up model monitoring for data and model quality drift
- Use SageMaker Clarify for bias detection
- Implement MLOps with CI/CD pipelines
- Manage model lifecycle with Model Registry
- Optimize costs with multi-model endpoints

## Prerequisites
- Completed AI/ML Medium assessment
- SageMaker endpoint from medium assessment
- Python 3.8+ with sagemaker SDK
- Understanding of ML workflows

---

## Tasks

### Task 1: SageMaker Pipeline Creation
**Objective**: Create an ML pipeline with preprocessing, training, and evaluation steps.

**Pipeline components**:
1. Data preprocessing step
2. Model training step
3. Model evaluation step
4. Conditional registration step

**Python script** (`scripts/create_pipeline.py`):
```python
import boto3
import sagemaker
from sagemaker.workflow.pipeline import Pipeline
from sagemaker.workflow.steps import ProcessingStep, TrainingStep
from sagemaker.workflow.parameters import ParameterString
from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.inputs import TrainingInput
from sagemaker.workflow.properties import PropertyFile
from sagemaker.workflow.conditions import ConditionGreaterThanOrEqualTo
from sagemaker.workflow.condition_step import ConditionStep
from sagemaker.workflow.functions import JsonGet
from sagemaker import image_uris
import json

def create_ml_pipeline(student_id, role_arn):
    """Create SageMaker Pipeline"""
    
    region = boto3.Session().region_name
    sagemaker_session = sagemaker.Session()
    
    # Parameters
    input_data = ParameterString(
        name="InputData",
        default_value=f"s3://sagemaker-{student_id}/data/training/"
    )
    
    model_approval_status = ParameterString(
        name="ModelApprovalStatus",
        default_value="PendingManualApproval"
    )
    
    # Step 1: Preprocessing
    sklearn_processor = SKLearnProcessor(
        framework_version='1.0-1',
        role=role_arn,
        instance_type='ml.m5.xlarge',
        instance_count=1,
        sagemaker_session=sagemaker_session
    )
    
    processing_step = ProcessingStep(
        name="PreprocessData",
        processor=sklearn_processor,
        inputs=[
            sagemaker.processing.ProcessingInput(
                source=input_data,
                destination="/opt/ml/processing/input"
            )
        ],
        outputs=[
            sagemaker.processing.ProcessingOutput(
                output_name="train",
                source="/opt/ml/processing/train",
                destination=f"s3://sagemaker-{student_id}/pipeline/train/"
            ),
            sagemaker.processing.ProcessingOutput(
                output_name="validation",
                source="/opt/ml/processing/validation",
                destination=f"s3://sagemaker-{student_id}/pipeline/validation/"
            ),
            sagemaker.processing.ProcessingOutput(
                output_name="test",
                source="/opt/ml/processing/test",
                destination=f"s3://sagemaker-{student_id}/pipeline/test/"
            )
        ],
        code=f"s3://sagemaker-{student_id}/scripts/preprocessing.py"
    )
    
    # Step 2: Training
    xgboost_image = image_uris.retrieve('xgboost', region, version='1.5-1')
    
    xgb_estimator = sagemaker.estimator.Estimator(
        image_uri=xgboost_image,
        role=role_arn,
        instance_count=1,
        instance_type='ml.m5.xlarge',
        output_path=f"s3://sagemaker-{student_id}/pipeline/models/",
        sagemaker_session=sagemaker_session
    )
    
    xgb_estimator.set_hyperparameters(
        objective='binary:logistic',
        num_round=100,
        max_depth=5,
        eta=0.2
    )
    
    training_step = TrainingStep(
        name="TrainModel",
        estimator=xgb_estimator,
        inputs={
            "train": TrainingInput(
                s3_data=processing_step.properties.ProcessingOutputConfig.Outputs["train"].S3Output.S3Uri,
                content_type="text/csv"
            ),
            "validation": TrainingInput(
                s3_data=processing_step.properties.ProcessingOutputConfig.Outputs["validation"].S3Output.S3Uri,
                content_type="text/csv"
            )
        }
    )
    
    # Create pipeline
    pipeline = Pipeline(
        name=f"MLPipeline-{student_id}",
        parameters=[input_data, model_approval_status],
        steps=[processing_step, training_step]
    )
    
    # Create or update pipeline
    pipeline.upsert(role_arn=role_arn)
    
    print(f"✅ Pipeline created: {pipeline.name}")
    
    # Save pipeline info
    with open(f'pipeline-{student_id}.json', 'w') as f:
        json.dump({
            'pipeline_name': pipeline.name,
            'pipeline_arn': pipeline.describe()['PipelineArn']
        }, f, indent=2)
    
    return pipeline.name

if __name__ == "__main__":
    import sys
    student_id = sys.argv[1]
    role_arn = sys.argv[2]
    create_ml_pipeline(student_id, role_arn)
```

**Create preprocessing script** (`scripts/preprocessing.py`):
```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import os

if __name__ == "__main__":
    # Read input data
    input_path = "/opt/ml/processing/input"
    output_path_train = "/opt/ml/processing/train"
    output_path_val = "/opt/ml/processing/validation"
    output_path_test = "/opt/ml/processing/test"
    
    # Create output directories
    os.makedirs(output_path_train, exist_ok=True)
    os.makedirs(output_path_val, exist_ok=True)
    os.makedirs(output_path_test, exist_ok=True)
    
    # Load data
    df = pd.read_csv(f"{input_path}/data.csv")
    
    # Split data
    train, temp = train_test_split(df, test_size=0.3, random_state=42)
    val, test = train_test_split(temp, test_size=0.5, random_state=42)
    
    # Save splits
    train.to_csv(f"{output_path_train}/train.csv", index=False, header=False)
    val.to_csv(f"{output_path_val}/validation.csv", index=False, header=False)
    test.to_csv(f"{output_path_test}/test.csv", index=False, header=False)
    
    print(f"Preprocessing complete: {len(train)} train, {len(val)} val, {len(test)} test")
```

**Upload and run**:
```bash
# Upload preprocessing script
aws s3 cp scripts/preprocessing.py s3://sagemaker-{student_id}/scripts/

# Run pipeline
python scripts/create_pipeline.py {student_id} $ROLE_ARN

# Execute pipeline
aws sagemaker start-pipeline-execution \
  --pipeline-name MLPipeline-{student_id}
```

---

### Task 2: Hyperparameter Tuning Job
**Objective**: Find optimal hyperparameters using SageMaker Hyperparameter Tuning.

**Python script** (`scripts/hyperparameter_tuning.py`):
```python
import boto3
import sagemaker
from sagemaker.tuner import HyperparameterTuner, IntegerParameter, ContinuousParameter
from sagemaker import image_uris
import json
import time

def create_tuning_job(student_id, role_arn):
    """Create hyperparameter tuning job"""
    
    region = boto3.Session().region_name
    sagemaker_session = sagemaker.Session()
    
    # XGBoost estimator
    xgboost_image = image_uris.retrieve('xgboost', region, version='1.5-1')
    
    xgb_estimator = sagemaker.estimator.Estimator(
        image_uri=xgboost_image,
        role=role_arn,
        instance_count=1,
        instance_type='ml.m5.xlarge',
        output_path=f"s3://sagemaker-{student_id}/tuning/models/",
        sagemaker_session=sagemaker_session
    )
    
    xgb_estimator.set_hyperparameters(
        objective='binary:logistic',
        num_round=100
    )
    
    # Hyperparameter ranges
    hyperparameter_ranges = {
        'max_depth': IntegerParameter(3, 10),
        'eta': ContinuousParameter(0.01, 0.3),
        'subsample': ContinuousParameter(0.5, 1.0),
        'colsample_bytree': ContinuousParameter(0.5, 1.0),
        'min_child_weight': IntegerParameter(1, 10)
    }
    
    # Objective metric
    objective_metric_name = 'validation:auc'
    
    # Create tuner
    tuner = HyperparameterTuner(
        estimator=xgb_estimator,
        objective_metric_name=objective_metric_name,
        hyperparameter_ranges=hyperparameter_ranges,
        max_jobs=10,
        max_parallel_jobs=2,
        objective_type='Maximize'
    )
    
    # Training data
    train_input = sagemaker.inputs.TrainingInput(
        s3_data=f"s3://sagemaker-{student_id}/data/training/",
        content_type='text/csv'
    )
    
    val_input = sagemaker.inputs.TrainingInput(
        s3_data=f"s3://sagemaker-{student_id}/data/validation/",
        content_type='text/csv'
    )
    
    # Start tuning
    tuning_job_name = f'xgboost-tuning-{student_id}-{int(time.time())}'
    tuner.fit(
        inputs={'train': train_input, 'validation': val_input},
        job_name=tuning_job_name
    )
    
    print(f"✅ Tuning job started: {tuning_job_name}")
    
    # Save tuning job info
    with open(f'tuning-job-{student_id}.json', 'w') as f:
        json.dump({
            'tuning_job_name': tuning_job_name,
            'status': 'InProgress'
        }, f, indent=2)
    
    return tuning_job_name

if __name__ == "__main__":
    import sys
    student_id = sys.argv[1]
    role_arn = sys.argv[2]
    create_tuning_job(student_id, role_arn)
```

**Check tuning results**:
```bash
python scripts/hyperparameter_tuning.py {student_id} $ROLE_ARN

# Check status
aws sagemaker describe-hyper-parameter-tuning-job \
  --hyper-parameter-tuning-job-name xgboost-tuning-{student_id}-<timestamp>

# Get best training job
aws sagemaker describe-hyper-parameter-tuning-job \
  --hyper-parameter-tuning-job-name xgboost-tuning-{student_id}-<timestamp> \
  --query 'BestTrainingJob'
```

---

### Task 3: Batch Transform Job
**Objective**: Perform batch inference on large datasets.

**Python script** (`scripts/batch_transform.py`):
```python
import boto3
import sagemaker
import json
import time

def create_batch_transform_job(student_id, model_name):
    """Create batch transform job for batch inference"""
    
    sagemaker_client = boto3.client('sagemaker')
    
    transform_job_name = f'batch-transform-{student_id}-{int(time.time())}'
    
    transform_job_config = {
        'TransformJobName': transform_job_name,
        'ModelName': model_name,
        'TransformInput': {
            'DataSource': {
                'S3DataSource': {
                    'S3DataType': 'S3Prefix',
                    'S3Uri': f's3://sagemaker-{student_id}/data/batch-input/'
                }
            },
            'ContentType': 'text/csv',
            'SplitType': 'Line'
        },
        'TransformOutput': {
            'S3OutputPath': f's3://sagemaker-{student_id}/batch-output/',
            'AssembleWith': 'Line'
        },
        'TransformResources': {
            'InstanceType': 'ml.m5.xlarge',
            'InstanceCount': 1
        }
    }
    
    # Create transform job
    response = sagemaker_client.create_transform_job(**transform_job_config)
    
    print(f"✅ Batch transform job created: {transform_job_name}")
    
    # Wait for completion
    print("Waiting for batch transform to complete...")
    while True:
        response = sagemaker_client.describe_transform_job(
            TransformJobName=transform_job_name
        )
        status = response['TransformJobStatus']
        print(f"Status: {status}")
        
        if status in ['Completed', 'Failed', 'Stopped']:
            break
        
        time.sleep(30)
    
    if status == 'Completed':
        print(f"✅ Batch transform completed successfully!")
        
        # Save job info
        with open(f'batch-transform-{student_id}.json', 'w') as f:
            json.dump({
                'job_name': transform_job_name,
                'status': status,
                'output_path': f's3://sagemaker-{student_id}/batch-output/'
            }, f, indent=2)
        
        return transform_job_name
    else:
        print(f"❌ Batch transform failed: {response.get('FailureReason')}")
        return None

if __name__ == "__main__":
    import sys
    student_id = sys.argv[1]
    model_name = sys.argv[2]
    create_batch_transform_job(student_id, model_name)
```

**Run batch transform**:
```bash
python scripts/batch_transform.py {student_id} xgboost-model-{student_id}

# Check output
aws s3 ls s3://sagemaker-{student_id}/batch-output/ --recursive
```

---

### Task 4-10: Additional Tasks

**Task 4: Model Registry** - Register models with versioning
**Task 5: Data Quality Monitoring** - Set up data drift detection
**Task 6: Model Quality Monitoring** - Track model performance
**Task 7: SageMaker Clarify** - Detect bias in data and models
**Task 8: Multi-Model Endpoint** - Deploy multiple models efficiently
**Task 9: Automated Retraining** - Lambda-triggered retraining
**Task 10: CI/CD Pipeline** - MLOps with CodePipeline

_(Scripts and detailed instructions available in assessment materials)_

---

## Validation Commands

```bash
# Check pipeline exists
aws sagemaker list-pipelines --name-contains {student_id}

# Check tuning jobs
aws sagemaker list-hyper-parameter-tuning-jobs --name-contains {student_id}

# Check batch transform jobs
aws sagemaker list-transform-jobs --name-contains {student_id}

# Run validation
python validate_tasks.py aiml_hard
```

---

## Success Criteria

✅ **Pipeline**: SageMaker Pipeline with 3+ steps  
✅ **Tuning**: Hyperparameter tuning job completed  
✅ **Batch Transform**: Batch inference executed  
✅ **Model Registry**: Models registered with versions  
✅ **Monitoring**: Data and model quality monitoring active  
✅ **Scripts**: All Python scripts functional  

---

## Testing Your Work

```bash
python validate_tasks.py aiml_hard
```

**Minimum passing score**: 70% (7 out of 10 tasks)

---

## Cost Considerations

**SageMaker Advanced Features**:
- Pipeline execution: ~$0.03 per pipeline run
- Hyperparameter tuning: ~$3-10 per job (10 trials)
- Batch transform: ~$0.30/hour per instance
- Model monitoring: ~$0.01 per monitoring execution

**Important**: Delete resources after completion!

**Estimated Cost**: $5-15 for this assessment

---

## Additional Resources

- [SageMaker Pipelines](https://docs.aws.amazon.com/sagemaker/latest/dg/pipelines.html)
- [Hyperparameter Tuning](https://docs.aws.amazon.com/sagemaker/latest/dg/automatic-model-tuning.html)
- [Batch Transform](https://docs.aws.amazon.com/sagemaker/latest/dg/batch-transform.html)
- [Model Monitor](https://docs.aws.amazon.com/sagemaker/latest/dg/model-monitor.html)

---

**Good luck with your AI/ML Hard assessment!** 🚀
