-- Placeholder Athena query
SELECT year, month, COUNT(*) as cnt
FROM processed_table
WHERE year = 2025
GROUP BY year, month
LIMIT 10;

-- TODO: Update this Athena query to point to your Glue/processed table and partitions.
-- Example:
-- SELECT year, month, COUNT(*) as cnt
-- FROM "your_database"."processed_table"
-- WHERE year = 2025
-- GROUP BY year, month
-- ORDER BY month;

-- Checklist (short):
-- TODO_CHECKLIST - [ ] Update database.table to match your Glue Catalog
-- TODO_CHECKLIST - [ ] Verify partition columns are registered in Glue
-- TODO_CHECKLIST - [ ] Run the query in Athena and save results or screenshots if required
