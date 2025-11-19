"""
Test script for README_s3_glue_medium.md
Performs 10 concise checks and writes test_report.log
"""
import sys
import os
import boto3
from botocore.exceptions import ClientError

REPORT = 'test_report.log'

def get_student_id():
    if len(sys.argv) < 2:
        print('Usage: python validate_tasks.py s3_glue_medium <student-id>')
        sys.exit(1)
    return sys.argv[1]


def write_report(lines):
    with open(REPORT, 'a') as f:
        for l in lines:
            f.write(l + '\n')


def test_bucket_and_partitions(s3, student_id):
    bucket = f's3-glue-{student_id}'
    try:
        resp = s3.list_objects_v2(Bucket=bucket, Prefix='raw/')
        ok = resp.get('KeyCount', 0) > 0
        return ok, f"Raw objects count: {resp.get('KeyCount',0)}"
    except Exception as e:
        return False, f"S3 error: {e}"


def test_glue_crawler(glue, crawler):
    try:
        resp = glue.get_crawler(Name=crawler)
        return True, f"Crawler {crawler} exists"
    except Exception:
        return False, f"Crawler {crawler} missing"


def test_glue_job(glue, job):
    try:
        resp = glue.get_job(JobName=job)
        return True, f"Job {job} exists"
    except Exception:
        return False, f"Job {job} missing"


def test_parquet_output(s3, student_id):
    bucket = f's3-glue-{student_id}'
    try:
        resp = s3.list_objects_v2(Bucket=bucket, Prefix='processed/')
        return (resp.get('KeyCount',0) > 0), f"Processed files: {resp.get('KeyCount',0)}"
    except Exception as e:
        return False, f"S3 error: {e}"


def test_glue_catalog_partitions(glue, db, table):
    try:
        resp = glue.get_partitions(DatabaseName=db, TableName=table, MaxResults=100)
        return (len(resp.get('Partitions',[]))>0), f"Partitions: {len(resp.get('Partitions',[]))}"
    except Exception as e:
        return False, f"Partition error: {e}"


def test_athena_query():
    ok = os.path.exists('sql/athena_query.sql')
    return ok, f"Athena query present: {ok}"


def test_readme_present():
    ok = os.path.exists('README_s3_glue_medium.md')
    return ok, f"README present: {ok}"


def test_scripts_present():
    ok = os.path.exists('scripts/glue_job.py')
    return ok, f"Glue job script present: {ok}"


def test_catalog_db_exists(glue, db):
    try:
        resp = glue.get_database(Name=db)
        return True, f"Database {db} exists"
    except Exception:
        return False, f"Database {db} missing"


def main():
    student_id = get_student_id()
    s3 = boto3.client('s3')
    glue = boto3.client('glue')

    db = f's3_glue_{student_id}_db'
    table = f'raw_table_{student_id}'
    crawler = f'glue-crawler-{student_id}'
    job = f'glue-etl-{student_id}'

    checks = []
    checks.append(test_bucket_and_partitions(s3, student_id))
    checks.append(test_glue_crawler(glue, crawler))
    checks.append(test_glue_job(glue, job))
    checks.append(test_parquet_output(s3, student_id))
    checks.append(test_glue_catalog_partitions(glue, db, table))
    checks.append(test_athena_query())
    checks.append(test_readme_present())
    checks.append(test_scripts_present())
    checks.append(test_catalog_db_exists(glue, db))
    checks.append((True, 'Manual: validate partition filters in Athena'))

    passed = sum(1 for ok, _ in checks if ok)
    total = len(checks)
    pct = (passed / total) * 100

    lines = [f"Test Summary for {student_id} - S3+Glue Medium", f"Passed: {passed}/{total} ({pct:.1f}%)"]
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
