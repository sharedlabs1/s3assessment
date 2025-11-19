# AWS Assessment — Redshift + Glue (Medium)

Difficulty: 🟡 Medium

Scenario
Build an ETL flow: land raw CSVs in S3, catalog with Glue, and load to Redshift for analytics.

Tasks (concise):

1. Create an S3 bucket `redshift-glue-<your-student-id>` and upload sample CSV files to `raw/`.
2. Create a Glue Database and a Glue Crawler that discovers the raw data and creates tables.
3. Create a Glue ETL job (PySpark) that cleans/transforms data and writes Parquet to `processed/`.
4. Load the processed Parquet files into an Amazon Redshift table (COPY from S3).
5. Run two analytical SQL queries in Redshift (e.g., aggregation and JOIN) and export results back to S3.

Notes
- Keep the README short; participants should implement typical Glue→Redshift flow.
- Provide minimal configuration values; expect them to choose sensible defaults.

Run tests

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run validation (recommended):

```bash
python validate_tasks.py redshift_glue_medium
# enter your student id when prompted
```

The helper will trigger the repository GitHub Action which produces `test_report.log` in the repo root. Inspect the action logs for troubleshooting.

Starter files (lightweight templates)

This repo provides small starter artifacts for the assessment:

- `sql/load_to_redshift.sql` — placeholder SQL for table creation/COPY
- `sql/queries.sql` — example queries students can expand
- `scripts/glue_job.py` — minimal Glue ETL script placeholder
- `CLEANUP.md` — cleanup instructions

These files are templates — replace or extend them with your ETL logic.

See the template: `sql/load_to_redshift.sql` for an example CREATE/COPY and checklist.

Templates include short inline checklists marked with the token `TODO` — the validator looks for these to guide grading.