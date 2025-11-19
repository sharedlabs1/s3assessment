#!/usr/bin/env python3
"""
Glue Hard Assessment Test Script
Validates enterprise Glue features including DataBrew, Schema Registry, Lake Formation, custom classifiers
"""

import boto3
import sys
import json
from datetime import datetime

class GlueHardAssessmentTester:
    def __init__(self, student_id):
        self.student_id = student_id
        self.glue_client = boto3.client('glue')
        self.s3_client = boto3.client('s3')
        self.iam_client = boto3.client('iam')
        self.kms_client = boto3.client('kms')
        self.cloudwatch_client = boto3.client('cloudwatch')
        try:
            self.databrew_client = boto3.client('databrew')
        except:
            self.databrew_client = None
        try:
            self.lakeformation_client = boto3.client('lakeformation')
        except:
            self.lakeformation_client = None
        
        self.results = {
            'student_id': student_id,
            'assessment': 'glue_hard',
            'timestamp': datetime.utcnow().isoformat(),
            'tasks': {},
            'score': 0,
            'total_tasks': 10
        }
        self.bucket_name = f"enterprise-datalake-{student_id}"
        self.registry_name = f"enterprise-registry-{student_id}"
        self.classifier_name = f"custom-log-classifier-{student_id}"
        self.crawler_name = f"enterprise-crawler-{student_id}"
        self.workflow_name = f"enterprise-pipeline-{student_id}"

    def test_task1_enterprise_datalake(self):
        """Task 1: Verify enterprise S3 data lake with encryption"""
        task_name = "Task 1: Create Enterprise S3 Data Lake"
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
            
            # Check encryption
            try:
                encryption = self.s3_client.get_bucket_encryption(Bucket=self.bucket_name)
                rules = encryption.get('ServerSideEncryptionConfiguration', {}).get('Rules', [])
                if not rules:
                    issues.append("Encryption not configured")
                else:
                    sse_algorithm = rules[0].get('ApplyServerSideEncryptionByDefault', {}).get('SSEAlgorithm')
                    if sse_algorithm != 'aws:kms':
                        issues.append("Not using KMS encryption")
            except:
                issues.append("Could not verify encryption")
            
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
                    'message': f"Data lake issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Enterprise data lake configured correctly'
                }
                self.results['score'] += 1
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'FAIL',
                'message': f"Error: {str(e)}"
            }

    def test_task2_multi_database_architecture(self):
        """Task 2: Verify medallion architecture databases"""
        task_name = "Task 2: Create Multi-Database Architecture"
        try:
            issues = []
            required_databases = [
                f"landing_{self.student_id}",
                f"bronze_{self.student_id}",
                f"silver_{self.student_id}",
                f"gold_{self.student_id}"
            ]
            
            for db_name in required_databases:
                try:
                    self.glue_client.get_database(Name=db_name)
                except self.glue_client.exceptions.EntityNotFoundException:
                    issues.append(f"Database '{db_name}' not found")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Database issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Medallion architecture databases created',
                    'details': {'database_count': len(required_databases)}
                }
                self.results['score'] += 1
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task3_lake_formation(self):
        """Task 3: Verify Lake Formation configuration"""
        task_name = "Task 3: Configure Lake Formation"
        try:
            if not self.lakeformation_client:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': 'Lake Formation client not available in this region'
                }
                self.results['score'] += 0.5
                return
            
            # Check if S3 location is registered
            response = self.lakeformation_client.list_resources()
            
            resources = response.get('ResourceInfoList', [])
            s3_resources = [r for r in resources if self.bucket_name in r.get('ResourceArn', '')]
            
            if s3_resources:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Lake Formation configured',
                    'details': {'registered_resources': len(s3_resources)}
                }
                self.results['score'] += 1
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': 'S3 location not registered with Lake Formation'
                }
                self.results['score'] += 0.5
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'PARTIAL',
                'message': f"Lake Formation check incomplete: {str(e)}"
            }
            self.results['score'] += 0.5

    def test_task4_custom_classifier(self):
        """Task 4: Verify custom classifier"""
        task_name = "Task 4: Create Custom Classifier"
        try:
            response = self.glue_client.get_classifier(Name=self.classifier_name)
            
            classifier = response['Classifier']
            
            # Check if it's a Grok classifier
            if 'GrokClassifier' in classifier:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Custom Grok classifier created',
                    'details': {
                        'classifier': self.classifier_name,
                        'type': 'Grok'
                    }
                }
                self.results['score'] += 1
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': 'Classifier exists but not Grok type'
                }
                self.results['score'] += 0.5
                
        except self.glue_client.exceptions.EntityNotFoundException:
            self.results['tasks'][task_name] = {
                'status': 'FAIL',
                'message': f"Custom classifier '{self.classifier_name}' not found"
            }
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task5_schema_registry(self):
        """Task 5: Verify Schema Registry"""
        task_name = "Task 5: Set Up Schema Registry"
        try:
            response = self.glue_client.get_registry(RegistryId={'RegistryName': self.registry_name})
            
            registry = response
            
            # List schemas in registry
            schemas_response = self.glue_client.list_schemas(
                RegistryId={'RegistryName': self.registry_name}
            )
            
            schemas = schemas_response.get('Schemas', [])
            
            if len(schemas) >= 2:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Schema Registry with schemas created',
                    'details': {
                        'registry': self.registry_name,
                        'schema_count': len(schemas)
                    }
                }
                self.results['score'] += 1
            elif len(schemas) > 0:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f'Registry exists with {len(schemas)} schema(s), expected at least 2'
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': 'Registry exists but no schemas defined'
                }
                self.results['score'] += 0.5
                
        except self.glue_client.exceptions.EntityNotFoundException:
            self.results['tasks'][task_name] = {
                'status': 'FAIL',
                'message': f"Schema Registry '{self.registry_name}' not found"
            }
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task6_advanced_crawler(self):
        """Task 6: Verify advanced crawler with custom classifier"""
        task_name = "Task 6: Create Advanced Crawler with Custom Classifier"
        try:
            response = self.glue_client.get_crawler(Name=self.crawler_name)
            
            crawler = response['Crawler']
            issues = []
            
            # Check if custom classifier is assigned
            classifiers = crawler.get('Classifiers', [])
            if self.classifier_name not in classifiers:
                issues.append("Custom classifier not assigned to crawler")
            
            # Check schedule
            schedule = crawler.get('Schedule')
            if not schedule or not schedule.get('ScheduleExpression'):
                issues.append("No schedule configured")
            
            # Check multiple data sources
            s3_targets = crawler.get('Targets', {}).get('S3Targets', [])
            if len(s3_targets) < 2:
                issues.append(f"Expected multiple S3 targets, found {len(s3_targets)}")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Crawler issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Advanced crawler configured correctly'
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

    def test_task7_databrew_project(self):
        """Task 7: Verify DataBrew project"""
        task_name = "Task 7: Create DataBrew Project"
        try:
            if not self.databrew_client:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': 'DataBrew not available in this region'
                }
                self.results['score'] += 0.5
                return
            
            # List DataBrew projects
            response = self.databrew_client.list_projects()
            
            projects = response.get('Projects', [])
            student_projects = [p for p in projects if self.student_id in p.get('Name', '')]
            
            if len(student_projects) > 0:
                # Check for recipe
                project = student_projects[0]
                if project.get('RecipeName'):
                    self.results['tasks'][task_name] = {
                        'status': 'PASS',
                        'message': 'DataBrew project with recipe created'
                    }
                    self.results['score'] += 1
                else:
                    self.results['tasks'][task_name] = {
                        'status': 'PARTIAL',
                        'message': 'DataBrew project exists but no recipe'
                    }
                    self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'FAIL',
                    'message': 'No DataBrew project found'
                }
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'PARTIAL',
                'message': f"DataBrew check incomplete: {str(e)}"
            }
            self.results['score'] += 0.5

    def test_task8_studio_visual_etl(self):
        """Task 8: Verify Glue Studio visual ETL job"""
        task_name = "Task 8: Create Glue Studio Visual ETL Job"
        try:
            # List all jobs and look for Studio jobs
            response = self.glue_client.get_jobs()
            
            jobs = response.get('Jobs', [])
            student_jobs = [j for j in jobs if self.student_id in j.get('Name', '')]
            
            # Check for visual jobs (they have CodeGenConfigurationNodes)
            visual_jobs = [j for j in student_jobs if 'CodeGenConfigurationNodes' in j]
            
            if len(visual_jobs) > 0:
                job = visual_jobs[0]
                # Check if it has multiple nodes
                nodes = job.get('CodeGenConfigurationNodes', {})
                if len(nodes) >= 5:
                    self.results['tasks'][task_name] = {
                        'status': 'PASS',
                        'message': 'Glue Studio visual ETL job created',
                        'details': {'node_count': len(nodes)}
                    }
                    self.results['score'] += 1
                else:
                    self.results['tasks'][task_name] = {
                        'status': 'PARTIAL',
                        'message': f'Visual job exists with {len(nodes)} nodes, expected at least 5'
                    }
                    self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'FAIL',
                    'message': 'No Glue Studio visual ETL job found'
                }
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task9_complex_workflow(self):
        """Task 9: Verify complex workflow with multiple stages"""
        task_name = "Task 10: Create Complex Workflow with Multiple Triggers"
        try:
            response = self.glue_client.get_workflow(Name=self.workflow_name)
            
            workflow = response['Workflow']
            graph = workflow.get('Graph', {})
            nodes = graph.get('Nodes', [])
            
            if len(nodes) >= 5:
                # Check for triggers
                triggers_response = self.glue_client.get_triggers()
                triggers = triggers_response.get('Triggers', [])
                workflow_triggers = [t for t in triggers if self.workflow_name in str(t.get('Actions', []))]
                
                if len(workflow_triggers) >= 2:
                    self.results['tasks'][task_name] = {
                        'status': 'PASS',
                        'message': 'Complex workflow with multiple stages created',
                        'details': {
                            'node_count': len(nodes),
                            'trigger_count': len(workflow_triggers)
                        }
                    }
                    self.results['score'] += 1
                else:
                    self.results['tasks'][task_name] = {
                        'status': 'PARTIAL',
                        'message': f'Workflow has {len(nodes)} nodes but only {len(workflow_triggers)} triggers'
                    }
                    self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f'Workflow has {len(nodes)} nodes, expected at least 5'
                }
                self.results['score'] += 0.5
                
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

    def test_task10_security_configuration(self):
        """Task 12: Verify security configuration"""
        task_name = "Task 12: Configure Security and Encryption"
        try:
            # List security configurations
            response = self.glue_client.get_security_configurations()
            
            configs = response.get('SecurityConfigurations', [])
            student_configs = [c for c in configs if self.student_id in c.get('Name', '')]
            
            if len(student_configs) > 0:
                config = student_configs[0]
                encryption_config = config.get('EncryptionConfiguration', {})
                
                # Check S3 encryption
                s3_encryption = encryption_config.get('S3Encryption', [])
                # Check CloudWatch encryption
                cw_encryption = encryption_config.get('CloudWatchEncryption', {})
                
                if s3_encryption and cw_encryption:
                    self.results['tasks'][task_name] = {
                        'status': 'PASS',
                        'message': 'Security configuration with encryption created'
                    }
                    self.results['score'] += 1
                else:
                    self.results['tasks'][task_name] = {
                        'status': 'PARTIAL',
                        'message': 'Security configuration incomplete (missing S3 or CloudWatch encryption)'
                    }
                    self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'FAIL',
                    'message': 'No security configuration found'
                }
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def run_all_tests(self):
        """Run all test tasks"""
        print(f"Starting Glue Hard Assessment for Student: {self.student_id}")
        print("=" * 60)
        
        self.test_task1_enterprise_datalake()
        self.test_task2_multi_database_architecture()
        self.test_task3_lake_formation()
        self.test_task4_custom_classifier()
        self.test_task5_schema_registry()
        self.test_task6_advanced_crawler()
        self.test_task7_databrew_project()
        self.test_task8_studio_visual_etl()
        self.test_task9_complex_workflow()
        self.test_task10_security_configuration()
        
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
            f.write(f"Glue Hard Assessment Results\n")
            f.write(f"{'=' * 60}\n")
            f.write(f"Student ID: {self.results['student_id']}\n")
            f.write(f"Score: {self.results['score']}/{self.results['total_tasks']} ({self.results['percentage']:.1f}%)\n\n")
            
            for task_name, task_result in self.results['tasks'].items():
                f.write(f"{task_name}\n")
                f.write(f"  Status: {task_result['status']}\n")
                f.write(f"  Message: {task_result['message']}\n\n")

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_glue_hard_assessment.py <student_id>")
        sys.exit(1)
    
    student_id = sys.argv[1]
    
    try:
        tester = GlueHardAssessmentTester(student_id)
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
