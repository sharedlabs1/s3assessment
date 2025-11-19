#!/usr/bin/env python3
"""
Glue Medium Assessment Test Script
Validates advanced ETL workflows, job bookmarks, triggers, and data quality
"""

import boto3
import sys
import json
from datetime import datetime

class GlueMediumAssessmentTester:
    def __init__(self, student_id):
        self.student_id = student_id
        self.glue_client = boto3.client('glue')
        self.s3_client = boto3.client('s3')
        self.iam_client = boto3.client('iam')
        self.cloudwatch_client = boto3.client('cloudwatch')
        self.results = {
            'student_id': student_id,
            'assessment': 'glue_medium',
            'timestamp': datetime.utcnow().isoformat(),
            'tasks': {},
            'score': 0,
            'total_tasks': 9
        }
        self.bucket_name = f"glue-pipeline-{student_id}"
        self.raw_database = f"raw_data_{student_id}"
        self.processed_database = f"processed_data_{student_id}"
        self.role_name = f"GlueProductionRole-{student_id}"
        self.crawler_name = f"transactions-crawler-{student_id}"
        self.job_name = f"incremental-etl-{student_id}"
        self.workflow_name = f"etl-pipeline-{student_id}"

    def test_task1_s3_infrastructure(self):
        """Task 1: Verify S3 bucket with versioning"""
        task_name = "Task 1: Create S3 Data Infrastructure"
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            
            issues = []
            
            # Check versioning
            try:
                versioning = self.s3_client.get_bucket_versioning(Bucket=self.bucket_name)
                if versioning.get('Status') != 'Enabled':
                    issues.append("Versioning not enabled")
            except:
                issues.append("Could not check versioning")
            
            # Check lifecycle policy
            try:
                self.s3_client.get_bucket_lifecycle_configuration(Bucket=self.bucket_name)
            except self.s3_client.exceptions.NoSuchLifecycleConfiguration:
                issues.append("Lifecycle policy not configured")
            except:
                pass
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"S3 issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'S3 infrastructure configured correctly'
                }
                self.results['score'] += 1
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'FAIL',
                'message': f"Error: {str(e)}"
            }

    def test_task2_databases(self):
        """Task 2: Verify multiple Glue databases"""
        task_name = "Task 2: Create Glue Databases"
        try:
            issues = []
            
            # Check raw database
            try:
                self.glue_client.get_database(Name=self.raw_database)
            except self.glue_client.exceptions.EntityNotFoundException:
                issues.append(f"Raw database '{self.raw_database}' not found")
            
            # Check processed database
            try:
                self.glue_client.get_database(Name=self.processed_database)
            except self.glue_client.exceptions.EntityNotFoundException:
                issues.append(f"Processed database '{self.processed_database}' not found")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Database issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Multiple databases created successfully'
                }
                self.results['score'] += 1
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task3_iam_role(self):
        """Task 3: Verify enhanced IAM role"""
        task_name = "Task 3: Create Enhanced IAM Role"
        try:
            role_response = self.iam_client.get_role(RoleName=self.role_name)
            
            # Check attached policies
            policies_response = self.iam_client.list_attached_role_policies(
                RoleName=self.role_name
            )
            
            attached_policies = [p['PolicyName'] for p in policies_response['AttachedPolicies']]
            issues = []
            
            required_policies = ['AWSGlueServiceRole']
            for policy in required_policies:
                if policy not in attached_policies:
                    issues.append(f"Missing policy: {policy}")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"IAM role issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'IAM role configured correctly'
                }
                self.results['score'] += 1
                
        except self.iam_client.exceptions.NoSuchEntityException:
            self.results['tasks'][task_name] = {
                'status': 'FAIL',
                'message': f"IAM role '{self.role_name}' not found"
            }
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task4_crawler_with_schedule(self):
        """Task 4: Verify crawler with partition detection and schedule"""
        task_name = "Task 4: Create Crawler with Partition Detection"
        try:
            response = self.glue_client.get_crawler(Name=self.crawler_name)
            
            crawler = response['Crawler']
            issues = []
            
            # Check schedule
            schedule = crawler.get('Schedule')
            if not schedule or not schedule.get('ScheduleExpression'):
                issues.append("No schedule configured")
            
            # Check if crawler has been run
            if crawler.get('State') == 'READY' and crawler.get('CrawlElapsedTime', 0) == 0:
                issues.append("Crawler has never been executed")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Crawler issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Crawler configured with schedule'
                }
                self.results['score'] += 1
                
        except self.glue_client.exceptions.EntityNotFoundException:
            self.results['tasks'][task_name] = {
                'status': 'FAIL',
                'message': f"Crawler '{self.crawler_name}' not found"
            }
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task5_job_with_bookmarks(self):
        """Task 5: Verify ETL job with job bookmarks"""
        task_name = "Task 5: Create ETL Job with Job Bookmarks"
        try:
            response = self.glue_client.get_job(JobName=self.job_name)
            
            job = response['Job']
            issues = []
            
            # Check job bookmarks
            default_args = job.get('DefaultArguments', {})
            job_bookmark_option = default_args.get('--job-bookmark-option', 'job-bookmark-disable')
            
            if job_bookmark_option == 'job-bookmark-disable':
                issues.append("Job bookmarks not enabled")
            
            # Check worker configuration
            num_workers = job.get('NumberOfWorkers', 0)
            if num_workers < 5:
                issues.append(f"Expected at least 5 workers, found {num_workers}")
            
            # Check max retries
            max_retries = job.get('MaxRetries', 0)
            if max_retries < 2:
                issues.append(f"Expected max retries >= 2, found {max_retries}")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Job issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'ETL job with bookmarks configured correctly'
                }
                self.results['score'] += 1
                
        except self.glue_client.exceptions.EntityNotFoundException:
            self.results['tasks'][task_name] = {
                'status': 'FAIL',
                'message': f"Job '{self.job_name}' not found"
            }
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task6_workflow(self):
        """Task 6: Verify Glue workflow"""
        task_name = "Task 6: Create Glue Workflow"
        try:
            response = self.glue_client.get_workflow(Name=self.workflow_name)
            
            workflow = response['Workflow']
            
            # Check if workflow has nodes
            graph = workflow.get('Graph', {})
            nodes = graph.get('Nodes', [])
            
            if len(nodes) < 2:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Workflow has only {len(nodes)} nodes, expected at least 2"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Workflow created with multiple nodes',
                    'details': {'node_count': len(nodes)}
                }
                self.results['score'] += 1
                
        except self.glue_client.exceptions.EntityNotFoundException:
            self.results['tasks'][task_name] = {
                'status': 'FAIL',
                'message': f"Workflow '{self.workflow_name}' not found"
            }
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task7_triggers(self):
        """Task 7: Verify workflow triggers"""
        task_name = "Task 7: Create Workflow Triggers"
        try:
            # List all triggers
            response = self.glue_client.get_triggers()
            
            triggers = response.get('Triggers', [])
            student_triggers = [t for t in triggers if self.student_id in t['Name']]
            
            if len(student_triggers) == 0:
                self.results['tasks'][task_name] = {
                    'status': 'FAIL',
                    'message': 'No triggers found for this student'
                }
            elif len(student_triggers) < 2:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Only {len(student_triggers)} trigger found, expected 2 (scheduled and on-demand)"
                }
                self.results['score'] += 0.5
            else:
                # Check if there's a scheduled trigger
                scheduled_found = any(t.get('Type') == 'SCHEDULED' for t in student_triggers)
                on_demand_found = any(t.get('Type') == 'ON_DEMAND' for t in student_triggers)
                
                if scheduled_found and on_demand_found:
                    self.results['tasks'][task_name] = {
                        'status': 'PASS',
                        'message': 'Triggers configured correctly',
                        'details': {'trigger_count': len(student_triggers)}
                    }
                    self.results['score'] += 1
                else:
                    self.results['tasks'][task_name] = {
                        'status': 'PARTIAL',
                        'message': 'Triggers exist but missing scheduled or on-demand type'
                    }
                    self.results['score'] += 0.5
                    
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task8_data_quality(self):
        """Task 8: Verify data quality ruleset"""
        task_name = "Task 8: Implement Data Quality Rules"
        try:
            # List data quality rulesets
            response = self.glue_client.list_data_quality_rulesets()
            
            rulesets = response.get('Rulesets', [])
            student_rulesets = [r for r in rulesets if self.student_id in r.get('Name', '')]
            
            if len(student_rulesets) == 0:
                self.results['tasks'][task_name] = {
                    'status': 'FAIL',
                    'message': 'No data quality rulesets found'
                }
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Data quality ruleset created',
                    'details': {'ruleset_count': len(student_rulesets)}
                }
                self.results['score'] += 1
                
        except Exception as e:
            # Data quality might not be available in all regions
            self.results['tasks'][task_name] = {
                'status': 'PARTIAL',
                'message': f"Could not verify data quality (might not be available): {str(e)}"
            }
            self.results['score'] += 0.5

    def test_task9_monitoring(self):
        """Task 9: Verify CloudWatch monitoring"""
        task_name = "Task 9: Configure Job Monitoring"
        try:
            # Check for CloudWatch alarms
            alarms_response = self.cloudwatch_client.describe_alarms(
                AlarmNamePrefix=f"glue-job"
            )
            
            alarms = alarms_response.get('MetricAlarms', [])
            student_alarms = [a for a in alarms if self.student_id in a['AlarmName']]
            
            if len(student_alarms) == 0:
                self.results['tasks'][task_name] = {
                    'status': 'FAIL',
                    'message': 'No CloudWatch alarms configured'
                }
            elif len(student_alarms) < 2:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Only {len(student_alarms)} alarm found, expected at least 2"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'CloudWatch monitoring configured',
                    'details': {'alarm_count': len(student_alarms)}
                }
                self.results['score'] += 1
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def run_all_tests(self):
        """Run all test tasks"""
        print(f"Starting Glue Medium Assessment for Student: {self.student_id}")
        print("=" * 60)
        
        self.test_task1_s3_infrastructure()
        self.test_task2_databases()
        self.test_task3_iam_role()
        self.test_task4_crawler_with_schedule()
        self.test_task5_job_with_bookmarks()
        self.test_task6_workflow()
        self.test_task7_triggers()
        self.test_task8_data_quality()
        self.test_task9_monitoring()
        
        self.results['percentage'] = (self.results['score'] / self.results['total_tasks']) * 100
        return self.results

    def print_results(self):
        """Print formatted results"""
        print("\n" + "=" * 60)
        print("ASSESSMENT RESULTS")
        print("=" * 60)
        print(f"Student ID: {self.results['student_id']}")
        print(f"Assessment: {self.results['assessment']}")
        print(f"Score: {self.results['score']}/{self.results['total_tasks']} ({self.results['percentage']:.1f}%)")
        print("\nTask Results:")
        print("-" * 60)
        
        for task_name, task_result in self.results['tasks'].items():
            status_emoji = {'PASS': '✓', 'FAIL': '✗', 'PARTIAL': '~', 'ERROR': '!'}.get(task_result['status'], '?')
            print(f"\n{status_emoji} {task_name}")
            print(f"  Status: {task_result['status']}")
            print(f"  {task_result['message']}")

    def save_results(self, filename='test_report.log'):
        """Save results to file"""
        with open(filename, 'w') as f:
            f.write(f"Glue Medium Assessment Results\n")
            f.write(f"{'=' * 60}\n")
            f.write(f"Student ID: {self.results['student_id']}\n")
            f.write(f"Score: {self.results['score']}/{self.results['total_tasks']} ({self.results['percentage']:.1f}%)\n\n")
            
            for task_name, task_result in self.results['tasks'].items():
                f.write(f"{task_name}\n")
                f.write(f"  Status: {task_result['status']}\n")
                f.write(f"  Message: {task_result['message']}\n\n")

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_glue_medium_assessment.py <student_id>")
        sys.exit(1)
    
    student_id = sys.argv[1]
    
    try:
        tester = GlueMediumAssessmentTester(student_id)
        tester.run_all_tests()
        tester.print_results()
        tester.save_results()
        
        if tester.results['percentage'] >= 70:
            print("\n✓ Assessment PASSED!")
            sys.exit(0)
        else:
            print("\n✗ Assessment FAILED.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n✗ Assessment ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
