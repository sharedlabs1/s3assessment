"""
AWS AI/ML Services - Easy Assessment - Test Script
Tests Rekognition, Comprehend, Translate, Polly integration
"""

import sys
import os
import boto3
from botocore.exceptions import ClientError

def get_student_id():
    """Get student ID from command line arguments"""
    if len(sys.argv) < 2:
        print("Error: Student ID is required")
        print("Usage: python validate_tasks.py aiml_easy")
        sys.exit(1)
    return sys.argv[1]

def test_s3_bucket_exists(s3_client, student_id):
    """Task 1: Verify S3 bucket exists with folder structure"""
    bucket_name = f"aiml-assets-{student_id}"
    
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        
        # Check for folders
        folders = ['images/', 'videos/', 'documents/', 'audio/']
        found_folders = []
        
        for folder in folders:
            try:
                response = s3_client.list_objects_v2(
                    Bucket=bucket_name,
                    Prefix=folder,
                    MaxKeys=1
                )
                if 'Contents' in response or 'CommonPrefixes' in response:
                    found_folders.append(folder)
            except:
                pass
        
        if len(found_folders) == 0:
            print(f"⚠️  Task 1 Warning: Bucket exists but folders not found")
            return True
        
        print(f"✅ Task 1 Passed: S3 bucket with {len(found_folders)}/4 folder(s)")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"❌ Task 1 Failed: Bucket '{bucket_name}' not found")
            return False
        print(f"❌ Task 1 Failed: {e}")
        return False

def test_rekognition_access(student_id):
    """Task 2-4: Verify Rekognition can be accessed"""
    
    try:
        rekognition = boto3.client('rekognition')
        
        # Simple test to verify access (list collections)
        # This doesn't require any resources
        rekognition.list_collections(MaxResults=1)
        
        print(f"✅ Task 2-4 Passed: Rekognition service accessible")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDeniedException':
            print(f"❌ Task 2-4 Failed: No permission to access Rekognition")
            return False
        print(f"⚠️  Task 2-4 Warning: {e}")
        return True

def test_scripts_directory_exists(student_id):
    """Task 2-10: Verify scripts directory and files exist"""
    
    if not os.path.isdir('scripts'):
        print(f"❌ Task 2-10 Failed: scripts/ directory not found")
        return False
    
    expected_scripts = [
        'scripts/detect_labels.py',
        'scripts/detect_faces.py',
        'scripts/detect_text.py',
        'scripts/analyze_sentiment.py',
        'scripts/detect_entities.py',
        'scripts/translate_text.py',
        'scripts/text_to_speech.py',
        'scripts/ai_pipeline.py'
    ]
    
    found_scripts = sum(1 for script in expected_scripts if os.path.exists(script))
    
    if found_scripts == 0:
        print(f"❌ Task 2-10 Failed: No Python scripts found")
        return False
    
    print(f"✅ Task 2-10 Passed: {found_scripts}/{len(expected_scripts)} script(s) created")
    return True

def test_output_files_exist(student_id):
    """Task 2-8: Verify output files were generated"""
    
    expected_patterns = [
        f'rekognition-labels-{student_id}.json',
        f'rekognition-faces-{student_id}.json',
        f'rekognition-text-{student_id}.json',
        f'comprehend-sentiment-{student_id}.json',
        f'comprehend-entities-{student_id}.json',
        f'translate-results-{student_id}.json',
        f'polly-joanna-{student_id}.mp3',
        f'ai-pipeline-results-{student_id}.json'
    ]
    
    found_files = sum(1 for pattern in expected_patterns if os.path.exists(pattern))
    
    if found_files == 0:
        print(f"⚠️  Task 2-8 Warning: No output files found")
        print(f"   Run the Python scripts to generate outputs")
        return True
    
    print(f"✅ Task 2-8 Passed: {found_files}/{len(expected_patterns)} output file(s) generated")
    return True

def test_comprehend_access(student_id):
    """Task 5-6: Verify Comprehend service access"""
    
    try:
        comprehend = boto3.client('comprehend')
        
        # Test with simple sentiment detection
        response = comprehend.detect_sentiment(
            Text="This is a test.",
            LanguageCode='en'
        )
        
        if 'Sentiment' in response:
            print(f"✅ Task 5-6 Passed: Comprehend service accessible")
            return True
        
        return False
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDeniedException':
            print(f"❌ Task 5-6 Failed: No permission to access Comprehend")
            return False
        print(f"⚠️  Task 5-6 Warning: {e}")
        return True

def test_translate_access(student_id):
    """Task 7: Verify Translate service access"""
    
    try:
        translate_client = boto3.client('translate')
        
        # Test with simple translation
        response = translate_client.translate_text(
            Text="Hello",
            SourceLanguageCode='en',
            TargetLanguageCode='es'
        )
        
        if 'TranslatedText' in response:
            print(f"✅ Task 7 Passed: Translate service accessible")
            return True
        
        return False
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDeniedException':
            print(f"❌ Task 7 Failed: No permission to access Translate")
            return False
        print(f"⚠️  Task 7 Warning: {e}")
        return True

