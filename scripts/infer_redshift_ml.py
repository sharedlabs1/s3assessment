#!/usr/bin/env python3
"""Redshift ML inference helper template.

TODOs:
- Replace with code that calls Redshift Data API or Redshift ML prediction SQL.
- Use this script to demonstrate how you ran prediction queries and exported results.
"""

import argparse


def parse_args():
    p = argparse.ArgumentParser(description='Redshift ML inference helper')
    p.add_argument('--workgroup', required=False, help='Redshift workgroup name')
    p.add_argument('--sql-file', required=False, help='SQL file to execute for inference')
    return p.parse_args()


def main():
    args = parse_args()
    print('TODO_CHECKLIST: Use AWS CLI or boto3 redshift-data to execute inference SQL')
    print(f'Workgroup: {args.workgroup}, SQL: {args.sql_file}')

    # Example (commented):
    # import boto3
    # client = boto3.client('redshift-data')
    # resp = client.execute_statement(workgroupName=args.workgroup, database='analyticsdb', sql=open(args.sql_file).read())
    # print(resp)


if __name__ == '__main__':
    main()

# Checklist (short) — maps to Redshift+AIML tasks:
# TODO_CHECKLIST - [ ] COPY dataset from s3://redshift-ml-<student-id>/dataset/ into Redshift table
# TODO_CHECKLIST - [ ] Train model using Redshift ML or SageMaker and save model artifacts
# TODO_CHECKLIST - [ ] Run prediction SQL and export results to s3://redshift-ml-<student-id>/predictions/
# TODO_CHECKLIST - [ ] Record SQL and commands used in `notes.txt`
