# Multi-Service Assessment Framework

This repository supports multiple AWS service assessments with a reusable validation framework.

## Architecture

### Student Files (distribute these 3 files):
1. **`validate_tasks.py`** - Generic validation script (works for all services)
2. **`requirements.txt`** - Python dependencies
3. **`README_xxx.md`** - Service-specific instructions (where xxx = service name)

### Repository Structure (GitHub):
```
.github/
  workflows/
    validate.yml                    # Generic workflow (handles all services)
  scripts/
    test_s3_assessment.py          # S3 test logic
    test_ec2_assessment.py         # EC2 test logic
    test_xxx_assessment.py         # Add more services...

README.md                           # S3 assessment (default)
README_ec2.md                       # EC2 assessment
README_xxx.md                       # Add more services...
validate_tasks.py                   # Generic validation script
requirements.txt                    # Dependencies
```

## Adding a New Service Assessment

To add a new service (e.g., Lambda), follow these steps:

### 1. Create Service-Specific README

Create `README_lambda.md`:
```markdown
# AWS Lambda Assessment - Serverless Functions

## Tasks to Complete
### Task 1: Create Lambda Function
- **Function Name**: `hello-world-${your-student-id}`
- Runtime: Python 3.12
- etc...

## Validation
Run: `python validate_tasks.py lambda`
```

### 2. Create Test Script

Create `.github/scripts/test_lambda_assessment.py`:

```python
#!/usr/bin/env python3
"""
Lambda Assessment Test Cases
"""

import boto3
from datetime import datetime

class LambdaAssessmentTester:
    def __init__(self, student_id=None):
        self.lambda_client = boto3.client('lambda')
        self.sts_client = boto3.client('sts')
        self.account_id = self.sts_client.get_caller_identity()['Account']
        self.student_id = student_id
        
        self.function_name = f'hello-world-{student_id}'
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def log_result(self, passed: bool, test_name: str, details: str):
        status = "[PASS]" if passed else "[FAIL]"
        self.results.append(f"{status} {test_name}")
        self.results.append(f"       {details}")
        self.results.append("")
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def test_task1_function_exists(self):
        """Test if Lambda function exists"""
        try:
            response = self.lambda_client.get_function(
                FunctionName=self.function_name
            )
            self.log_result(True,
                "Task 1.1 - Function Exists",
                f"Function '{self.function_name}' found")
        except:
            self.log_result(False,
                "Task 1.1 - Function Exists",
                f"Function '{self.function_name}' not found")
    
    # Add more test methods...
    
    def generate_report(self):
        """Generate test report"""
        report = []
        report.append("=" * 70)
        report.append("AWS LAMBDA ASSESSMENT - TEST REPORT")
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
            report.append("STATUS: ✓ ALL TESTS PASSED")
        else:
            report.append(f"STATUS: ✗ {self.failed} TEST(S) FAILED")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def run_all_tests(self):
        """Run all test cases"""
        try:
            self.test_task1_function_exists()
        except Exception as e:
            self.log_result(False, "Task 1 - Critical Error", f"Error: {str(e)}")
        
        # Add more test calls...
        
        report = self.generate_report()
        
        with open('test_report.log', 'w') as f:
            f.write(report)
        
        print(report)
        return self.failed == 0

if __name__ == "__main__":
    import sys
    student_id = sys.argv[1] if len(sys.argv) > 1 else None
    
    try:
        tester = LambdaAssessmentTester(student_id=student_id)
        success = tester.run_all_tests()
        exit(0 if success else 1)
    except Exception as e:
        # Error handling...
        exit(1)
```

### 3. That's It!

No need to modify:
- ✅ `validate_tasks.py` (already generic)
- ✅ `.github/workflows/validate.yml` (already generic)
- ✅ `requirements.txt` (boto3 works for all AWS services)

## How It Works

1. **Student runs:** `python validate_tasks.py lambda`
2. **Script sends to workflow:** `assessment_type=lambda`, `student_id=xxx`
3. **Workflow executes:** `python .github/scripts/test_lambda_assessment.py "xxx"`
4. **Test script runs:** Checks Lambda resources for student xxx
5. **Report downloaded:** `test_report.log` saved locally

## Usage Examples

```bash
# S3 Assessment (default)
python validate_tasks.py
python validate_tasks.py s3

# EC2 Assessment
python validate_tasks.py ec2

# Lambda Assessment (after you add it)
python validate_tasks.py lambda

# RDS Assessment (after you add it)
python validate_tasks.py rds
```

## Naming Conventions

### Resources should follow this pattern:
- **S3 Buckets:** `service-purpose-${student-id}`
  - Example: `mediaflow-raw-student123`
  
- **EC2 Instances:** `purpose-${student-id}`
  - Example: `webserver-student123`
  
- **Lambda Functions:** `function-name-${student-id}`
  - Example: `hello-world-student123`

### Test Scripts:
- **File:** `test_xxx_assessment.py` (where xxx = service name)
- **Class:** `XXXAssessmentTester` (e.g., `S3AssessmentTester`, `EC2AssessmentTester`)

### README Files:
- **Default service:** `README.md`
- **Other services:** `README_xxx.md` (e.g., `README_ec2.md`, `README_lambda.md`)

## Configuration

### Instructor Setup (One-time):
1. Add AWS credentials to GitHub repository secrets:
   - Go to: `https://github.com/sharedlabs1/s3assessment/settings/secrets/actions`
   - Add `AWS_ACCESS_KEY_ID`
   - Add `AWS_SECRET_ACCESS_KEY`

2. These credentials should have permissions for ALL services you're testing (S3, EC2, Lambda, etc.)

### Student Setup (Simple):
1. Download 3 files: `validate_tasks.py`, `requirements.txt`, `README_xxx.md`
2. Run: `pip install -r requirements.txt`
3. Run: `gh auth login` (one-time)
4. Run: `python validate_tasks.py xxx` (where xxx = service name)

## Benefits

✅ **Reusable:** One validation script for all services
✅ **Scalable:** Easy to add new services
✅ **Consistent:** Same workflow for students across all assessments
✅ **Maintainable:** Each service has isolated test logic
✅ **Secure:** Test logic hidden from students (in `.github/scripts/`)
✅ **Concurrent:** Multiple students can run validations simultaneously

## Currently Supported Services

- [x] **S3** - Data Lake Setup
- [x] **EC2** - Instance Management
- [ ] Lambda - Serverless Functions (template ready)
- [ ] RDS - Database Management
- [ ] VPC - Network Configuration
- [ ] IAM - Access Management
- [ ] CloudFormation - Infrastructure as Code

Add more as needed!
