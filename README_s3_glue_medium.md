# AWS Assessment — S3 + Glue (Medium)

Difficulty: 🟡 Medium

Scenario
Work with partitioned data in S3 and create Glue-based ETL to prepare it for analytics.

Tasks (concise):

1. Create S3 bucket `s3-glue-<your-student-id>` and place CSV data partitioned by `year=` and `month=` under `raw/`.
2. Create a Glue Database and a Crawler to register the partitioned table.
3. Create a Glue ETL job that reads partitioned input, converts to partitioned Parquet, and writes to `processed/`.
4. Verify partitions appear in the Glue Catalog and you can query them (e.g., select year/month filtered data).
5. Create a short Athena query that reads processed Parquet and returns a small result set.

Notes
- Keep instructions concise so the participant demonstrates Glue partition handling and catalog usage.

Run tests

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run validation (recommended):

```bash
python validate_tasks.py s3_glue_medium
# enter your student id when prompted
```

The GitHub Action will run the checks and place `test_report.log` in the repository root for retrieval.

Starter files (lightweight templates)

Included starter artifacts:

- `scripts/glue_job.py` — minimal Glue ETL script to edit
- `sql/athena_query.sql` — placeholder Athena query example
- `notes.txt` — notes template

These are small templates intended to help you get started; replace them with your ETL code.

See the template: `scripts/glue_job.py` and `sql/athena_query.sql` for skeletons and checklists.