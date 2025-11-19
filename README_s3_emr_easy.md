# AWS Assessment — S3 + EMR (Easy)

Difficulty: 🟢 Easy

Scenario
You will stage data in S3 and run a simple Spark job on EMR Serverless to process it.

Tasks (concise):

1. Create an S3 bucket named `s3-emr-<your-student-id>` and upload a CSV dataset into `input/`.
2. Create an EMR Serverless application named `emr-spark-<your-student-id>`.
3. Submit a simple Spark job that reads `s3://s3-emr-<your-student-id>/input/` and writes aggregated results to `s3://s3-emr-<your-student-id>/output/`.
4. Verify output files exist and contain aggregated rows (e.g., group-by count).
5. Clean up EMR job runs and stop/delete Serverless application if desired.

Notes
- Keep code short: a single PySpark script is sufficient.
- This README is intentionally brief — test participant's ability to implement the steps independent of detailed guidance.

Run tests

1. Install dependencies (locally or in CI):

```bash
pip install -r requirements.txt
```

2. Run validation (recommended):

```bash
python validate_tasks.py s3_emr_easy
# enter your student id when prompted
```

The validation helper triggers the repository GitHub Action which runs the checks and downloads `test_report.log` into the repository root. Use the GitHub Action run logs to debug failures.