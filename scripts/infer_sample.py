#!/usr/bin/env python3
"""Inference helper template.

TODOs:
- Replace with real endpoint invocation using boto3 (SageMaker runtime) or other client.
- Provide --endpoint argument to call a deployed model.
"""

import argparse
import json


def parse_args():
	p = argparse.ArgumentParser(description='Sample inference helper')
	p.add_argument('--endpoint', required=False, help='SageMaker endpoint name')
	p.add_argument('--payload', required=False, help='JSON payload or path')
	return p.parse_args()


def main():
	args = parse_args()

	payload = {"features": [1, 2, 3]} if not args.payload else args.payload
	print('TODO_CHECKLIST: Replace this mock with a real inference call to your endpoint')
	print('Endpoint:', args.endpoint)
	print('Payload:', payload)

	# Example (commented):
	# import boto3
	# runtime = boto3.client('sagemaker-runtime')
	# resp = runtime.invoke_endpoint(EndpointName=args.endpoint,
	#                                ContentType='application/json',
	#                                Body=json.dumps(payload))
	# print(resp['Body'].read())


if __name__ == '__main__':
	main()

# Checklist (short) — maps to AIML+EMR tasks:
# TODO_CHECKLIST - [ ] Ensure training data is written to s3://aiml-emr-<student-id>/training/
# TODO_CHECKLIST - [ ] Provide --endpoint to call the real SageMaker endpoint
# TODO_CHECKLIST - [ ] Invoke endpoint and write prediction results to S3 (e.g., s3://aiml-emr-<student-id>/predictions/)
# TODO_CHECKLIST - [ ] Document inference steps and sample payloads in `notes.txt`
