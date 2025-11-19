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

    print('TODO: Replace this template with your PySpark logic')
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
    
# Checklist (short):
# - [ ] Update this file with PySpark imports and SparkSession initialization
# - [ ] Read input from --input (S3 path) and infer schema or provide schema
# - [ ] Implement cleaning/transformation steps required by the task
# - [ ] Write results to --output in Parquet or CSV as requested
# - [ ] Remove these TODO lines after implementing
