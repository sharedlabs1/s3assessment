# AWS S3 Assessment - Data Lake Setup

## Scenario
You are a cloud engineer at MediaFlow Inc. Your task is to set up a secure and cost-optimized S3 data lake infrastructure.

## Prerequisites
- AWS Account with appropriate permissions
- AWS CLI configured (optional)
- Python 3.8+ installed

## Tasks to Complete

### Task 1: Create S3 Buckets with Proper Naming
Create three S3 buckets with the following specifications:
- **Bucket 1**: `mediaflow-raw-${your-account-id}` (for raw video uploads)
- **Bucket 2**: `mediaflow-processed-${your-account-id}` (for processed content)
- **Bucket 3**: `mediaflow-archive-${your-account-id}` (for long-term archive)

**Requirements:**
- Enable versioning on the raw and processed buckets
- Enable default encryption (SSE-S3) on all buckets
- Block all public access on all buckets

### Task 2: Configure Lifecycle Policies
Set up lifecycle policies to optimize costs:

**For `mediaflow-raw-${your-account-id}`:**
- Transition objects to Standard-IA after 30 days
- Transition objects to Glacier Flexible Retrieval after 90 days
- Expire objects after 365 days

**For `mediaflow-processed-${your-account-id}`:**
- Transition non-current versions to Glacier after 30 days
- Delete non-current versions after 90 days

### Task 3: Set Up Bucket Policies and Tags
**For `mediaflow-raw-${your-account-id}`:**
- Add bucket policy to deny unencrypted uploads
- Add tags: `Environment=Production`, `Project=MediaFlow`, `CostCenter=Engineering`

**For `mediaflow-processed-${your-account-id}`:**
- Enable server access logging to `mediaflow-archive-${your-account-id}/logs/`
- Add tags: `Environment=Production`, `Project=MediaFlow`, `CostCenter=Engineering`

### Task 4: Create Folder Structure and Upload Test File
In `mediaflow-raw-${your-account-id}`, create the following folder structure:
- `videos/incoming/`
- `videos/processing/`
- `thumbnails/`

Upload a test file named `test-video.txt` to `videos/incoming/` with content: "Test Upload"

## Validation

Run the validation script:
```bash
python validate_task.py
```

This will generate `test_report.log` with your results.

## Cleanup (After Assessment)
To avoid charges, delete all buckets and their contents after completing the assessment.