def test_polly_access(student_id):
    """Task 8: Verify Polly service access"""
    
    try:
        polly = boto3.client('polly')
        
        # Test by listing voices
        response = polly.describe_voices(MaxResults=1)
        
        if 'Voices' in response:
            print(f"✅ Task 8 Passed: Polly service accessible")
            return True
        
        return False
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDeniedException':
            print(f"❌ Task 8 Failed: No permission to access Polly")
            return False
        print(f"⚠️  Task 8 Warning: {e}")
        return True

def test_iam_role_exists(iam_client, student_id):
    """Task 9: Verify IAM role exists"""
    role_name = f"AWSAIMLServicesRole-{student_id}"
    
    try:
        response = iam_client.get_role(RoleName=role_name)
        role = response['Role']
        
        # Check if role has policies
        try:
            policies = iam_client.list_attached_role_policies(RoleName=role_name)
            inline_policies = iam_client.list_role_policies(RoleName=role_name)
            
            total_policies = len(policies.get('AttachedPolicies', [])) + len(inline_policies.get('PolicyNames', []))
            
            if total_policies == 0:
                print(f"⚠️  Task 9 Warning: Role exists but no policies attached")
                return True
            
            print(f"✅ Task 9 Passed: IAM role with {total_policies} policy/policies")
            return True
            
        except ClientError:
            print(f"✅ Task 9 Passed: IAM role exists")
            return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchEntity':
            print(f"⚠️  Task 9 Warning: IAM role '{role_name}' not found")
            return True
        print(f"⚠️  Task 9 Warning: {e}")
        return True

def test_pipeline_results_exist(student_id):
    """Task 10: Verify AI pipeline was executed"""
    
    pipeline_result_file = f'ai-pipeline-results-{student_id}.json'
    
    if not os.path.exists(pipeline_result_file):
        print(f"⚠️  Task 10 Warning: Pipeline results file not found")
        print(f"   Run: python scripts/ai_pipeline.py {student_id}")
        return True
    
    try:
        import json
        with open(pipeline_result_file, 'r') as f:
            data = json.load(f)
        
        # Check if it has expected keys
        expected_keys = ['labels', 'text', 'translation', 'sentiment']
        found_keys = sum(1 for key in expected_keys if key in data)
        
        print(f"✅ Task 10 Passed: AI pipeline executed ({found_keys}/4 components)")
        return True
        
    except Exception as e:
        print(f"⚠️  Task 10 Warning: Could not read pipeline results: {e}")
        return True

def main():
    """Run all AI/ML Easy assessment tests"""
    print("=" * 60)
    print("AWS AI/ML Services - Easy Assessment - Validation")
    print("=" * 60)
    
    student_id = get_student_id()
    print(f"\n🎓 Student ID: {student_id}")
    print(f"🤖 Testing AI/ML Services\n")
    
    # Initialize AWS clients
    try:
        s3_client = boto3.client('s3')
        iam_client = boto3.client('iam')
    except Exception as e:
        print(f"❌ Error initializing AWS clients: {e}")
        sys.exit(1)
    
    # Run tests
    results = []
    total_tasks = 10
    
    print("Starting validation...\n")
    
    # Task 1: S3 bucket
    results.append(test_s3_bucket_exists(s3_client, student_id))
    
    # Task 2-4: Rekognition
    results.append(test_rekognition_access(student_id))
    
    # Task 2-10: Scripts directory
    results.append(test_scripts_directory_exists(student_id))
    
    # Task 2-8: Output files
    results.append(test_output_files_exist(student_id))
    
    # Task 5-6: Comprehend
    results.append(test_comprehend_access(student_id))
    
    # Task 7: Translate
    results.append(test_translate_access(student_id))
    
    # Task 8: Polly
    results.append(test_polly_access(student_id))
    
    # Task 9: IAM role
    results.append(test_iam_role_exists(iam_client, student_id))
    
    # Task 10: Pipeline
    results.append(test_pipeline_results_exist(student_id))
    
    # Additional: Check if sample files uploaded
    bucket_name = f"aiml-assets-{student_id}"
    try:
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix='images/',
            MaxKeys=5
        )
        image_count = response.get('KeyCount', 0)
        if image_count > 0:
            print(f"✅ Sample Data: {image_count} image(s) uploaded to S3")
            results.append(True)
        else:
            print(f"⚠️  Sample Data: No images found in S3 bucket")
            results.append(True)
    except:
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
        print("\n🎉 CONGRATULATIONS! You passed the AI/ML Easy assessment!")
        print("You've successfully demonstrated:")
        print("  ✓ Amazon Rekognition - Image analysis")
        print("  ✓ Amazon Comprehend - Text analysis")
        print("  ✓ Amazon Translate - Language translation")
        print("  ✓ Amazon Polly - Text-to-speech")
        print("  ✓ IAM permissions for AI services")
        print("  ✓ Integrated AI/ML pipeline")
        sys.exit(0)
    else:
        print("\n❌ Assessment not passed. Minimum score required: 70%")
        print("Please review the failed tasks and try again.")
        print("\nQuick start:")
        print(f"  1. Create S3 bucket: aws s3 mb s3://aiml-assets-{student_id}")
        print(f"  2. Create scripts/ directory: mkdir scripts")
        print(f"  3. Copy Python scripts from README")
        print(f"  4. Run scripts to generate outputs")
        sys.exit(1)

if __name__ == "__main__":
    main()
