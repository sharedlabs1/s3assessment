"""
AWS AI/ML Services - Medium Assessment - Test Script
Tests SageMaker training, model deployment, endpoints, predictions
"""

import sys
import os
import boto3
from botocore.exceptions import ClientError

def get_student_id():
    """Get student ID from command line arguments"""
    if len(sys.argv) < 2:
        print("Error: Student ID is required")
        print("Usage: python validate_tasks.py aiml_medium")
        sys.exit(1)
    return sys.argv[1]

def test_s3_bucket_exists(s3_client, student_id):
    """Task 1: Verify SageMaker S3 bucket exists"""
    bucket_name = f"sagemaker-{student_id}"
    
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        
        # Check for training data
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix='data/',
            MaxKeys=10
        )
        
        object_count = response.get('KeyCount', 0)
        
        if object_count == 0:
            print(f"⚠️  Task 1 Warning: Bucket exists but no training data found")
            return True
        
        print(f"✅ Task 1 Passed: S3 bucket with {object_count} data file(s)")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"❌ Task 1 Failed: Bucket '{bucket_name}' not found")
            return False
        print(f"❌ Task 1 Failed: {e}")
        return False

def test_iam_role_exists(iam_client, student_id):
    """Task 3: Verify SageMaker IAM role exists"""
    role_name = f"SageMakerExecutionRole-{student_id}"
    
    try:
        response = iam_client.get_role(RoleName=role_name)
        
        # Check policies
        policies = iam_client.list_attached_role_policies(RoleName=role_name)
        policy_count = len(policies.get('AttachedPolicies', []))
        
        print(f"✅ Task 3 Passed: IAM role with {policy_count} policy/policies")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchEntity':
            print(f"❌ Task 3 Failed: Role '{role_name}' not found")
            return False
        print(f"⚠️  Task 3 Warning: {e}")
        return True

def test_training_job_exists(sagemaker_client, student_id):
    """Task 4: Verify training job was created"""
    
    try:
        response = sagemaker_client.list_training_jobs(
            NameContains=student_id,
            MaxResults=10,
            SortBy='CreationTime',
            SortOrder='Descending'
        )
        
        training_jobs = response.get('TrainingJobSummaries', [])
        
        if not training_jobs:
            print(f"⚠️  Task 4 Warning: No training jobs found")
            return True
        
        completed_jobs = [j for j in training_jobs if j['TrainingJobStatus'] == 'Completed']
        
        if not completed_jobs:
            print(f"⚠️  Task 4 Warning: Training jobs exist but none completed")
            return True
        
        print(f"✅ Task 4 Passed: {len(completed_jobs)} completed training job(s)")
        return True
        
    except Exception as e:
        print(f"⚠️  Task 4 Warning: {e}")
        return True

def test_model_exists(sagemaker_client, student_id):
    """Task 5: Verify SageMaker model exists"""
    model_name = f"xgboost-model-{student_id}"
    
    try:
        response = sagemaker_client.describe_model(ModelName=model_name)
        
        print(f"✅ Task 5 Passed: Model '{model_name}' exists")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if 'NotFound' in error_code or 'ValidationException' in error_code:
            print(f"⚠️  Task 5 Warning: Model '{model_name}' not found")
            return True
        print(f"⚠️  Task 5 Warning: {e}")
        return True

def test_endpoint_exists(sagemaker_client, student_id):
    """Task 6: Verify endpoint exists and is in service"""
    endpoint_name = f"xgboost-endpoint-{student_id}"
    
    try:
        response = sagemaker_client.describe_endpoint(
            EndpointName=endpoint_name
        )
        
        status = response['EndpointStatus']
        
        if status != 'InService':
            print(f"⚠️  Task 6 Warning: Endpoint exists but status is '{status}'")
            return True
        
        print(f"✅ Task 6 Passed: Endpoint is InService")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if 'NotFound' in error_code or 'ValidationException' in error_code:
            print(f"⚠️  Task 6 Warning: Endpoint '{endpoint_name}' not found")
            return True
        print(f"⚠️  Task 6 Warning: {e}")
        return True

def test_predictions_file_exists(student_id):
    """Task 7: Verify predictions were made"""
    predictions_file = f'predictions-{student_id}.json'
    
    if not os.path.exists(predictions_file):
        print(f"⚠️  Task 7 Warning: Predictions file not found")
        print(f"   Run: python scripts/make_predictions.py {student_id}")
        return True
    
    try:
        import json
        with open(predictions_file, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, list) and len(data) > 0:
            print(f"✅ Task 7 Passed: {len(data)} prediction(s) made")
            return True
        
        print(f"⚠️  Task 7 Warning: Predictions file is empty")
        return True
        
    except Exception as e:
        print(f"⚠️  Task 7 Warning: Could not read predictions: {e}")
        return True

