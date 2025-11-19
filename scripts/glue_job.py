#!/usr/bin/env python3
"""Glue ETL job template (starter).

TODOs:
- Replace this template with your Glue ETL logic (PySpark / DynamicFrame).
- Use the --input and --output arguments to locate S3 paths.

This script is a small scaffold; students should implement actual transformations.
"""

import argparse


def parse_args():
    p = argparse.ArgumentParser(description='Starter Glue ETL job')
    p.add_argument('--input', required=False, help='S3 input path e.g. s3://bucket/raw/')
    p.add_argument('--output', required=False, help='S3 output path e.g. s3://bucket/processed/')
    return p.parse_args()


def main():
    args = parse_args()

    print('TODO: Replace this template with your Glue ETL code')
    print(f'Input: {args.input}')
    print(f'Output: {args.output}')

    # Example Glue skeleton (commented):
    # from awsglue.context import GlueContext
    # from pyspark.context import SparkContext
    # sc = SparkContext()
    # glueContext = GlueContext(sc)
    # spark = glueContext.spark_session
    # df = spark.read.csv(args.input, header=True, inferSchema=True)
    # # transformations
    # df.write.parquet(args.output)


if __name__ == '__main__':
    main()

# Checklist (short):
# - [ ] Initialize GlueContext and SparkContext (if running on Glue)
# - [ ] Read raw data from --input (S3 path)
# - [ ] Apply transformations and cleaning steps
# - [ ] Write processed data to --output in partitioned Parquet
# - [ ] Register or update Glue Catalog tables if required
# - [ ] Remove these TODO lines after implementing
