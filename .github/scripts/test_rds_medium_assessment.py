#!/usr/bin/env python3
"""
RDS Medium Assessment Test Script
Validates intermediate RDS configuration with Multi-AZ, read replicas, parameter groups
"""

import boto3
import sys
import json
from datetime import datetime

class RDSMediumAssessmentTester:
    def __init__(self, student_id):
        self.student_id = student_id
        self.rds_client = boto3.client('rds')
        self.ec2_client = boto3.client('ec2')
        self.results = {
            'student_id': student_id,
            'assessment': 'rds_medium',
            'timestamp': datetime.utcnow().isoformat(),
            'tasks': {},
            'score': 0,
            'total_tasks': 7
        }
        self.db_identifier = f"webapp-db-{student_id}"
        self.read_replica_identifier = f"webapp-db-{student_id}-replica"
        self.param_group_name = f"webapp-params-{student_id}"
        self.option_group_name = f"webapp-options-{student_id}"

    def test_task1_primary_instance(self):
        """Task 1: Verify primary RDS instance with Multi-AZ"""
        task_name = "Task 1: Create Primary RDS Instance"
        try:
            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=self.db_identifier
            )
            
            if not response['DBInstances']:
                self.results['tasks'][task_name] = {
                    'status': 'FAIL',
                    'message': f"Primary instance '{self.db_identifier}' not found"
                }
                return
            
            db_instance = response['DBInstances'][0]
            issues = []
            
            # Check engine and version
            if db_instance['Engine'] != 'mysql':
                issues.append(f"Expected engine 'mysql', found '{db_instance['Engine']}'")
            
            # Check instance class
            if db_instance['DBInstanceClass'] != 'db.t3.small':
                issues.append(f"Expected 'db.t3.small', found '{db_instance['DBInstanceClass']}'")
            
            # Check Multi-AZ
            if not db_instance.get('MultiAZ', False):
                issues.append("Multi-AZ is not enabled")
            
            # Check storage
            if db_instance['AllocatedStorage'] < 100:
                issues.append(f"Expected at least 100 GB, found {db_instance['AllocatedStorage']} GB")
            
            # Check storage type
            if db_instance.get('StorageType') != 'gp3':
                issues.append(f"Expected 'gp3' storage, found '{db_instance.get('StorageType')}'")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Instance exists but has issues: {'; '.join(issues)}",
                    'details': {
                        'multi_az': db_instance.get('MultiAZ'),
                        'instance_class': db_instance['DBInstanceClass'],
                        'storage': db_instance['AllocatedStorage']
                    }
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Primary instance configured correctly',
                    'details': {
                        'multi_az': db_instance['MultiAZ'],
                        'instance_class': db_instance['DBInstanceClass'],
                        'storage_type': db_instance['StorageType']
                    }
                }
                self.results['score'] += 1
                
        except self.rds_client.exceptions.DBInstanceNotFoundFault:
            self.results['tasks'][task_name] = {
                'status': 'FAIL',
                'message': f"Primary instance '{self.db_identifier}' not found"
            }
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task2_read_replica(self):
        """Task 2: Verify read replica exists"""
        task_name = "Task 2: Create Read Replica"
        try:
            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=self.read_replica_identifier
            )
            
            if not response['DBInstances']:
                self.results['tasks'][task_name] = {
                    'status': 'FAIL',
                    'message': f"Read replica '{self.read_replica_identifier}' not found"
                }
                return
            
            replica = response['DBInstances'][0]
            issues = []
            
            # Check if it's actually a read replica
            if not replica.get('ReadReplicaSourceDBInstanceIdentifier'):
                issues.append("Instance is not configured as a read replica")
            else:
                source = replica['ReadReplicaSourceDBInstanceIdentifier']
                if self.db_identifier not in source:
                    issues.append(f"Read replica source doesn't match primary instance")
            
            # Check instance class
            if replica['DBInstanceClass'] != 'db.t3.small':
                issues.append(f"Expected 'db.t3.small', found '{replica['DBInstanceClass']}'")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Read replica issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Read replica configured correctly',
                    'details': {
                        'replica_id': self.read_replica_identifier,
                        'source': replica.get('ReadReplicaSourceDBInstanceIdentifier')
                    }
                }
                self.results['score'] += 1
                
        except self.rds_client.exceptions.DBInstanceNotFoundFault:
            self.results['tasks'][task_name] = {
                'status': 'FAIL',
                'message': f"Read replica '{self.read_replica_identifier}' not found"
            }
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task3_parameter_group(self):
        """Task 3: Verify custom parameter group"""
        task_name = "Task 3: Create Custom Parameter Group"
        try:
            response = self.rds_client.describe_db_parameter_groups(
                DBParameterGroupName=self.param_group_name
            )
            
            if not response['DBParameterGroups']:
                self.results['tasks'][task_name] = {
                    'status': 'FAIL',
                    'message': f"Parameter group '{self.param_group_name}' not found"
                }
                return
            
            param_group = response['DBParameterGroups'][0]
            issues = []
            
            # Check if parameter group is attached to instance
            db_response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=self.db_identifier
            )
            db_instance = db_response['DBInstances'][0]
            
            attached_params = [pg['DBParameterGroupName'] for pg in db_instance['DBParameterGroups']]
            if self.param_group_name not in attached_params:
                issues.append("Parameter group not attached to primary instance")
            
            # Check specific parameters
            params_response = self.rds_client.describe_db_parameters(
                DBParameterGroupName=self.param_group_name
            )
            
            params = {p['ParameterName']: p.get('ParameterValue') 
                     for p in params_response['Parameters'] 
                     if 'ParameterValue' in p}
            
            expected_params = {
                'max_connections': '200',
                'slow_query_log': '1'
            }
            
            for param_name, expected_value in expected_params.items():
                if param_name not in params:
                    issues.append(f"Parameter '{param_name}' not set")
                elif params[param_name] != expected_value:
                    issues.append(f"Parameter '{param_name}' = '{params[param_name]}', expected '{expected_value}'")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Parameter group issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Parameter group configured correctly',
                    'details': {
                        'parameter_group': self.param_group_name,
                        'attached': True
                    }
                }
                self.results['score'] += 1
                
        except self.rds_client.exceptions.DBParameterGroupNotFoundFault:
            self.results['tasks'][task_name] = {
                'status': 'FAIL',
                'message': f"Parameter group '{self.param_group_name}' not found"
            }
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task4_option_group(self):
        """Task 4: Verify custom option group"""
        task_name = "Task 4: Create Custom Option Group"
        try:
            response = self.rds_client.describe_option_groups(
                OptionGroupName=self.option_group_name
            )
            
            if not response['OptionGroupsList']:
                self.results['tasks'][task_name] = {
                    'status': 'FAIL',
                    'message': f"Option group '{self.option_group_name}' not found"
                }
                return
            
            option_group = response['OptionGroupsList'][0]
            issues = []
            
            # Check if option group is attached
            db_response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=self.db_identifier
            )
            db_instance = db_response['DBInstances'][0]
            
            attached_options = [og['OptionGroupName'] for og in db_instance['OptionGroupMemberships']]
            if self.option_group_name not in attached_options:
                issues.append("Option group not attached to primary instance")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Option group issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Option group configured correctly',
                    'details': {
                        'option_group': self.option_group_name
                    }
                }
                self.results['score'] += 1
                
        except self.rds_client.exceptions.OptionGroupNotFoundFault:
            self.results['tasks'][task_name] = {
                'status': 'FAIL',
                'message': f"Option group '{self.option_group_name}' not found"
            }
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task5_automated_backups(self):
        """Task 5: Verify automated backup configuration"""
        task_name = "Task 5: Configure Automated Backups"
        try:
            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=self.db_identifier
            )
            
            db_instance = response['DBInstances'][0]
            issues = []
            
            # Check backup retention
            retention = db_instance.get('BackupRetentionPeriod', 0)
            if retention < 7:
                issues.append(f"Backup retention is {retention} days, expected at least 7")
            
            # Check backup window
            if not db_instance.get('PreferredBackupWindow'):
                issues.append("Backup window not configured")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Backup issues: {'; '.join(issues)}",
                    'details': {
                        'retention_period': retention
                    }
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Automated backups configured correctly',
                    'details': {
                        'retention_period': retention,
                        'backup_window': db_instance.get('PreferredBackupWindow')
                    }
                }
                self.results['score'] += 1
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task6_monitoring(self):
        """Task 6: Verify enhanced monitoring"""
        task_name = "Task 6: Enable Enhanced Monitoring"
        try:
            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=self.db_identifier
            )
            
            db_instance = response['DBInstances'][0]
            issues = []
            
            # Check enhanced monitoring
            if not db_instance.get('EnhancedMonitoringResourceArn'):
                issues.append("Enhanced monitoring not enabled")
            
            monitoring_interval = db_instance.get('MonitoringInterval', 0)
            if monitoring_interval == 0:
                issues.append("Monitoring interval not set")
            elif monitoring_interval > 60:
                issues.append(f"Monitoring interval is {monitoring_interval}s, should be <= 60s")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Monitoring issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Enhanced monitoring configured correctly',
                    'details': {
                        'monitoring_interval': monitoring_interval
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
        task_name = "Task 7: Add Resource Tags"
        try:
            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=self.db_identifier
            )
            
            db_instance = response['DBInstances'][0]
            arn = db_instance['DBInstanceArn']
            tags_response = self.rds_client.list_tags_for_resource(ResourceName=arn)
            
            tags = {tag['Key']: tag['Value'] for tag in tags_response.get('TagList', [])}
            issues = []
            
            required_tags = {
                'Environment': 'Production',
                'Application': 'WebApp',
                'Backup': 'Required',
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
        print(f"Starting RDS Medium Assessment for Student: {self.student_id}")
        print("=" * 60)
        
        self.test_task1_primary_instance()
        self.test_task2_read_replica()
        self.test_task3_parameter_group()
        self.test_task4_option_group()
        self.test_task5_automated_backups()
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
            f.write(f"RDS Medium Assessment Results\n")
            f.write(f"{'=' * 60}\n")
            f.write(f"Student ID: {self.results['student_id']}\n")
            f.write(f"Score: {self.results['score']}/{self.results['total_tasks']} ({self.results['percentage']:.1f}%)\n\n")
            
            for task_name, task_result in self.results['tasks'].items():
                f.write(f"{task_name}\n")
                f.write(f"  Status: {task_result['status']}\n")
                f.write(f"  Message: {task_result['message']}\n\n")

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_rds_medium_assessment.py <student_id>")
        sys.exit(1)
    
    student_id = sys.argv[1]
    
    try:
        tester = RDSMediumAssessmentTester(student_id)
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
