#!/usr/bin/env python3
"""Minimal PySpark job template (starter).

TODOs:
- Replace the skeleton below with your real PySpark transformations.
- Use the --input and --output arguments to read/write from S3 (e.g. s3://bucket/input/).

Note: This file is a template. The CI/test harness checks for a file but does not execute this script.
"""

import argparse
# If you plan to use Spark locally, uncomment the import below and create a SparkSession
# from pyspark.sql import SparkSession


def parse_args():
    p = argparse.ArgumentParser(description='Starter PySpark job')
    p.add_argument('--input', required=False, help='S3 input path e.g. s3://bucket/input/')
    p.add_argument('--output', required=False, help='S3 output path e.g. s3://bucket/output/')
    return p.parse_args()


def main():
    args = parse_args()

    print('TODO_CHECKLIST: Replace this template with your PySpark logic')
    print(f'Input path: {args.input}')
    print(f'Output path: {args.output}')

    # Example skeleton (commented):
    # spark = SparkSession.builder.appName('student-job').getOrCreate()
    # df = spark.read.csv(args.input, header=True, inferSchema=True)
    # # perform transforms
    # result = df.groupBy('col').count()
    # result.write.mode('overwrite').parquet(args.output)


if __name__ == '__main__':
    main()
    
# Checklist (short) — maps to README S3+EMR tasks:
# TODO_CHECKLIST - [ ] Create S3 bucket `s3-emr-<student-id>` and upload dataset under input/
# TODO_CHECKLIST - [ ] Read CSV from --input and infer schema or define schema
# TODO_CHECKLIST - [ ] Implement aggregation (group-by count or sum) as required by the task
# TODO_CHECKLIST - [ ] Write aggregated results to --output (S3 path) in Parquet/CSV
# TODO_CHECKLIST - [ ] Add commands used to `notes.txt` and CLEANUP.md
