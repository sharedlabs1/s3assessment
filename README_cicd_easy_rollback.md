CI/CD — Easy (deploy + rollback)

Goal
-----
Implement a minimal deployment and a rollback mechanism so learners demonstrate safe release practices.

What you must deliver
---------------------
- A GitHub Actions workflow at `cicd/github_actions.yml` (can be the same as the other easy task) that triggers on push to `main` and calls deploy/rollback scripts based on a parameter.
- A rollback script at `cicd/rollback.sh` with `TODO_CHECKLIST` that explains the steps to reverse a deployment (e.g., restore previous artifact, re-point DNS placeholder, or rollback tag).

Starter files
-------------
- `cicd/github_actions.yml`
- `cicd/rollback.sh`

Assessment notes
----------------
- The validator will check that `cicd/rollback.sh` exists and contains `TODO_CHECKLIST`. The grader may inspect your workflow and scripts to ensure rollback steps are clear.

Run tests
---------
```bash
python validate_tasks.py cicd_easy_rollback
```
