#!/usr/bin/env python3
"""
S3 Assessment Test Cases
Tests learner's S3 configuration against requirements
"""

import boto3  # type: ignore
import json
import traceback
from datetime import datetime

class S3AssessmentTester:
    def __init__(self, student_id=None):
        self.s3_client = boto3.client('s3')
        self.sts_client = boto3.client('sts')
        self.account_id = self.sts_client.get_caller_identity()['Account']
        
        # Use student_id if provided, otherwise fall back to account_id for backward compatibility
        identifier = student_id if student_id else self.account_id
        
        self.bucket_names = {
            'raw': f'mediaflow-raw-{identifier}',
            'processed': f'mediaflow-processed-{identifier}',
            'archive': f'mediaflow-archive-{identifier}'
        }
        
        self.student_id = student_id
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def log_result(self, passed: bool, test_name: str, details: str):
        """Log test result"""
        status = "[PASS]" if passed else "[FAIL]"
        self.results.append(f"{status} {test_name}")
        self.results.append(f"       {details}")
        self.results.append("")
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def test_task1_bucket_creation(self):
        """Test Task 1: Bucket creation with proper configuration"""
        print("Testing Task 1: S3 Bucket Creation...")
        
        for bucket_type, bucket_name in self.bucket_names.items():
            # Test 1.1: Bucket exists
            try:
                self.s3_client.head_bucket(Bucket=bucket_name)
                self.log_result(True, 
                    f"Task 1.1.{bucket_type.upper()} - Bucket Exists",
                    f"Bucket '{bucket_name}' was created successfully")
            except:
                self.log_result(False,
                    f"Task 1.1.{bucket_type.upper()} - Bucket Exists",
                    f"Bucket '{bucket_name}' not found. Please create the bucket.")
                continue
            
            # Test 1.2: Versioning enabled (raw and processed only)
            if bucket_type in ['raw', 'processed']:
                try:
                    versioning = self.s3_client.get_bucket_versioning(Bucket=bucket_name)
                    if versioning.get('Status') == 'Enabled':
                        self.log_result(True,
                            f"Task 1.2.{bucket_type.upper()} - Versioning Enabled",
                            f"Versioning is correctly enabled on '{bucket_name}'")
                    else:
                        self.log_result(False,
                            f"Task 1.2.{bucket_type.upper()} - Versioning Enabled",
                            f"Versioning is not enabled on '{bucket_name}'. Expected: Enabled, Got: {versioning.get('Status', 'Disabled')}")
                except Exception as e:
                    self.log_result(False,
                        f"Task 1.2.{bucket_type.upper()} - Versioning Enabled",
                        f"Error checking versioning: {str(e)}")
            
            # Test 1.3: Encryption enabled
            try:
                encryption = self.s3_client.get_bucket_encryption(Bucket=bucket_name)
                rules = encryption.get('ServerSideEncryptionConfiguration', {}).get('Rules', [])
                if rules and rules[0].get('ApplyServerSideEncryptionByDefault', {}).get('SSEAlgorithm') == 'AES256':
                    self.log_result(True,
                        f"Task 1.3.{bucket_type.upper()} - Encryption Enabled",
                        f"SSE-S3 encryption is correctly configured on '{bucket_name}'")
                else:
                    self.log_result(False,
                        f"Task 1.3.{bucket_type.upper()} - Encryption Enabled",
                        f"Incorrect encryption configuration on '{bucket_name}'. Expected: SSE-S3 (AES256)")
            except:
                self.log_result(False,
                    f"Task 1.3.{bucket_type.upper()} - Encryption Enabled",
                    f"No encryption configured on '{bucket_name}'. Please enable SSE-S3.")
            
            # Test 1.4: Public access blocked
            try:
                public_access = self.s3_client.get_public_access_block(Bucket=bucket_name)
                config = public_access.get('PublicAccessBlockConfiguration', {})
                if all([config.get('BlockPublicAcls'), config.get('IgnorePublicAcls'),
                       config.get('BlockPublicPolicy'), config.get('RestrictPublicBuckets')]):
                    self.log_result(True,
                        f"Task 1.4.{bucket_type.upper()} - Public Access Blocked",
                        f"All public access is correctly blocked on '{bucket_name}'")
                else:
                    self.log_result(False,
                        f"Task 1.4.{bucket_type.upper()} - Public Access Blocked",
                        f"Public access not fully blocked on '{bucket_name}'. All settings must be True.")
            except:
                self.log_result(False,
                    f"Task 1.4.{bucket_type.upper()} - Public Access Blocked",
                    f"Public access block not configured on '{bucket_name}'")
    
    def test_task2_lifecycle_policies(self):
        """Test Task 2: Lifecycle policies"""
        print("Testing Task 2: Lifecycle Policies...")
        
        # Test raw bucket lifecycle
        raw_bucket = self.bucket_names['raw']
        try:
            lifecycle = self.s3_client.get_bucket_lifecycle_configuration(Bucket=raw_bucket)
            rules = lifecycle.get('Rules', [])
            
            # Check for required transitions
            has_ia_30 = False
            has_glacier_90 = False
            has_expiration_365 = False
            
            for rule in rules:
                if rule.get('Status') == 'Enabled':
                    transitions = rule.get('Transitions', [])
                    for trans in transitions:
                        if trans.get('Days') == 30 and trans.get('StorageClass') == 'STANDARD_IA':
                            has_ia_30 = True
                        if trans.get('Days') == 90 and trans.get('StorageClass') == 'GLACIER':
                            has_glacier_90 = True
                    
                    expiration = rule.get('Expiration', {})
                    if expiration.get('Days') == 365:
                        has_expiration_365 = True
            
            if has_ia_30 and has_glacier_90 and has_expiration_365:
                self.log_result(True,
                    "Task 2.1 - Raw Bucket Lifecycle",
                    f"Lifecycle policy correctly configured: IA@30d, Glacier@90d, Expire@365d")
            else:
                missing = []
                if not has_ia_30: missing.append("Standard-IA @ 30 days")
                if not has_glacier_90: missing.append("Glacier @ 90 days")
                if not has_expiration_365: missing.append("Expiration @ 365 days")
                self.log_result(False,
                    "Task 2.1 - Raw Bucket Lifecycle",
                    f"Missing lifecycle rules: {', '.join(missing)}")
        except:
            self.log_result(False,
                "Task 2.1 - Raw Bucket Lifecycle",
                f"No lifecycle configuration found on '{raw_bucket}'")
        
        # Test processed bucket lifecycle
        processed_bucket = self.bucket_names['processed']
        try:
            lifecycle = self.s3_client.get_bucket_lifecycle_configuration(Bucket=processed_bucket)
            rules = lifecycle.get('Rules', [])
            
            has_noncurrent_glacier_30 = False
            has_noncurrent_expiration_90 = False
            
            for rule in rules:
                if rule.get('Status') == 'Enabled':
                    noncurrent_trans = rule.get('NoncurrentVersionTransitions', [])
                    for trans in noncurrent_trans:
                        if trans.get('NoncurrentDays') == 30 and trans.get('StorageClass') == 'GLACIER':
                            has_noncurrent_glacier_30 = True
                    
                    noncurrent_exp = rule.get('NoncurrentVersionExpiration', {})
                    if noncurrent_exp.get('NoncurrentDays') == 90:
                        has_noncurrent_expiration_90 = True
            
            if has_noncurrent_glacier_30 and has_noncurrent_expiration_90:
                self.log_result(True,
                    "Task 2.2 - Processed Bucket Lifecycle",
                    "Non-current version lifecycle correctly configured: Glacier@30d, Expire@90d")
            else:
                missing = []
                if not has_noncurrent_glacier_30: missing.append("Non-current Glacier @ 30 days")
                if not has_noncurrent_expiration_90: missing.append("Non-current Expiration @ 90 days")
                self.log_result(False,
                    "Task 2.2 - Processed Bucket Lifecycle",
                    f"Missing non-current version rules: {', '.join(missing)}")
        except:
            self.log_result(False,
                "Task 2.2 - Processed Bucket Lifecycle",
                f"No lifecycle configuration found on '{processed_bucket}'")
    
    def test_task3_policies_and_tags(self):
        """Test Task 3: Bucket policies and tags"""
        print("Testing Task 3: Policies and Tags...")
        
        raw_bucket = self.bucket_names['raw']
        processed_bucket = self.bucket_names['processed']
        archive_bucket = self.bucket_names['archive']
        
        # Test raw bucket policy for encryption
        try:
            policy = self.s3_client.get_bucket_policy(Bucket=raw_bucket)
            policy_doc = json.loads(policy['Policy'])
            
            has_encryption_deny = False
            for statement in policy_doc.get('Statement', []):
                if (statement.get('Effect') == 'Deny' and 
                    's3:PutObject' in statement.get('Action', []) and
                    statement.get('Condition', {}).get('StringNotEquals', {}).get('s3:x-amz-server-side-encryption')):
                    has_encryption_deny = True
                    break
            
            if has_encryption_deny:
                self.log_result(True,
                    "Task 3.1 - Raw Bucket Policy",
                    "Bucket policy correctly denies unencrypted uploads")
            else:
                self.log_result(False,
                    "Task 3.1 - Raw Bucket Policy",
                    "Bucket policy does not properly deny unencrypted uploads")
        except:
            self.log_result(False,
                "Task 3.1 - Raw Bucket Policy",
                f"No bucket policy found on '{raw_bucket}' or error reading policy")
        
        # Test tags on raw and processed buckets
        required_tags = {
            'Environment': 'Production',
            'Project': 'MediaFlow',
            'CostCenter': 'Engineering'
        }
        
        for bucket_type in ['raw', 'processed']:
            bucket_name = self.bucket_names[bucket_type]
            try:
                tagging = self.s3_client.get_bucket_tagging(Bucket=bucket_name)
                tags = {tag['Key']: tag['Value'] for tag in tagging.get('TagSet', [])}
                
                if all(tags.get(k) == v for k, v in required_tags.items()):
                    self.log_result(True,
                        f"Task 3.2.{bucket_type.upper()} - Bucket Tags",
                        f"All required tags present and correct on '{bucket_name}'")
                else:
                    missing_or_wrong = []
                    for k, v in required_tags.items():
                        if tags.get(k) != v:
                            missing_or_wrong.append(f"{k}={v}")
                    self.log_result(False,
                        f"Task 3.2.{bucket_type.upper()} - Bucket Tags",
                        f"Missing or incorrect tags on '{bucket_name}': {', '.join(missing_or_wrong)}")
            except:
                self.log_result(False,
                    f"Task 3.2.{bucket_type.upper()} - Bucket Tags",
                    f"No tags found on '{bucket_name}'")
        
        # Test server access logging on processed bucket
        try:
            logging = self.s3_client.get_bucket_logging(Bucket=processed_bucket)
            logging_config = logging.get('LoggingEnabled', {})
            
            if (logging_config.get('TargetBucket') == archive_bucket and 
                logging_config.get('TargetPrefix') == 'logs/'):
                self.log_result(True,
                    "Task 3.3 - Server Access Logging",
                    f"Logging correctly configured: target={archive_bucket}, prefix=logs/")
            else:
                self.log_result(False,
                    "Task 3.3 - Server Access Logging",
                    f"Incorrect logging configuration. Expected: target={archive_bucket}, prefix=logs/")
        except:
            self.log_result(False,
                "Task 3.3 - Server Access Logging",
                f"Server access logging not configured on '{processed_bucket}'")
    
    def test_task4_folder_structure_and_upload(self):
        """Test Task 4: Folder structure and test file upload"""
        print("Testing Task 4: Folder Structure and Upload...")
        
        raw_bucket = self.bucket_names['raw']
        
        # Test folder structure
        required_prefixes = [
            'videos/incoming/',
            'videos/processing/',
            'thumbnails/'
        ]
        
        try:
            all_objects = self.s3_client.list_objects_v2(Bucket=raw_bucket)
            all_keys = [obj['Key'] for obj in all_objects.get('Contents', [])]
            
            folders_found = []
            for prefix in required_prefixes:
                if any(key.startswith(prefix) for key in all_keys):
                    folders_found.append(prefix)
            
            if len(folders_found) == len(required_prefixes):
                self.log_result(True,
                    "Task 4.1 - Folder Structure",
                    f"All required folders created: {', '.join(required_prefixes)}")
            else:
                missing = set(required_prefixes) - set(folders_found)
                self.log_result(False,
                    "Task 4.1 - Folder Structure",
                    f"Missing folders: {', '.join(missing)}")
        except Exception as e:
            self.log_result(False,
                "Task 4.1 - Folder Structure",
                f"Error checking folder structure: {str(e)}")
        
        # Test file upload
        test_file_key = 'videos/incoming/test-video.txt'
        try:
            obj = self.s3_client.get_object(Bucket=raw_bucket, Key=test_file_key)
            content = obj['Body'].read().decode('utf-8')
            
            if content.strip() == "Test Upload":
                self.log_result(True,
                    "Task 4.2 - Test File Upload",
                    f"File '{test_file_key}' uploaded with correct content")
            else:
                self.log_result(False,
                    "Task 4.2 - Test File Upload",
                    f"File '{test_file_key}' has incorrect content. Expected: 'Test Upload'")
        except:
            self.log_result(False,
                "Task 4.2 - Test File Upload",
                f"File '{test_file_key}' not found in bucket")
    
    def generate_report(self):
        """Generate test report"""
        report = []
        report.append("=" * 70)
        report.append("AWS S3 ASSESSMENT - TEST REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report.append(f"Account ID: {self.account_id}")
        if self.student_id:
            report.append(f"Student ID: {self.student_id}")
        report.append("")
        report.append(f"SUMMARY: {self.passed} passed, {self.failed} failed")
        report.append("=" * 70)
        report.append("")
        
        report.extend(self.results)
        
        report.append("=" * 70)
        if self.failed == 0:
            report.append("STATUS: ✓ ALL TESTS PASSED - Excellent work!")
        else:
            report.append(f"STATUS: ✗ {self.failed} TEST(S) FAILED - Please review and fix")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def run_all_tests(self):
        """Run all test cases"""
        try:
            self.test_task1_bucket_creation()
        except Exception as e:
            self.log_result(False, "Task 1 - Critical Error", f"Error running Task 1 tests: {str(e)}")
        
        try:
            self.test_task2_lifecycle_policies()
        except Exception as e:
            self.log_result(False, "Task 2 - Critical Error", f"Error running Task 2 tests: {str(e)}")
        
        try:
            self.test_task3_policies_and_tags()
        except Exception as e:
            self.log_result(False, "Task 3 - Critical Error", f"Error running Task 3 tests: {str(e)}")
        
        try:
            self.test_task4_folder_structure_and_upload()
        except Exception as e:
            self.log_result(False, "Task 4 - Critical Error", f"Error running Task 4 tests: {str(e)}")
        
        report = self.generate_report()
        
        # Write report to file
        with open('test_report.log', 'w') as f:
            f.write(report)
        
        print(report)
        
        return self.failed == 0

if __name__ == "__main__":
    import sys
    # Get student_id from command line argument if provided
    student_id = sys.argv[1] if len(sys.argv) > 1 else None
    
    try:
        tester = S3AssessmentTester(student_id=student_id)
        success = tester.run_all_tests()
        exit(0 if success else 1)
    except Exception as e:
        # Create a detailed failure report when initialization fails
        error_type = type(e).__name__
        error_msg = str(e)
        
        # Build a comprehensive failure report marking all tests as failed
        error_report = [
            "=" * 70,
            "AWS S3 ASSESSMENT - TEST REPORT",
            "=" * 70,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "Account ID: Unable to retrieve (credentials error)",
        ]
        
        if student_id:
            error_report.append(f"Student ID: {student_id}")
        
        error_report.extend([
            "",
            "SUMMARY: 0 passed, 18 failed",
            "=" * 70,
            "",
            f"[FAIL] Initialization Failed",
            f"       Error Type: {error_type}",
            f"       Error: {error_msg}",
            "",
            "=" * 70,
            "TASK 1: S3 BUCKET CREATION - ALL TESTS FAILED",
            "=" * 70,
            "",
            "[FAIL] Task 1.1.RAW - Bucket Exists",
            "       Cannot verify - AWS credentials not configured or invalid",
            "",
            "[FAIL] Task 1.1.PROCESSED - Bucket Exists",
            "       Cannot verify - AWS credentials not configured or invalid",
            "",
            "[FAIL] Task 1.1.ARCHIVE - Bucket Exists",
            "       Cannot verify - AWS credentials not configured or invalid",
            "",
            "[FAIL] Task 1.2.RAW - Versioning Enabled",
            "       Cannot verify - AWS credentials not configured or invalid",
            "",
            "[FAIL] Task 1.2.PROCESSED - Versioning Enabled",
            "       Cannot verify - AWS credentials not configured or invalid",
            "",
            "[FAIL] Task 1.3.RAW - Encryption Enabled",
            "       Cannot verify - AWS credentials not configured or invalid",
            "",
            "[FAIL] Task 1.3.PROCESSED - Encryption Enabled",
            "       Cannot verify - AWS credentials not configured or invalid",
            "",
            "[FAIL] Task 1.3.ARCHIVE - Encryption Enabled",
            "       Cannot verify - AWS credentials not configured or invalid",
            "",
            "[FAIL] Task 1.4.RAW - Public Access Blocked",
            "       Cannot verify - AWS credentials not configured or invalid",
            "",
            "[FAIL] Task 1.4.PROCESSED - Public Access Blocked",
            "       Cannot verify - AWS credentials not configured or invalid",
            "",
            "[FAIL] Task 1.4.ARCHIVE - Public Access Blocked",
            "       Cannot verify - AWS credentials not configured or invalid",
            "",
            "[FAIL] Task 2.1 - Raw Bucket Lifecycle",
            "       Cannot verify - AWS credentials not configured or invalid",
            "",
            "[FAIL] Task 2.2 - Processed Bucket Lifecycle",
            "       Cannot verify - AWS credentials not configured or invalid",
            "",
            "[FAIL] Task 3.1 - Raw Bucket Policy",
            "       Cannot verify - AWS credentials not configured or invalid",
            "",
            "[FAIL] Task 3.2.RAW - Bucket Tags",
            "       Cannot verify - AWS credentials not configured or invalid",
            "",
            "[FAIL] Task 3.2.PROCESSED - Bucket Tags",
            "       Cannot verify - AWS credentials not configured or invalid",
            "",
            "[FAIL] Task 3.3 - Server Access Logging",
            "       Cannot verify - AWS credentials not configured or invalid",
            "",
            "[FAIL] Task 4.1 - Folder Structure",
            "       Cannot verify - AWS credentials not configured or invalid",
            "",
            "[FAIL] Task 4.2 - Test File Upload",
            "       Cannot verify - AWS credentials not configured or invalid",
            "",
            "=" * 70,
            "DIAGNOSTIC INFORMATION",
            "=" * 70,
            "",
            "Error Details:",
            f"  Type: {error_type}",
            f"  Message: {error_msg}",
            "",
            "Stack Trace:",
            traceback.format_exc(),
            "",
            "Common Causes:",
            "  - AWS credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY) not set",
            "  - Invalid or expired AWS credentials",
            "  - Insufficient IAM permissions",
            "  - Network connectivity issues to AWS",
            "",
            "Solutions:",
            "  1. Configure AWS credentials as GitHub Secrets:",
            "     - AWS_ACCESS_KEY_ID",
            "     - AWS_SECRET_ACCESS_KEY",
            "  2. Ensure the IAM user/role has these permissions:",
            "     - s3:ListBucket, s3:GetObject, s3:GetBucketVersioning",
            "     - s3:GetEncryptionConfiguration, s3:GetBucketPublicAccessBlock",
            "     - s3:GetLifecycleConfiguration, s3:GetBucketPolicy",
            "     - s3:GetBucketTagging, s3:GetBucketLogging",
            "  3. Verify network access to AWS services",
            "",
            "=" * 70,
            "STATUS: ✗ ALL TESTS FAILED - AWS Configuration Error",
            "=" * 70
        ])
        
        report_text = "\n".join(error_report)
        with open('test_report.log', 'w') as f:
            f.write(report_text)
        print(report_text)
        exit(1)