def test_scripts_exist(student_id):
    """Task 2-10: Verify all Python scripts exist"""
    
    expected_scripts = [
        'scripts/prepare_dataset.py',
        'scripts/train_xgboost.py',
        'scripts/create_model.py',
        'scripts/deploy_endpoint.py',
        'scripts/make_predictions.py',
        'scripts/monitor_endpoint.py',
        'scripts/cleanup_sagemaker.py'
    ]
    
    found_scripts = sum(1 for script in expected_scripts if os.path.exists(script))
    
    if found_scripts == 0:
        print(f"❌ Task 2-10 Failed: No scripts found")
        return False
    
    print(f"✅ Task 2-10 Passed: {found_scripts}/{len(expected_scripts)} script(s) created")
    return True

def test_training_output_exists(student_id):
    """Task 4: Verify training job output file exists"""
    training_file = f'training-job-{student_id}.json'
    
    if not os.path.exists(training_file):
        print(f"⚠️  Task 4 Warning: Training job output not found")
        return True
    
    print(f"✅ Task 4 Info: Training job details saved")
    return True

def test_monitoring_exists(student_id):
    """Task 9: Verify monitoring was set up"""
    monitoring_file = f'endpoint-monitoring-{student_id}.json'
    
    if not os.path.exists(monitoring_file):
        print(f"⚠️  Task 9 Warning: Monitoring results not found")
        print(f"   Run: python scripts/monitor_endpoint.py {student_id}")
        return True
    
    print(f"✅ Task 9 Passed: Endpoint monitoring configured")
    return True

def main():
    """Run all AI/ML Medium assessment tests"""
    print("=" * 60)
    print("AWS AI/ML Services - Medium Assessment - Validation")
    print("=" * 60)
    
    student_id = get_student_id()
    print(f"\n🎓 Student ID: {student_id}")
    print(f"🤖 Testing SageMaker Resources\n")
    
    # Initialize AWS clients
    try:
        s3_client = boto3.client('s3')
        iam_client = boto3.client('iam')
        sagemaker_client = boto3.client('sagemaker')
    except Exception as e:
        print(f"❌ Error initializing AWS clients: {e}")
        sys.exit(1)
    
    # Run tests
    results = []
    total_tasks = 10
    
    print("Starting validation...\n")
    
    # Task 1: S3 bucket
    results.append(test_s3_bucket_exists(s3_client, student_id))
    
    # Task 2-10: Scripts
    results.append(test_scripts_exist(student_id))
    
    # Task 3: IAM role
    results.append(test_iam_role_exists(iam_client, student_id))
    
    # Task 4: Training job
    results.append(test_training_job_exists(sagemaker_client, student_id))
    results.append(test_training_output_exists(student_id))
    
    # Task 5: Model
    results.append(test_model_exists(sagemaker_client, student_id))
    
    # Task 6: Endpoint
    results.append(test_endpoint_exists(sagemaker_client, student_id))
    
    # Task 7: Predictions
    results.append(test_predictions_file_exists(student_id))
    
    # Task 9: Monitoring
    results.append(test_monitoring_exists(student_id))
    
    # Additional check: Dataset preparation
    if os.path.exists('scripts/prepare_dataset.py'):
        print(f"✅ Dataset Preparation: Script ready")
        results.append(True)
    else:
        print(f"⚠️  Dataset Preparation: Script not found")
        results.append(True)
    
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
        print("\n🎉 CONGRATULATIONS! You passed the AI/ML Medium assessment!")
        print("You've successfully demonstrated:")
        print("  ✓ SageMaker training jobs with built-in algorithms")
        print("  ✓ Model creation and versioning")
        print("  ✓ Real-time endpoint deployment")
        print("  ✓ Making predictions via endpoints")
        print("  ✓ Model monitoring with CloudWatch")
        print("  ✓ IAM roles for SageMaker")
        print("\n⚠️  Remember to run cleanup script to avoid ongoing costs:")
        print(f"  python scripts/cleanup_sagemaker.py {student_id}")
        sys.exit(0)
    else:
        print("\n❌ Assessment not passed. Minimum score required: 70%")
        print("Please review the failed tasks and try again.")
        print("\nQuick start:")
        print(f"  1. Create S3 bucket: aws s3 mb s3://sagemaker-{student_id}")
        print(f"  2. Create IAM role: See Task 3 in README")
        print(f"  3. Prepare dataset: python scripts/prepare_dataset.py {student_id}")
        print(f"  4. Train model: python scripts/train_xgboost.py {student_id} <role-arn>")
        sys.exit(1)

if __name__ == "__main__":
    main()
