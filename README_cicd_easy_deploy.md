CI/CD — Easy (build & simple deploy)

Goal
-----
Create a simple CI workflow that builds a repo, runs unit tests, and performs a basic deployment via a script. This tests the learner's ability to author a CI workflow and a safe deploy script.

What you must deliver
---------------------
- A GitHub Actions workflow at `cicd/github_actions.yml` that defines a job to:
  - Checkout the repo
  - Run a build step (placeholder `echo "build"` is fine)
  - Run unit tests (placeholder command acceptable)
  - Call a deploy script `cicd/deploy.sh` on success
- A deployment script at `cicd/deploy.sh` with a `TODO_CHECKLIST` describing what the script should do (e.g., copy artifacts, tag release, minimal validation)

Starter files
-------------
See `cicd/github_actions.yml` and `cicd/deploy.sh` — both include `TODO_CHECKLIST` items to guide you.

How you'll be assessed
----------------------
- The validator checks both files exist and contain `TODO_CHECKLIST`. Optionally graders may run the workflow in CI. Keep the actions simple and avoid secrets in the template.

Run tests
---------
```bash
python validate_tasks.py cicd_easy_deploy
```

Hints
-----
- Use `actions/checkout` and simple shell steps. The deploy script should be idempotent and safe to run in a test environment.
- Document any assumptions in the deploy script header.
