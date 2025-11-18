# AWS S3 Assessment - Data Lake Setup

github-repo: https://github.com/sharedlabs1/s3assessment

## Scenario
You are a cloud engineer at MediaFlow Inc. Your task is to set up a secure and cost-optimized S3 data lake infrastructure.

## Prerequisites
- Access to the shared AWS training account
- Python 3.8+ installed
- GitHub CLI (`gh`) installed and authenticated

## Setup

1. **Download the assessment files** (you only need these 3 files):
   - `validate_tasks.py`
   - `requirements.txt`
   - `README.md`

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Authenticate with GitHub CLI** (one-time setup):
```bash
gh auth login
```

That's it! You're ready to start the assessment.

## Tasks to Complete

### Task 1: Create S3 Buckets with Proper Naming
Create three S3 buckets with the following specifications:
- **Bucket 1**: `mediaflow-raw-${your-student-id}` (for raw video uploads)
- **Bucket 2**: `mediaflow-processed-${your-student-id}` (for processed content)
- **Bucket 3**: `mediaflow-archive-${your-student-id}` (for long-term archive)

Replace `${your-student-id}` with your actual student ID (e.g., if your student ID is `12345`, bucket names would be `mediaflow-raw-12345`, `mediaflow-processed-12345`, `mediaflow-archive-12345`)

**Requirements:**
- Enable versioning on the raw and processed buckets
- Enable default encryption (SSE-S3) on all buckets
- Block all public access on all buckets

### Task 2: Configure Lifecycle Policies
Set up lifecycle policies to optimize costs:

**For `mediaflow-raw-${your-student-id}`:**
- Transition objects to Standard-IA after 30 days
- Transition objects to Glacier Flexible Retrieval after 90 days
- Expire objects after 365 days

**For `mediaflow-processed-${your-student-id}`:**
- Transition non-current versions to Glacier after 30 days
- Delete non-current versions after 90 days

### Task 3: Set Up Bucket Policies and Tags
**For `mediaflow-raw-${your-student-id}`:**
- Add bucket policy to deny unencrypted uploads
- Add tags: `Environment=Production`, `Project=MediaFlow`, `CostCenter=Engineering`

**For `mediaflow-processed-${your-student-id}`:**
- Enable server access logging to `mediaflow-archive-${your-student-id}/logs/`
- Add tags: `Environment=Production`, `Project=MediaFlow`, `CostCenter=Engineering`

### Task 4: Create Folder Structure and Upload Test File
In `mediaflow-raw-${your-student-id}`, create the following folder structure:
- `videos/incoming/`
- `videos/processing/`
- `thumbnails/`

Upload a test file named `test-video.txt` to `videos/incoming/` with content: "Test Upload"

## Validation

Once you've completed all tasks, run the validation script:

```bash
python validate_tasks.py
```

You will be prompted to enter your Student ID. The script will then:
- Trigger automated tests via GitHub Actions in the central repository
- The workflow uses shared AWS credentials (configured by your instructor)
- Tests will verify YOUR specific S3 buckets (mediaflow-raw-{your-student-id}, etc.)
- Wait for the tests to complete (2-3 minutes)
- Download and display your test results
- Save the results to `test_report.log` in your local directory

**Note:** You don't need to configure AWS credentials or create GitHub secrets. Just provide your student ID when prompted, and the system will automatically test your S3 resources in the shared training account.

## Cleanup (After Assessment)
To avoid charges, delete all buckets and their contents after completing the assessment.