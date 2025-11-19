# AWS Assessment — Redshift + AIML (Easy)

Difficulty: 🟢 Easy

Scenario
Load a small dataset into Redshift and run a simple ML prediction using either Redshift ML or SageMaker.

Tasks (concise):

1. Create an S3 bucket `redshift-ml-<your-student-id>` and upload a small CSV dataset (e.g., iris or a simple sales file).
2. Create a Redshift table and COPY the CSV from S3 into the table.
3. Using Redshift ML or a minimal SageMaker training job, train a model to predict a target column.
4. Run a few predictions (SQL or API) and save prediction output to S3.
5. Briefly document steps taken in a short `notes.txt` in the repo.

Notes
- This README is intentionally short; participants should demonstrate data load → train → predict.

Run tests

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run validation (recommended):

```bash
python validate_tasks.py redshift_aiml_easy
# enter your student id when prompted
```

The validation helper triggers the GitHub Action which produces `test_report.log` in the repository root.

Starter files (lightweight templates)

The repository includes a few starter files you can edit:

- `sql/load_to_redshift.sql` — basic CREATE/COPY SQL placeholder
- `scripts/infer_redshift_ml.py` — sample inference helper
- `notes.txt` — brief notes template

They are minimal templates — expand them with your data loading and ML steps.

See the template: `sql/load_to_redshift.sql` and `scripts/infer_redshift_ml.py` for examples and checklists.