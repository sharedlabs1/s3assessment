CI/CD — Medium (Blue/Green deployment)

Goal
-----
Design a blue/green deployment pipeline using GitHub Actions and simple scripts to switch traffic between two environments. This tests deployment orchestration and safe cutover.

What you must deliver
---------------------
- A GitHub Actions workflow skeleton at `cicd/blue_green_workflow.yml` that contains jobs for build, deploy-green, deploy-blue, and a manual switch step.
- A traffic switch helper `cicd/switch_traffic.sh` with `TODO_CHECKLIST` describing how to perform the switch (in real infra this could be via DNS/TG swap; for this exercise use a placeholder action and explain how to perform the switch safely).

Starter files
-------------
- `cicd/blue_green_workflow.yml`
- `cicd/switch_traffic.sh`

Assessment and verification
---------------------------
- The validator checks starter files exist and include `TODO_CHECKLIST`. Your workflow should include a manual approval step for the traffic switch (use `workflow_dispatch` or `environment` protection if desired).

Run tests
---------
```bash
python validate_tasks.py cicd_medium_bluegreen
```

Hints
-----
- Keep the implementation conceptual: document how the switch would be executed and what checks (smoke tests) you would run before switching traffic.
