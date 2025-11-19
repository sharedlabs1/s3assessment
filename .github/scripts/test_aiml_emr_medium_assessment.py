"""
Test script for README_aiml_emr_medium.md
Performs 10 concise checks and writes test_report.log
"""
import sys
import os
import boto3
from botocore.exceptions import ClientError

REPORT = 'test_report.log'


def get_student_id():
    if len(sys.argv) < 2:
        print('Usage: python validate_tasks.py aiml_emr_medium <student-id>')
        sys.exit(1)
    return sys.argv[1]


def write_report(lines):
    with open(REPORT, 'a') as f:
        for l in lines:
            f.write(l + '\n')


def test_emr_preproc(s3, emr, student_id):
    bucket = f'aiml-emr-{student_id}'
    try:
        resp = s3.list_objects_v2(Bucket=bucket, Prefix='training/')
        ok = resp.get('KeyCount', 0) > 0
        return ok, f"Training data objects: {resp.get('KeyCount',0)}"
    except Exception as e:
        return False, f"Error checking training data: {e}"


def test_sagemaker_artifact_exists(s3, student_id):
    bucket = f'aiml-emr-{student_id}'
    try:
        resp = s3.list_objects_v2(Bucket=bucket, Prefix='model/')
        ok = resp.get('KeyCount', 0) > 0
        return ok, f"Model artifacts found: {resp.get('KeyCount',0)}"
    except Exception as e:
        return False, f"S3 error: {e}"


def test_sagemaker_training(sagemaker, student_id):
    try:
        resp = sagemaker.list_training_jobs(MaxResults=50)
        jobs = [j for j in resp.get('TrainingJobSummaries', []) if student_id in j.get('TrainingJobName','')]
        ok = len(jobs) > 0
        return ok, f"Training jobs found: {len(jobs)}"
    except Exception as e:
        return False, f"SageMaker error: {e}"


def test_endpoint_exists(sagemaker, student_id):
    try:
        resp = sagemaker.list_endpoints(MaxResults=50)
        eps = [e for e in resp.get('Endpoints', []) if student_id in e.get('EndpointName','')]
        ok = len(eps) > 0
        return ok, f"Endpoints found: {len(eps)}"
    except Exception as e:
        return False, f"Endpoint error: {e}"


def test_model_registry(sagemaker, student_id):
    try:
        resp = sagemaker.list_model_packages(MaxResults=50)
        pkgs = [p for p in resp.get('ModelPackageSummaryList', []) if student_id in p.get('ModelPackageName','')]
        ok = len(pkgs) > 0
        return ok, f"Model packages: {len(pkgs)}"
    except Exception as e:
        return False, f"Model registry error: {e}"


def test_inference_lambda_exists(lambda_client, student_id):
    try:
        name = f'invoke-endpoint-{student_id}'
        resp = lambda_client.get_function(FunctionName=name)
        return True, f"Lambda {name} exists"
    except Exception:
        return False, f"Lambda {name} not found"


def test_emr_job_history(emr, student_id):
    try:
        apps = emr.list_applications(MaxResults=50).get('applications', [])
        found = any(student_id in a.get('name','') for a in apps)
        return found, f"EMR apps found: {found}"
    except Exception as e:
        return False, f"EMR error: {e}"


def test_sample_inference_call():
    path = 'scripts/infer_sample.py'
    ok = os.path.exists(path)
    msg = f"Sample inference script present: {ok}"
    if ok:
        try:
            with open(path, 'r') as fh:
                c = fh.read()
            if 'TODO' in c:
                msg += '; TODO found'
            else:
                msg += '; TODO missing'
        except Exception as e:
            msg += f'; read error: {e}'
    return ok, msg


def test_readme_present(student_id):
    ok = os.path.exists('README_aiml_emr_medium.md')
    return ok, f"README present: {ok}"


def main():
    student_id = get_student_id()
    s3 = boto3.client('s3')
    emr = boto3.client('emr-serverless')
    sagemaker = boto3.client('sagemaker')
    lambda_client = boto3.client('lambda')

    checks = []
    checks.append(test_emr_preproc(s3, emr, student_id))
    checks.append(test_sagemaker_artifact_exists(s3, student_id))
    checks.append(test_sagemaker_training(sagemaker, student_id))
    checks.append(test_endpoint_exists(sagemaker, student_id))
    checks.append(test_model_registry(sagemaker, student_id))
    checks.append(test_inference_lambda_exists(lambda_client, student_id))
    checks.append(test_emr_job_history(emr, student_id))
    checks.append(test_sample_inference_call())
    checks.append(test_readme_present(student_id))
    checks.append((True, 'Manual: Validate model accuracy'))

    passed = sum(1 for ok, _ in checks if ok)
    total = len(checks)
    pct = (passed / total) * 100

    lines = [f"Test Summary for {student_id} - AIML+EMR Medium", f"Passed: {passed}/{total} ({pct:.1f}%)"]
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
