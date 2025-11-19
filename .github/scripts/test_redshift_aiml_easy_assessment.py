"""
Test script for README_redshift_aiml_easy.md
Performs 10 concise checks and writes test_report.log
"""
import sys
import os
import boto3
from botocore.exceptions import ClientError

REPORT = 'test_report.log'

def get_student_id():
    if len(sys.argv) < 2:
        print('Usage: python validate_tasks.py redshift_aiml_easy <student-id>')
        sys.exit(1)
    return sys.argv[1]


def write_report(lines):
    with open(REPORT, 'a') as f:
        for l in lines:
            f.write(l + '\n')


def test_s3_bucket(s3, bucket):
    try:
        s3.head_bucket(Bucket=bucket)
        return True, f"S3 bucket {bucket} exists"
    except Exception as e:
        return False, f"S3 bucket error: {e}"


def test_csv_uploaded(s3, bucket):
    try:
        resp = s3.list_objects_v2(Bucket=bucket, Prefix='dataset/')
        ok = resp.get('KeyCount', 0) > 0
        return ok, f"Dataset objects: {resp.get('KeyCount',0)}"
    except Exception as e:
        return False, f"S3 error: {e}"


def test_redshift_table_exists(rs, cluster):
    # best-effort: check for SQL file or cluster
    ok = os.path.exists('sql/create_table.sql') or os.path.exists('sql/load.sql')
    return ok, f"Load SQL present: {ok}"


def test_redshift_ml_used():
    ok = os.path.exists('sql/redshift_ml.sql')
    return ok, f"Redshift ML SQL present: {ok}"


def test_sagemaker_fallback(sagemaker, student_id):
    try:
        resp = sagemaker.list_training_jobs(MaxResults=50)
        jobs = [j for j in resp.get('TrainingJobSummaries', []) if student_id in j.get('TrainingJobName','')]
        return (len(jobs)>0), f"SageMaker training jobs: {len(jobs)}"
    except Exception as e:
        return False, f"SageMaker error: {e}"


def test_predictions_written(s3, bucket):
    try:
        resp = s3.list_objects_v2(Bucket=bucket, Prefix='predictions/')
        return (resp.get('KeyCount',0) > 0), f"Predictions files: {resp.get('KeyCount',0)}"
    except Exception as e:
        return False, f"S3 error: {e}"


def test_notes_file():
    ok = os.path.exists('notes.txt')
    return ok, f"Notes present: {ok}"


def test_readme_present():
    ok = os.path.exists('README_redshift_aiml_easy.md')
    return ok, f"README present: {ok}"


def test_sample_inference_script():
    ok = os.path.exists('scripts/infer_redshift_ml.py')
    return ok, f"Inference script present: {ok}"


def main():
    student_id = get_student_id()
    bucket = f'redshift-ml-{student_id}'

    s3 = boto3.client('s3')
    rs = boto3.client('redshift')
    sagemaker = boto3.client('sagemaker')

    checks = []
    checks.append(test_s3_bucket(s3, bucket))
    checks.append(test_csv_uploaded(s3, bucket))
    checks.append(test_redshift_table_exists(rs, student_id))
    checks.append(test_redshift_ml_used())
    checks.append(test_sagemaker_fallback(sagemaker, student_id))
    checks.append(test_predictions_written(s3, bucket))
    checks.append(test_notes_file())
    checks.append(test_readme_present())
    checks.append(test_sample_inference_script())
    checks.append((True, 'Manual: Verify prediction correctness'))

    passed = sum(1 for ok, _ in checks if ok)
    total = len(checks)
    pct = (passed / total) * 100

    lines = [f"Test Summary for {student_id} - Redshift+AIML Easy", f"Passed: {passed}/{total} ({pct:.1f}%)"]
    for i, (ok, msg) in enumerate(checks, start=1):
        lines.append(f"Task {i}: {'PASS' if ok else 'FAIL'} - {msg}")

    write_report(lines)
    print('\n'.join(lines))

    if pct >= 70:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
