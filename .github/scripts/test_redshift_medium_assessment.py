#!/usr/bin/env python3
"""
Redshift Medium Assessment Test Script
Validates intermediate Redshift configuration with parameter groups, WLM, S3 integration
"""

import boto3
import sys
import json
from datetime import datetime

class RedshiftMediumAssessmentTester:
    def __init__(self, student_id):
        self.student_id = student_id
        self.redshift_client = boto3.client('redshift')
        self.s3_client = boto3.client('s3')
        self.iam_client = boto3.client('iam')
        self.cloudwatch_client = boto3.client('cloudwatch')
        self.results = {
            'student_id': student_id,
            'assessment': 'redshift_medium',
            'timestamp': datetime.utcnow().isoformat(),
            'tasks': {},
            'score': 0,
            'total_tasks': 7
        }
        self.cluster_id = f"dwh-cluster-{student_id}"
        self.param_group_name = f"dwh-params-{student_id}"
        self.s3_bucket = f"redshift-data-{student_id}"
        self.iam_role_name = f"RedshiftS3Access-{student_id}"

    def test_task1_production_cluster(self):
        """Task 1: Verify production Redshift cluster"""
        task_name = "Task 1: Create Production Redshift Cluster"
        try:
            response = self.redshift_client.describe_clusters(
                ClusterIdentifier=self.cluster_id
            )
            
            if not response['Clusters']:
                self.results['tasks'][task_name] = {
                    'status': 'FAIL',
                    'message': f"Cluster '{self.cluster_id}' not found"
                }
                return
            
            cluster = response['Clusters'][0]
            issues = []
            
            # Check node type
            if not cluster['NodeType'].startswith('ra3'):
                issues.append(f"Expected ra3 node type, found '{cluster['NodeType']}'")
            
            # Check number of nodes
            if cluster['NumberOfNodes'] < 4:
                issues.append(f"Expected at least 4 nodes, found {cluster['NumberOfNodes']}")
            
            # Check encryption
            if not cluster.get('Encrypted', False):
                issues.append("Cluster encryption not enabled")
            
            # Check enhanced VPC routing
            if not cluster.get('EnhancedVpcRouting', False):
                issues.append("Enhanced VPC routing not enabled")
            
            # Check automated snapshots
            retention = cluster.get('AutomatedSnapshotRetentionPeriod', 0)
            if retention < 14:
                issues.append(f"Snapshot retention is {retention} days, expected 14")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Cluster issues: {'; '.join(issues)}",
                    'details': {
                        'node_type': cluster['NodeType'],
                        'num_nodes': cluster['NumberOfNodes'],
                        'encrypted': cluster.get('Encrypted')
                    }
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Production cluster configured correctly',
                    'details': {
                        'cluster_id': self.cluster_id,
                        'node_type': cluster['NodeType'],
                        'num_nodes': cluster['NumberOfNodes'],
                        'encrypted': cluster['Encrypted']
                    }
                }
                self.results['score'] += 1
                
        except self.redshift_client.exceptions.ClusterNotFoundFault:
            self.results['tasks'][task_name] = {
                'status': 'FAIL',
                'message': f"Cluster '{self.cluster_id}' not found"
            }
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task2_parameter_group(self):
        """Task 2: Verify custom parameter group"""
        task_name = "Task 2: Configure Parameter Group"
        try:
            response = self.redshift_client.describe_cluster_parameter_groups(
                ParameterGroupName=self.param_group_name
            )
            
            if not response['ParameterGroups']:
                self.results['tasks'][task_name] = {
                    'status': 'FAIL',
                    'message': f"Parameter group '{self.param_group_name}' not found"
                }
                return
            
            # Check if parameter group is attached to cluster
            cluster_response = self.redshift_client.describe_clusters(
                ClusterIdentifier=self.cluster_id
            )
            cluster = cluster_response['Clusters'][0]
            
            param_groups = [pg['ParameterGroupName'] for pg in cluster.get('ClusterParameterGroups', [])]
            
            if self.param_group_name not in param_groups:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Parameter group exists but not attached to cluster"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Parameter group configured and attached',
                    'details': {
                        'parameter_group': self.param_group_name
                    }
                }
                self.results['score'] += 1
                
        except self.redshift_client.exceptions.ClusterParameterGroupNotFoundFault:
            self.results['tasks'][task_name] = {
                'status': 'FAIL',
                'message': f"Parameter group '{self.param_group_name}' not found"
            }
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task3_database_schema(self):
        """Task 3: Verify database schema exists (basic check)"""
        task_name = "Task 3: Design Database Schema with Optimization"
        # Note: This is a simplified check as we cannot directly query the database
        # In production, this would connect to the cluster and verify table structure
        try:
            response = self.redshift_client.describe_clusters(
                ClusterIdentifier=self.cluster_id
            )
            
            cluster = response['Clusters'][0]
            
            if cluster.get('DBName') == 'datawarehouse':
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Database exists (manual schema verification required)',
                    'details': {
                        'database': cluster['DBName'],
                        'note': 'Schema structure should be verified manually with SQL queries'
                    }
                }
                self.results['score'] += 1
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Database name is '{cluster.get('DBName')}', expected 'datawarehouse'"
                }
                self.results['score'] += 0.5
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task4_s3_integration(self):
        """Task 4: Verify S3 bucket and IAM role"""
        task_name = "Task 4: Configure S3 Data Loading"
        try:
            issues = []
            
            # Check S3 bucket exists
            try:
                self.s3_client.head_bucket(Bucket=self.s3_bucket)
            except:
                issues.append(f"S3 bucket '{self.s3_bucket}' not found")
            
            # Check IAM role exists
            try:
                role_response = self.iam_client.get_role(RoleName=self.iam_role_name)
                role_arn = role_response['Role']['Arn']
                
                # Check if role is attached to cluster
                cluster_response = self.redshift_client.describe_clusters(
                    ClusterIdentifier=self.cluster_id
                )
                cluster = cluster_response['Clusters'][0]
                
                attached_roles = [role['IamRoleArn'] for role in cluster.get('IamRoles', [])]
                if role_arn not in attached_roles:
                    issues.append("IAM role not attached to cluster")
                    
            except self.iam_client.exceptions.NoSuchEntityException:
                issues.append(f"IAM role '{self.iam_role_name}' not found")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"S3 integration issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'S3 integration configured correctly',
                    'details': {
                        's3_bucket': self.s3_bucket,
                        'iam_role': self.iam_role_name
                    }
                }
                self.results['score'] += 1
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task5_wlm_configuration(self):
        """Task 5: Verify WLM configuration (basic check)"""
        task_name = "Task 5: Configure Workload Management (WLM)"
        try:
            response = self.redshift_client.describe_clusters(
                ClusterIdentifier=self.cluster_id
            )
            
            cluster = response['Clusters'][0]
            
            # Check if custom parameter group is attached (which should contain WLM config)
            param_groups = [pg['ParameterGroupName'] for pg in cluster.get('ClusterParameterGroups', [])]
            
            if self.param_group_name in param_groups:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'WLM configuration in parameter group (manual verification recommended)',
                    'details': {
                        'note': 'WLM queues should be verified in parameter group settings'
                    }
                }
                self.results['score'] += 1
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': 'Custom parameter group not attached'
                }
                self.results['score'] += 0.5
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task6_monitoring(self):
        """Task 6: Verify monitoring configuration"""
        task_name = "Task 6: Configure Monitoring and Maintenance"
        try:
            response = self.redshift_client.describe_clusters(
                ClusterIdentifier=self.cluster_id
            )
            
            cluster = response['Clusters'][0]
            issues = []
            
            # Check logging enabled
            logging_status = self.redshift_client.describe_logging_status(
                ClusterIdentifier=self.cluster_id
            )
            
            if not logging_status.get('LoggingEnabled', False):
                issues.append("Audit logging not enabled")
            
            # Check if CloudWatch alarms exist for this cluster
            try:
                alarms_response = self.cloudwatch_client.describe_alarms(
                    AlarmNamePrefix=f"{self.cluster_id}"
                )
                
                if len(alarms_response['MetricAlarms']) < 2:
                    issues.append(f"Expected multiple CloudWatch alarms, found {len(alarms_response['MetricAlarms'])}")
            except:
                issues.append("Could not verify CloudWatch alarms")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Monitoring issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Monitoring configured correctly',
                    'details': {
                        'logging_enabled': True
                    }
                }
                self.results['score'] += 1
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task7_tags(self):
        """Task 7: Verify resource tags"""
        task_name = "Task 7: Configure Security"
        try:
            response = self.redshift_client.describe_clusters(
                ClusterIdentifier=self.cluster_id
            )
            
            cluster = response['Clusters'][0]
            tags = {tag['Key']: tag['Value'] for tag in cluster.get('Tags', [])}
            issues = []
            
            required_tags = {
                'Environment': 'Production',
                'Project': 'DataWarehouse',
                'CostCenter': 'Analytics',
                'StudentID': self.student_id
            }
            
            for key, expected_value in required_tags.items():
                if key not in tags:
                    issues.append(f"Missing tag: {key}")
                elif tags[key] != expected_value:
                    issues.append(f"Tag {key} = '{tags[key]}', expected '{expected_value}'")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Tag issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'All required tags present',
                    'details': {'tags': tags}
                }
                self.results['score'] += 1
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def run_all_tests(self):
        """Run all test tasks"""
        print(f"Starting Redshift Medium Assessment for Student: {self.student_id}")
        print("=" * 60)
        
        self.test_task1_production_cluster()
        self.test_task2_parameter_group()
        self.test_task3_database_schema()
        self.test_task4_s3_integration()
        self.test_task5_wlm_configuration()
        self.test_task6_monitoring()
        self.test_task7_tags()
        
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
            f.write(f"Redshift Medium Assessment Results\n")
            f.write(f"{'=' * 60}\n")
            f.write(f"Student ID: {self.results['student_id']}\n")
            f.write(f"Score: {self.results['score']}/{self.results['total_tasks']} ({self.results['percentage']:.1f}%)\n\n")
            
            for task_name, task_result in self.results['tasks'].items():
                f.write(f"{task_name}\n")
                f.write(f"  Status: {task_result['status']}\n")
                f.write(f"  Message: {task_result['message']}\n\n")

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_redshift_medium_assessment.py <student_id>")
        sys.exit(1)
    
    student_id = sys.argv[1]
    
    try:
        tester = RedshiftMediumAssessmentTester(student_id)
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
