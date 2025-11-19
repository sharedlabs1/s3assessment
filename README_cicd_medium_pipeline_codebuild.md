CI/CD — Medium (CodeBuild / CodePipeline pipeline)

Goal
-----
Create starter artifacts for an AWS CodeBuild / CodePipeline-based pipeline: a `buildspec.yml` and a CloudFormation template for a simple pipeline.

What you must deliver
---------------------
- A `cicd/buildspec.yml` file containing build phases and a `TODO_CHECKLIST` describing required steps (install, build, test, artifacts).
- A starter `cicd/codepipeline_template.yaml` CloudFormation template skeleton that defines a pipeline resource (sections left as TODO with `TODO_CHECKLIST`).

Starter files
-------------
- `cicd/buildspec.yml`
- `cicd/codepipeline_template.yaml`

Assessment
----------
- Validator checks the files exist and contain `TODO_CHECKLIST`. The grader may deploy or inspect the pipeline skeleton to ensure parameters and artifact store are reasonable.

Run tests
---------
```bash
python validate_tasks.py cicd_medium_pipeline_codebuild
```

Hints
-----
- Keep resource names parameterized and include Outputs for pipeline name or role ARN placeholders.
