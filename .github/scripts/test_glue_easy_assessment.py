#!/usr/bin/env python3
"""
Glue Easy Assessment Test Script
Validates basic Glue crawler, database, and ETL job configuration
"""

import boto3
import sys
import json
from datetime import datetime

class GlueEasyAssessmentTester:
    def __init__(self, student_id):
        self.student_id = student_id
        self.glue_client = boto3.client('glue')
        self.s3_client = boto3.client('s3')
        self.iam_client = boto3.client('iam')
        self.results = {
            'student_id': student_id,
            'assessment': 'glue_easy',
            'timestamp': datetime.utcnow().isoformat(),
            'tasks': {},
            'score': 0,
            'total_tasks': 8
        }
        self.bucket_name = f"glue-data-{student_id}"
        self.database_name = f"datacatalog_{student_id}"
        self.role_name = f"GlueServiceRole-{student_id}"
        self.customers_crawler = f"customers-crawler-{student_id}"
        self.orders_crawler = f"orders-crawler-{student_id}"
        self.job_name = f"customer-orders-job-{student_id}"

    def test_task1_s3_bucket(self):
        """Task 1: Verify S3 bucket with folder structure"""
        task_name = "Task 1: Create S3 Data Source"
        try:
            # Check bucket exists
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            
            issues = []
            
            # Check folder structure
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Delimiter='/'
            )
            
            required_folders = ['raw/', 'processed/']
            common_prefixes = [p['Prefix'] for p in response.get('CommonPrefixes', [])]
            
            for folder in required_folders:
                if folder not in common_prefixes:
                    issues.append(f"Missing folder: {folder}")
            
            # Check tags
            try:
                tags_response = self.s3_client.get_bucket_tagging(Bucket=self.bucket_name)
                tags = {tag['Key']: tag['Value'] for tag in tags_response['TagSet']}
                
                if tags.get('StudentID') != self.student_id:
                    issues.append("Missing or incorrect StudentID tag")
            except:
                issues.append("No tags configured on bucket")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Bucket issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'S3 bucket configured correctly',
                    'details': {'bucket': self.bucket_name}
                }
                self.results['score'] += 1
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'FAIL',
                'message': f"Bucket '{self.bucket_name}' not found or error: {str(e)}"
            }

    def test_task2_glue_database(self):
        """Task 2: Verify Glue database exists"""
        task_name = "Task 2: Create Glue Database"
        try:
            response = self.glue_client.get_database(Name=self.database_name)
            
            database = response['Database']
            
            self.results['tasks'][task_name] = {
                'status': 'PASS',
                'message': 'Glue database created successfully',
                'details': {
                    'database': self.database_name,
                    'description': database.get('Description', 'N/A')
                }
            }
            self.results['score'] += 1
            
        except self.glue_client.exceptions.EntityNotFoundException:
            self.results['tasks'][task_name] = {
                'status': 'FAIL',
                'message': f"Database '{self.database_name}' not found"
            }
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task3_iam_role(self):
        """Task 3: Verify IAM role for Glue"""
        task_name = "Task 3: Create IAM Role for Glue"
        try:
            role_response = self.iam_client.get_role(RoleName=self.role_name)
            
            issues = []
            
            # Check trust relationship
            trust_policy = role_response['Role']['AssumeRolePolicyDocument']
            glue_service_found = False
            for statement in trust_policy.get('Statement', []):
                principal = statement.get('Principal', {})
                if 'glue.amazonaws.com' in str(principal):
                    glue_service_found = True
                    break
            
            if not glue_service_found:
                issues.append("Trust policy doesn't allow Glue service")
            
            # Check attached policies
            policies_response = self.iam_client.list_attached_role_policies(
                RoleName=self.role_name
            )
            
            attached_policies = [p['PolicyName'] for p in policies_response['AttachedPolicies']]
            if 'AWSGlueServiceRole' not in attached_policies:
                issues.append("AWSGlueServiceRole policy not attached")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"IAM role issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'IAM role configured correctly',
                    'details': {'role': self.role_name}
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

    def test_task4_customers_crawler(self):
        """Task 4: Verify customers crawler"""
        task_name = "Task 4: Create Glue Crawler for Customers"
        try:
            response = self.glue_client.get_crawler(Name=self.customers_crawler)
            
            crawler = response['Crawler']
            issues = []
            
            # Check targets
            s3_targets = crawler.get('Targets', {}).get('S3Targets', [])
            if not s3_targets:
                issues.append("No S3 targets configured")
            else:
                target_path = s3_targets[0].get('Path', '')
                if 'customers' not in target_path.lower():
                    issues.append("S3 target doesn't point to customers folder")
            
            # Check database
            if crawler.get('DatabaseName') != self.database_name:
                issues.append(f"Crawler targets wrong database")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Crawler issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Customers crawler configured correctly',
                    'details': {'crawler': self.customers_crawler}
                }
                self.results['score'] += 1
                
        except self.glue_client.exceptions.EntityNotFoundException:
            self.results['tasks'][task_name] = {
                'status': 'FAIL',
                'message': f"Crawler '{self.customers_crawler}' not found"
            }
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task5_orders_crawler(self):
        """Task 5: Verify orders crawler"""
        task_name = "Task 5: Create Glue Crawler for Orders"
        try:
            response = self.glue_client.get_crawler(Name=self.orders_crawler)
            
            crawler = response['Crawler']
            issues = []
            
            # Check targets
            s3_targets = crawler.get('Targets', {}).get('S3Targets', [])
            if not s3_targets:
                issues.append("No S3 targets configured")
            else:
                target_path = s3_targets[0].get('Path', '')
                if 'orders' not in target_path.lower():
                    issues.append("S3 target doesn't point to orders folder")
            
            # Check database
            if crawler.get('DatabaseName') != self.database_name:
                issues.append(f"Crawler targets wrong database")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Crawler issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Orders crawler configured correctly',
                    'details': {'crawler': self.orders_crawler}
                }
                self.results['score'] += 1
                
        except self.glue_client.exceptions.EntityNotFoundException:
            self.results['tasks'][task_name] = {
                'status': 'FAIL',
                'message': f"Crawler '{self.orders_crawler}' not found"
            }
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task6_crawlers_executed(self):
        """Task 6: Verify crawlers have been run"""
        task_name = "Task 6: Run Crawlers"
        try:
            issues = []
            
            # Check customers crawler runs
            customers_response = self.glue_client.get_crawler_metrics(
                CrawlerNameList=[self.customers_crawler]
            )
            customers_metrics = customers_response['CrawlerMetricsList'][0] if customers_response['CrawlerMetricsList'] else None
            
            if not customers_metrics or customers_metrics.get('TablesCreated', 0) == 0:
                issues.append("Customers crawler hasn't created any tables")
            
            # Check orders crawler runs
            orders_response = self.glue_client.get_crawler_metrics(
                CrawlerNameList=[self.orders_crawler]
            )
            orders_metrics = orders_response['CrawlerMetricsList'][0] if orders_response['CrawlerMetricsList'] else None
            
            if not orders_metrics or orders_metrics.get('TablesCreated', 0) == 0:
                issues.append("Orders crawler hasn't created any tables")
            
            # Check if tables exist in database
            try:
                tables_response = self.glue_client.get_tables(DatabaseName=self.database_name)
                table_count = len(tables_response['TableList'])
                
                if table_count < 2:
                    issues.append(f"Expected at least 2 tables, found {table_count}")
            except:
                issues.append("Could not retrieve tables from database")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Crawler execution issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Crawlers executed and tables created',
                    'details': {'table_count': table_count}
                }
                self.results['score'] += 1
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task7_etl_job(self):
        """Task 7: Verify ETL job exists"""
        task_name = "Task 7: Create Basic ETL Job"
        try:
            response = self.glue_client.get_job(JobName=self.job_name)
            
            job = response['Job']
            issues = []
            
            # Check job type
            if job.get('Command', {}).get('Name') != 'glueetl':
                issues.append("Job is not a Spark ETL job")
            
            # Check Glue version
            glue_version = job.get('GlueVersion', '')
            if not glue_version.startswith('4'):
                issues.append(f"Expected Glue version 4.0, found {glue_version}")
            
            # Check worker configuration
            worker_type = job.get('WorkerType', '')
            if worker_type != 'G.1X':
                issues.append(f"Expected worker type G.1X, found {worker_type}")
            
            num_workers = job.get('NumberOfWorkers', 0)
            if num_workers < 2:
                issues.append(f"Expected at least 2 workers, found {num_workers}")
            
            # Check role
            if self.role_name not in job.get('Role', ''):
                issues.append("Job not using correct IAM role")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"ETL job issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'ETL job configured correctly',
                    'details': {
                        'job': self.job_name,
                        'glue_version': glue_version,
                        'workers': num_workers
                    }
                }
                self.results['score'] += 1
                
        except self.glue_client.exceptions.EntityNotFoundException:
            self.results['tasks'][task_name] = {
                'status': 'FAIL',
                'message': f"ETL job '{self.job_name}' not found"
            }
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task8_job_execution(self):
        """Task 8: Verify job has been executed"""
        task_name = "Task 8: Run ETL Job"
        try:
            response = self.glue_client.get_job_runs(JobName=self.job_name, MaxResults=10)
            
            job_runs = response.get('JobRuns', [])
            
            if not job_runs:
                self.results['tasks'][task_name] = {
                    'status': 'FAIL',
                    'message': 'ETL job has not been executed'
                }
                return
            
            # Check if at least one run was successful
            successful_runs = [run for run in job_runs if run.get('JobRunState') == 'SUCCEEDED']
            
            if successful_runs:
                latest_run = job_runs[0]
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'ETL job executed successfully',
                    'details': {
                        'total_runs': len(job_runs),
                        'successful_runs': len(successful_runs),
                        'latest_state': latest_run.get('JobRunState'),
                        'execution_time': latest_run.get('ExecutionTime', 'N/A')
                    }
                }
                self.results['score'] += 1
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Job executed {len(job_runs)} times but no successful runs"
                }
                self.results['score'] += 0.5
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def run_all_tests(self):
        """Run all test tasks"""
        print(f"Starting Glue Easy Assessment for Student: {self.student_id}")
        print("=" * 60)
        
        self.test_task1_s3_bucket()
        self.test_task2_glue_database()
        self.test_task3_iam_role()
        self.test_task4_customers_crawler()
        self.test_task5_orders_crawler()
        self.test_task6_crawlers_executed()
        self.test_task7_etl_job()
        self.test_task8_job_execution()
        
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
            f.write(f"Glue Easy Assessment Results\n")
            f.write(f"{'=' * 60}\n")
            f.write(f"Student ID: {self.results['student_id']}\n")
            f.write(f"Score: {self.results['score']}/{self.results['total_tasks']} ({self.results['percentage']:.1f}%)\n\n")
            
            for task_name, task_result in self.results['tasks'].items():
                f.write(f"{task_name}\n")
                f.write(f"  Status: {task_result['status']}\n")
                f.write(f"  Message: {task_result['message']}\n\n")

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_glue_easy_assessment.py <student_id>")
        sys.exit(1)
    
    student_id = sys.argv[1]
    
    try:
        tester = GlueEasyAssessmentTester(student_id)
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
