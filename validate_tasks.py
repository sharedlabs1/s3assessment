#!/usr/bin/env python3
"""
AWS S3 Assessment Validation Script
Triggers GitHub Action for automated testing
"""

import json
import subprocess
import sys
import os
from datetime import datetime

def trigger_github_action():
    """Trigger GitHub Action workflow"""
    print("=" * 60)
    print("AWS S3 Assessment - Validation Started")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Prompt for student ID
    student_id = input("Enter your Student ID: ").strip()
    if not student_id:
        print("ERROR: Student ID is required")
        return False
    
    print(f"Student ID: {student_id}")
    print()
    
    # GitHub repository and workflow details
    REPO = "sharedlabs1/s3assessment"
    WORKFLOW = "validate-s3.yml"
    
    print("Triggering GitHub Action for validation...")
    print(f"Repository: {REPO}")
    print(f"Workflow: {WORKFLOW}")
    print()
    
    try:
        # Trigger GitHub Action using gh CLI
        cmd = [
            "gh", "workflow", "run", WORKFLOW,
            "--repo", REPO,
            "--ref", "main",
            "-f", f"assessment_type=s3",
            "-f", f"timestamp={datetime.now().isoformat()}",
            "-f", f"student_id={student_id}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print("ERROR: Failed to trigger GitHub Action")
            print(result.stderr)
            print("\nFalling back to local validation...")
            return False
        
        print("✓ GitHub Action triggered successfully")
        print("\nWaiting for workflow to complete...")
        print("This may take 2-3 minutes...\n")
        
        # Wait for workflow to complete and fetch results
        import time
        time.sleep(10)  # Initial wait
        
        # Get latest workflow run
        get_run_cmd = [
            "gh", "run", "list",
            "--repo", REPO,
            "--workflow", WORKFLOW,
            "--limit", "1",
            "--json", "databaseId,status,conclusion"
        ]
        
        max_attempts = 30
        for attempt in range(max_attempts):
            run_result = subprocess.run(get_run_cmd, capture_output=True, text=True)
            if run_result.returncode == 0:
                runs = json.loads(run_result.stdout)
                if runs and runs[0]['status'] == 'completed':
                    run_id = runs[0]['databaseId']
                    conclusion = runs[0].get('conclusion', 'unknown')
                    
                    print(f"✓ Workflow completed with status: {conclusion}")
                    print(f"  Run ID: {run_id}")
                    
                    # Check if artifacts are available
                    list_artifacts_cmd = [
                        "gh", "run", "view", str(run_id),
                        "--repo", REPO,
                        "--json", "artifacts"
                    ]
                    
                    artifacts_result = subprocess.run(list_artifacts_cmd, capture_output=True, text=True)
                    if artifacts_result.returncode == 0:
                        artifacts_data = json.loads(artifacts_result.stdout)
                        artifacts = artifacts_data.get('artifacts', [])
                        print(f"  Found {len(artifacts)} artifact(s)")
                        
                        if not artifacts:
                            print("\n⚠ WARNING: No artifacts were created by the workflow")
                            print("This usually means the test script failed to create test_report.log")
                            print("\nTo debug, check the workflow logs:")
                            print(f"  gh run view {run_id} --repo {REPO} --log")
                            return False
                    
                    # Download artifacts (test_report.log)
                    print("\nDownloading test report...")
                    download_cmd = [
                        "gh", "run", "download", str(run_id),
                        "--repo", REPO,
                        "--name", "test-report",
                        "--dir", os.getcwd()
                    ]
                    
                    download_result = subprocess.run(download_cmd, capture_output=True, text=True, cwd=os.getcwd())
                    if download_result.returncode == 0:
                        print("✓ Test report downloaded successfully")
                        
                        # Check if report exists and display it
                        report_path = os.path.join(os.getcwd(), "test_report.log")
                        if os.path.exists(report_path):
                            print(f"✓ Report saved to: {report_path}")
                            print("\n" + "=" * 60)
                            print("TEST RESULTS")
                            print("=" * 60)
                            with open(report_path, "r") as f:
                                print(f.read())
                            return True
                        else:
                            print(f"WARNING: Report file not found at {report_path}")
                    else:
                        print(f"ERROR: Failed to download artifact")
                        print(download_result.stderr)
                        print("\nTo manually check the logs:")
                        print(f"  gh run view {run_id} --repo {REPO} --log")
                    break
            
            time.sleep(6)
            print(f"  Waiting... ({attempt + 1}/{max_attempts})")
        
        return False
        
    except FileNotFoundError:
        print("ERROR: GitHub CLI (gh) not found.")
        print("Please install: https://cli.github.com/")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = trigger_github_action()
    sys.exit(0 if success else 1)