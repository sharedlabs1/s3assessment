#!/usr/bin/env python3
"""
Redshift Hard Assessment Test Script
Validates enterprise Redshift configuration with DR, Spectrum, data sharing, advanced security
"""

import boto3
import sys
import json
from datetime import datetime

class RedshiftHardAssessmentTester:
    def __init__(self, student_id):
        self.student_id = student_id
        self.redshift_client = boto3.client('redshift')
        self.kms_client = boto3.client('kms')
        self.iam_client = boto3.client('iam')
        self.s3_client = boto3.client('s3')
        self.cloudwatch_client = boto3.client('cloudwatch')
        self.results = {
            'student_id': student_id,
            'assessment': 'redshift_hard',
            'timestamp': datetime.utcnow().isoformat(),
            'tasks': {},
            'score': 0,
            'total_tasks': 10
        }
        self.primary_cluster_id = f"dwh-primary-{student_id}"
        self.dr_cluster_id = f"dwh-dr-{student_id}"
        self.param_group_name = f"enterprise-params-{student_id}"
        self.spectrum_role = f"RedshiftSpectrumRole-{student_id}"

    def test_task1_multi_cluster_architecture(self):
        """Task 1: Verify primary and DR clusters"""
        task_name = "Task 1: Create Multi-Cluster Architecture"
        try:
            issues = []
            
            # Check primary cluster
            try:
                primary_response = self.redshift_client.describe_clusters(
                    ClusterIdentifier=self.primary_cluster_id
                )
                primary = primary_response['Clusters'][0]
                
                # Verify primary cluster specs
                if not primary['NodeType'].startswith('ra3.4xlarge'):
                    issues.append(f"Primary: Expected ra3.4xlarge, found '{primary['NodeType']}'")
                
                if primary['NumberOfNodes'] < 6:
                    issues.append(f"Primary: Expected 6+ nodes, found {primary['NumberOfNodes']}")
                
                if not primary.get('Encrypted', False):
                    issues.append("Primary: Encryption not enabled")
                
                if not primary.get('EnhancedVpcRouting', False):
                    issues.append("Primary: Enhanced VPC routing not enabled")
                
                retention = primary.get('AutomatedSnapshotRetentionPeriod', 0)
                if retention < 35:
                    issues.append(f"Primary: Snapshot retention {retention} days, expected 35")
                    
            except self.redshift_client.exceptions.ClusterNotFoundFault:
                issues.append(f"Primary cluster '{self.primary_cluster_id}' not found")
            
            # Check DR cluster (optional - may be in different region)
            dr_exists = False
            try:
                dr_response = self.redshift_client.describe_clusters(
                    ClusterIdentifier=self.dr_cluster_id
                )
                dr_exists = True
            except self.redshift_client.exceptions.ClusterNotFoundFault:
                issues.append(f"DR cluster '{self.dr_cluster_id}' not found (may be in different region)")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Cluster issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Multi-cluster architecture configured correctly',
                    'details': {
                        'primary_cluster': self.primary_cluster_id,
                        'dr_cluster_exists': dr_exists
                    }
                }
                self.results['score'] += 1
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task2_parameter_group(self):
        """Task 2: Verify advanced parameter group"""
        task_name = "Task 2: Advanced Parameter Group Configuration"
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
            
            # Check if attached to cluster
            cluster_response = self.redshift_client.describe_clusters(
                ClusterIdentifier=self.primary_cluster_id
            )
            cluster = cluster_response['Clusters'][0]
            
            param_groups = [pg['ParameterGroupName'] for pg in cluster.get('ClusterParameterGroups', [])]
            
            if self.param_group_name in param_groups:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Enterprise parameter group configured',
                    'details': {
                        'parameter_group': self.param_group_name
                    }
                }
                self.results['score'] += 1
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': 'Parameter group exists but not attached'
                }
                self.results['score'] += 0.5
                
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

    def test_task3_database_design(self):
        """Task 3: Verify database design (basic check)"""
        task_name = "Task 3: Enterprise Database Design with Advanced Optimization"
        try:
            response = self.redshift_client.describe_clusters(
                ClusterIdentifier=self.primary_cluster_id
            )
            
            cluster = response['Clusters'][0]
            
            if cluster.get('DBName') == 'enterprise_dwh':
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Enterprise database exists (schema verification required)',
                    'details': {
                        'database': cluster['DBName'],
                        'note': 'Table structure, distribution keys, and sort keys should be verified with SQL queries'
                    }
                }
                self.results['score'] += 1
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Database name is '{cluster.get('DBName')}', expected 'enterprise_dwh'"
                }
                self.results['score'] += 0.5
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task4_spectrum_configuration(self):
        """Task 4: Verify Redshift Spectrum IAM role"""
        task_name = "Task 4: Configure Redshift Spectrum for Data Lake Integration"
        try:
            issues = []
            
            # Check IAM role exists
            try:
                role_response = self.iam_client.get_role(RoleName=self.spectrum_role)
                role_arn = role_response['Role']['Arn']
                
                # Check if role is attached to cluster
                cluster_response = self.redshift_client.describe_clusters(
                    ClusterIdentifier=self.primary_cluster_id
                )
                cluster = cluster_response['Clusters'][0]
                
                attached_roles = [role['IamRoleArn'] for role in cluster.get('IamRoles', [])]
                if role_arn not in attached_roles:
                    issues.append("Spectrum IAM role not attached to cluster")
                    
            except self.iam_client.exceptions.NoSuchEntityException:
                issues.append(f"IAM role '{self.spectrum_role}' not found")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Spectrum issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Redshift Spectrum role configured',
                    'details': {
                        'iam_role': self.spectrum_role,
                        'note': 'External schema and tables should be verified with SQL queries'
                    }
                }
                self.results['score'] += 1
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task5_data_sharing(self):
        """Task 5: Verify data sharing configuration (basic check)"""
        task_name = "Task 5: Configure Data Sharing (Producer/Consumer)"
        try:
            # Data sharing verification requires query access
            # This is a placeholder check
            response = self.redshift_client.describe_clusters(
                ClusterIdentifier=self.primary_cluster_id
            )
            
            if response['Clusters']:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Cluster ready for data sharing (manual verification required)',
                    'details': {
                        'note': 'Datashare creation and grants should be verified with SQL queries'
                    }
                }
                self.results['score'] += 1
            else:
                self.results['tasks'][task_name] = {
                    'status': 'FAIL',
                    'message': 'Primary cluster not available'
                }
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task6_advanced_security(self):
        """Task 6: Verify advanced security configuration"""
        task_name = "Task 6: Implement Advanced Security"
        try:
            response = self.redshift_client.describe_clusters(
                ClusterIdentifier=self.primary_cluster_id
            )
            
            cluster = response['Clusters'][0]
            issues = []
            
            # Check encryption with customer-managed KMS key
            if not cluster.get('Encrypted', False):
                issues.append("Cluster encryption not enabled")
            elif not cluster.get('KmsKeyId'):
                issues.append("Customer-managed KMS key not configured")
            
            # Check VPC configuration
            if not cluster.get('VpcId'):
                issues.append("Cluster not in VPC")
            
            # Check audit logging
            logging_status = self.redshift_client.describe_logging_status(
                ClusterIdentifier=self.primary_cluster_id
            )
            if not logging_status.get('LoggingEnabled', False):
                issues.append("Audit logging not enabled")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Security issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Advanced security configured correctly',
                    'details': {
                        'encrypted': True,
                        'vpc_configured': True,
                        'logging_enabled': True
                    }
                }
                self.results['score'] += 1
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task7_automated_maintenance(self):
        """Task 7: Verify automated maintenance and monitoring"""
        task_name = "Task 7: Configure Automated Maintenance and Monitoring"
        try:
            issues = []
            
            # Check CloudWatch alarms
            try:
                alarms_response = self.cloudwatch_client.describe_alarms(
                    AlarmNamePrefix=f"{self.primary_cluster_id}"
                )
                
                if len(alarms_response['MetricAlarms']) < 4:
                    issues.append(f"Expected at least 4 CloudWatch alarms, found {len(alarms_response['MetricAlarms'])}")
            except:
                issues.append("Could not verify CloudWatch alarms")
            
            # Check logging
            logging_status = self.redshift_client.describe_logging_status(
                ClusterIdentifier=self.primary_cluster_id
            )
            if not logging_status.get('LoggingEnabled', False):
                issues.append("Logging not enabled")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Monitoring issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Automated maintenance and monitoring configured',
                    'details': {
                        'note': 'Stored procedures should be verified with SQL queries'
                    }
                }
                self.results['score'] += 1
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task8_query_optimization(self):
        """Task 8: Verify query optimization (basic check)"""
        task_name = "Task 8: Query Optimization and Performance Tuning"
        try:
            response = self.redshift_client.describe_clusters(
                ClusterIdentifier=self.primary_cluster_id
            )
            
            cluster = response['Clusters'][0]
            
            # Check if custom parameter group is attached (for QMR)
            param_groups = [pg['ParameterGroupName'] for pg in cluster.get('ClusterParameterGroups', [])]
            
            if self.param_group_name in param_groups:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Query optimization ready (QMR and materialized views require SQL verification)',
                    'details': {
                        'note': 'Query monitoring rules and materialized views should be verified with SQL queries'
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

    def test_task9_disaster_recovery(self):
        """Task 9: Verify DR configuration"""
        task_name = "Task 9: Disaster Recovery Testing"
        try:
            # Check for manual snapshots
            snapshots_response = self.redshift_client.describe_cluster_snapshots(
                ClusterIdentifier=self.primary_cluster_id,
                SnapshotType='manual'
            )
            
            issues = []
            
            if len(snapshots_response['Snapshots']) == 0:
                issues.append("No manual snapshots found")
            
            # Check automated snapshot schedule
            response = self.redshift_client.describe_clusters(
                ClusterIdentifier=self.primary_cluster_id
            )
            cluster = response['Clusters'][0]
            
            retention = cluster.get('AutomatedSnapshotRetentionPeriod', 0)
            if retention < 35:
                issues.append(f"Snapshot retention {retention} days, expected 35")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"DR issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'DR configuration verified',
                    'details': {
                        'manual_snapshots': len(snapshots_response['Snapshots']),
                        'retention_days': retention
                    }
                }
                self.results['score'] += 1
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task10_cost_optimization(self):
        """Task 10: Verify cost optimization settings"""
        task_name = "Task 10: Cost Optimization"
        try:
            response = self.redshift_client.describe_clusters(
                ClusterIdentifier=self.primary_cluster_id
            )
            
            cluster = response['Clusters'][0]
            issues = []
            
            # Check if using RA3 nodes (supports independent compute/storage scaling)
            if not cluster['NodeType'].startswith('ra3'):
                issues.append("Not using RA3 nodes for cost optimization")
            
            # Check tags for cost allocation
            tags = {tag['Key']: tag['Value'] for tag in cluster.get('Tags', [])}
            required_cost_tags = ['Environment', 'Project', 'StudentID']
            
            for tag in required_cost_tags:
                if tag not in tags:
                    issues.append(f"Missing cost allocation tag: {tag}")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Cost optimization issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Cost optimization configured',
                    'details': {
                        'node_type': cluster['NodeType'],
                        'tags': tags
                    }
                }
                self.results['score'] += 1
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def run_all_tests(self):
        """Run all test tasks"""
        print(f"Starting Redshift Hard Assessment for Student: {self.student_id}")
        print("=" * 60)
        
        self.test_task1_multi_cluster_architecture()
        self.test_task2_parameter_group()
        self.test_task3_database_design()
        self.test_task4_spectrum_configuration()
        self.test_task5_data_sharing()
        self.test_task6_advanced_security()
        self.test_task7_automated_maintenance()
        self.test_task8_query_optimization()
        self.test_task9_disaster_recovery()
        self.test_task10_cost_optimization()
        
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
            f.write(f"Redshift Hard Assessment Results\n")
            f.write(f"{'=' * 60}\n")
            f.write(f"Student ID: {self.results['student_id']}\n")
            f.write(f"Score: {self.results['score']}/{self.results['total_tasks']} ({self.results['percentage']:.1f}%)\n\n")
            
            for task_name, task_result in self.results['tasks'].items():
                f.write(f"{task_name}\n")
                f.write(f"  Status: {task_result['status']}\n")
                f.write(f"  Message: {task_result['message']}\n\n")

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_redshift_hard_assessment.py <student_id>")
        sys.exit(1)
    
    student_id = sys.argv[1]
    
    try:
        tester = RedshiftHardAssessmentTester(student_id)
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
