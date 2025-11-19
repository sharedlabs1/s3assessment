# AWS Assessment — AIML (SageMaker) + EMR (Medium)

Difficulty: 🟡 Medium

Scenario
Use EMR to preprocess data at scale and SageMaker to train and deploy a model.

Tasks (concise):

1. Create an EMR Serverless or EMR cluster `emr-preproc-<your-student-id>` and run a Spark job to clean and write training data to S3 `s3://aiml-emr-<your-student-id>/training/`.
2. Create a SageMaker training job using the prepared data (any framework or built-in algorithm).
3. Create a SageMaker endpoint (real-time) for inference and test it with a sample record.
4. Save model artifacts to S3 and register a model package in SageMaker Model Registry.
5. Optionally create a simple Lambda or script to invoke the endpoint and log results to S3.

Notes
- Minimal guidance: participants should choose suitable instance types and IAM roles.
- Focus is on correct end-to-end flow: preprocess → train → deploy → infer.

Run tests

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run validation (recommended):

```bash
python validate_tasks.py aiml_emr_medium
# enter your student id when prompted
```

This triggers the repository GitHub Action and downloads `test_report.log` into the repo root when complete.