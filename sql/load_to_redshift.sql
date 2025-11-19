-- Placeholder SQL to load data into Redshift
CREATE TABLE IF NOT EXISTS sample_table (
    id INT,
    name VARCHAR(256),
    amount DECIMAL(10,2)
);

-- COPY command would be used by students to load CSV from S3
-- COPY sample_table FROM 's3://redshift-glue-<student-id>/processed/' IAM_ROLE 'arn:aws:iam::<account-id>:role/RedshiftRole' CSV;

-- TODO_CHECKLIST: Replace the above with your own CREATE/COPY commands.
-- Example COPY (adjust bucket, IAM role and format):
-- COPY sample_table
-- FROM 's3://redshift-glue-<your-student-id>/processed/'
-- IAM_ROLE 'arn:aws:iam::<account_id>:role/RedshiftRole-<your-student-id>'
-- FORMAT AS PARQUET;

-- Checklist (short):
-- TODO_CHECKLIST - [ ] Create appropriate table schema for your dataset
-- TODO_CHECKLIST - [ ] Use COPY with correct IAM role and S3 path
-- TODO_CHECKLIST - [ ] Verify data loaded with SELECT COUNT(*)
-- TODO_CHECKLIST - [ ] Document commands used in notes.txt
