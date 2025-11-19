#!/usr/bin/env python3
"""
RDS Hard Assessment Test Script
Validates advanced RDS configuration with encryption, IAM auth, performance insights
"""

import boto3
import sys
import json
from datetime import datetime

class RDSHardAssessmentTester:
    def __init__(self, student_id):
        self.student_id = student_id
        self.rds_client = boto3.client('rds')
        self.ec2_client = boto3.client('ec2')
        self.kms_client = boto3.client('kms')
        self.results = {
            'student_id': student_id,
            'assessment': 'rds_hard',
            'timestamp': datetime.utcnow().isoformat(),
            'tasks': {},
            'score': 0,
            'total_tasks': 8
        }
        self.db_identifier = f"secure-db-{student_id}"

    def test_task1_encrypted_instance(self):
        """Task 1: Verify encrypted RDS instance"""
        task_name = "Task 1: Create Encrypted RDS Instance"
        try:
            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=self.db_identifier
            )
            
            if not response['DBInstances']:
                self.results['tasks'][task_name] = {
                    'status': 'FAIL',
                    'message': f"Instance '{self.db_identifier}' not found"
                }
                return
            
            db_instance = response['DBInstances'][0]
            issues = []
            
            # Check encryption
            if not db_instance.get('StorageEncrypted', False):
                issues.append("Storage encryption not enabled")
            
            # Check KMS key
            if not db_instance.get('KmsKeyId'):
                issues.append("KMS key not configured")
            
            # Check instance class
            if not db_instance['DBInstanceClass'].startswith('db.m'):
                issues.append(f"Expected db.m class, found '{db_instance['DBInstanceClass']}'")
            
            # Check Multi-AZ
            if not db_instance.get('MultiAZ', False):
                issues.append("Multi-AZ not enabled")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Instance issues: {'; '.join(issues)}",
                    'details': {
                        'encrypted': db_instance.get('StorageEncrypted'),
                        'multi_az': db_instance.get('MultiAZ')
                    }
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Encrypted instance configured correctly',
                    'details': {
                        'instance_id': self.db_identifier,
                        'encrypted': True,
                        'kms_key': db_instance.get('KmsKeyId')
                    }
                }
                self.results['score'] += 1
                
        except self.rds_client.exceptions.DBInstanceNotFoundFault:
            self.results['tasks'][task_name] = {
                'status': 'FAIL',
                'message': f"Instance '{self.db_identifier}' not found"
            }
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task2_iam_authentication(self):
        """Task 2: Verify IAM database authentication"""
        task_name = "Task 2: Enable IAM Database Authentication"
        try:
            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=self.db_identifier
            )
            
            db_instance = response['DBInstances'][0]
            
            if db_instance.get('IAMDatabaseAuthenticationEnabled', False):
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'IAM database authentication enabled',
                    'details': {
                        'iam_auth_enabled': True
                    }
                }
                self.results['score'] += 1
            else:
                self.results['tasks'][task_name] = {
                    'status': 'FAIL',
                    'message': 'IAM database authentication not enabled'
                }
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task3_performance_insights(self):
        """Task 3: Verify Performance Insights"""
        task_name = "Task 3: Enable Performance Insights"
        try:
            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=self.db_identifier
            )
            
            db_instance = response['DBInstances'][0]
            issues = []
            
            # Check Performance Insights
            if not db_instance.get('PerformanceInsightsEnabled', False):
                issues.append("Performance Insights not enabled")
            
            # Check retention period
            retention = db_instance.get('PerformanceInsightsRetentionPeriod', 0)
            if retention < 7:
                issues.append(f"Performance Insights retention is {retention} days, expected >= 7")
            
            # Check KMS encryption for PI
            if db_instance.get('PerformanceInsightsEnabled') and not db_instance.get('PerformanceInsightsKMSKeyId'):
                issues.append("Performance Insights KMS key not configured")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Performance Insights issues: {'; '.join(issues)}"
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Performance Insights configured correctly',
                    'details': {
                        'enabled': True,
                        'retention': retention
                    }
                }
                self.results['score'] += 1
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task4_automated_backups(self):
        """Task 4: Verify automated backup configuration"""
        task_name = "Task 4: Configure Automated Backups"
        try:
            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=self.db_identifier
            )
            
            db_instance = response['DBInstances'][0]
            issues = []
            
            # Check backup retention (30 days)
            retention = db_instance.get('BackupRetentionPeriod', 0)
            if retention < 30:
                issues.append(f"Backup retention is {retention} days, expected 30")
            
            # Check backup window
            backup_window = db_instance.get('PreferredBackupWindow')
            if not backup_window or '03:00-04:00' not in backup_window:
                issues.append(f"Backup window not set to 03:00-04:00 UTC")
            
            # Check backup encryption
            if not db_instance.get('StorageEncrypted'):
                issues.append("Backups not encrypted (storage encryption disabled)")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Backup issues: {'; '.join(issues)}",
                    'details': {
                        'retention': retention,
                        'backup_window': backup_window
                    }
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Automated backups configured correctly',
                    'details': {
                        'retention': retention,
                        'backup_window': backup_window
                    }
                }
                self.results['score'] += 1
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task5_maintenance_window(self):
        """Task 5: Verify maintenance window configuration"""
        task_name = "Task 5: Configure Maintenance Window"
        try:
            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=self.db_identifier
            )
            
            db_instance = response['DBInstances'][0]
            issues = []
            
            # Check maintenance window
            maint_window = db_instance.get('PreferredMaintenanceWindow')
            if not maint_window or 'sun:04:00-sun:05:00' not in maint_window.lower():
                issues.append(f"Maintenance window not set to Sun:04:00-Sun:05:00")
            
            # Check auto minor version upgrade
            if db_instance.get('AutoMinorVersionUpgrade', False):
                issues.append("Auto minor version upgrade should be disabled for production")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Maintenance issues: {'; '.join(issues)}",
                    'details': {
                        'maintenance_window': maint_window
                    }
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Maintenance window configured correctly',
                    'details': {
                        'maintenance_window': maint_window,
                        'auto_minor_upgrade': db_instance.get('AutoMinorVersionUpgrade')
                    }
                }
                self.results['score'] += 1
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task6_deletion_protection(self):
        """Task 6: Verify deletion protection"""
        task_name = "Task 6: Enable Deletion Protection"
        try:
            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=self.db_identifier
            )
            
            db_instance = response['DBInstances'][0]
            
            if db_instance.get('DeletionProtection', False):
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Deletion protection enabled',
                    'details': {
                        'deletion_protection': True
                    }
                }
                self.results['score'] += 1
            else:
                self.results['tasks'][task_name] = {
                    'status': 'FAIL',
                    'message': 'Deletion protection not enabled'
                }
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task7_cloudwatch_logs(self):
        """Task 7: Verify CloudWatch Logs export"""
        task_name = "Task 7: Enable CloudWatch Logs Export"
        try:
            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=self.db_identifier
            )
            
            db_instance = response['DBInstances'][0]
            issues = []
            
            # Check enabled log types
            enabled_logs = db_instance.get('EnabledCloudwatchLogsExports', [])
            required_logs = ['error', 'general', 'slowquery']
            
            for log_type in required_logs:
                if log_type not in enabled_logs:
                    issues.append(f"CloudWatch log '{log_type}' not enabled")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Log export issues: {'; '.join(issues)}",
                    'details': {
                        'enabled_logs': enabled_logs
                    }
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'CloudWatch Logs export configured correctly',
                    'details': {
                        'enabled_logs': enabled_logs
                    }
                }
                self.results['score'] += 1
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error: {str(e)}"
            }

    def test_task8_tags(self):
        """Task 8: Verify comprehensive resource tags"""
        task_name = "Task 8: Add Comprehensive Tags"
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
                'Application': 'FinanceApp',
                'DataClassification': 'Confidential',
                'Compliance': 'PCI-DSS',
                'BackupRequired': 'Yes',
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
        print(f"Starting RDS Hard Assessment for Student: {self.student_id}")
        print("=" * 60)
        
        self.test_task1_encrypted_instance()
        self.test_task2_iam_authentication()
        self.test_task3_performance_insights()
        self.test_task4_automated_backups()
        self.test_task5_maintenance_window()
        self.test_task6_deletion_protection()
        self.test_task7_cloudwatch_logs()
        self.test_task8_tags()
        
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
            f.write(f"RDS Hard Assessment Results\n")
            f.write(f"{'=' * 60}\n")
            f.write(f"Student ID: {self.results['student_id']}\n")
            f.write(f"Score: {self.results['score']}/{self.results['total_tasks']} ({self.results['percentage']:.1f}%)\n\n")
            
            for task_name, task_result in self.results['tasks'].items():
                f.write(f"{task_name}\n")
                f.write(f"  Status: {task_result['status']}\n")
                f.write(f"  Message: {task_result['message']}\n\n")

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_rds_hard_assessment.py <student_id>")
        sys.exit(1)
    
    student_id = sys.argv[1]
    
    try:
        tester = RDSHardAssessmentTester(student_id)
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
