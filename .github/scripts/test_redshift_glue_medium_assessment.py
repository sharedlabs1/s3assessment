"""
Test script for README_redshift_glue_medium.md
Performs 10 concise checks and writes test_report.log
"""
import sys
import os
import boto3
from botocore.exceptions import ClientError

REPORT = 'test_report.log'

def get_student_id():
    if len(sys.argv) < 2:
        print('Usage: python validate_tasks.py redshift_glue_medium <student-id>')
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


def test_glue_database(glue, db_name):
    try:
        resp = glue.get_database(Name=db_name)
        return True, f"Glue DB {db_name} exists"
    except glue.exceptions.EntityNotFoundException:
        return False, f"Glue DB {db_name} not found"
    except Exception as e:
        return False, f"Glue DB error: {e}"


def test_glue_crawler(glue, crawler_name):
    try:
        resp = glue.get_crawler(Name=crawler_name)
        return True, f"Crawler {crawler_name} exists"
    except glue.exceptions.EntityNotFoundException:
        return False, f"Crawler {crawler_name} not found"
    except Exception as e:
        return False, f"Crawler error: {e}"


def test_glue_job(glue, job_name):
    try:
        resp = glue.get_job(JobName=job_name)
        return True, f"Glue job {job_name} exists"
    except glue.exceptions.EntityNotFoundException:
        return False, f"Glue job {job_name} not found"
    except Exception as e:
        return False, f"Glue job error: {e}"


def test_parquet_in_s3(s3, bucket):
    try:
        resp = s3.list_objects_v2(Bucket=bucket, Prefix='processed/')
        return (resp.get('KeyCount',0) > 0), f"Processed parquet count: {resp.get('KeyCount',0)}"
    except Exception as e:
        return False, f"S3 list error: {e}"


def test_redshift_cluster(rs, identifier):
    try:
        resp = rs.describe_clusters(ClusterIdentifier=identifier)
        return True, f"Redshift cluster {identifier} found"
    except rs.exceptions.ClusterNotFoundFault:
        return False, f"Redshift cluster {identifier} not found"
    except Exception as e:
        return False, f"Redshift error: {e}"


def test_redshift_table(rs, cluster_id):
    # Best effort: check if SQL file exists indicating loading
    ok = os.path.exists('sql/load_to_redshift.sql')
    return ok, f"Load SQL present: {ok}"


def test_sql_queries():
    ok = os.path.exists('sql/queries.sql')
    return ok, f"Queries present: {ok}"


def test_export_results(s3, bucket):
    try:
        resp = s3.list_objects_v2(Bucket=bucket, Prefix='exports/')
        return (resp.get('KeyCount',0) > 0), f"Export objects: {resp.get('KeyCount',0)}"
    except Exception as e:
        return False, f"Export check error: {e}"


def main():
    student_id = get_student_id()
    bucket = f'redshift-glue-{student_id}'
    glue_db = f'redshift_glue_{student_id}_db'
    crawler = f'redshift-crawler-{student_id}'
    glue_job = f'redshift-etl-{student_id}'
    redshift_cluster = f'redshift-{student_id}'

    s3 = boto3.client('s3')
    glue = boto3.client('glue')
    rs = boto3.client('redshift')

    checks = []
    checks.append(test_s3_bucket(s3, bucket))
    checks.append(test_glue_database(glue, glue_db))
    checks.append(test_glue_crawler(glue, crawler))
    checks.append(test_glue_job(glue, glue_job))
    checks.append(test_parquet_in_s3(s3, bucket))
    checks.append(test_redshift_cluster(rs, redshift_cluster))
    checks.append(test_redshift_table(rs, redshift_cluster))
    checks.append(test_sql_queries())
    checks.append(test_export_results(s3, bucket))
    checks.append((True, 'Manual verification: check Redshift query output'))

    passed = sum(1 for ok, _ in checks if ok)
    total = len(checks)
    pct = (passed / total) * 100

    lines = [f"Test Summary for {student_id} - Redshift+Glue Medium", f"Passed: {passed}/{total} ({pct:.1f}%)"]
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
