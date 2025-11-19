#!/usr/bin/env python3
"""
RDS Easy Assessment Test Script
Validates basic RDS instance configuration for student assessment
"""

import boto3
import sys
import json
from datetime import datetime

class RDSEasyAssessmentTester:
    def __init__(self, student_id):
        self.student_id = student_id
        self.rds_client = boto3.client('rds')
        self.ec2_client = boto3.client('ec2')
        self.results = {
            'student_id': student_id,
            'assessment': 'rds_easy',
            'timestamp': datetime.utcnow().isoformat(),
            'tasks': {},
            'score': 0,
            'total_tasks': 4
        }
        self.db_identifier = f"student-db-{student_id}"
        self.sg_name = f"student-db-sg-{student_id}"

    def test_task1_db_instance_exists(self):
        """Task 1: Verify RDS instance exists with correct configuration"""
        task_name = "Task 1: Create RDS Instance"
        try:
            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=self.db_identifier
            )
            
            if not response['DBInstances']:
                self.results['tasks'][task_name] = {
                    'status': 'FAIL',
                    'message': f"DB instance '{self.db_identifier}' not found"
                }
                return
            
            db_instance = response['DBInstances'][0]
            issues = []
            
            # Check engine
            if db_instance['Engine'] != 'mysql':
                issues.append(f"Expected engine 'mysql', found '{db_instance['Engine']}'")
            
            # Check instance class
            if db_instance['DBInstanceClass'] != 'db.t3.micro':
                issues.append(f"Expected instance class 'db.t3.micro', found '{db_instance['DBInstanceClass']}'")
            
            # Check database name
            if db_instance.get('DBName') != 'studentdb':
                issues.append(f"Expected database name 'studentdb', found '{db_instance.get('DBName')}'")
            
            # Check master username
            if db_instance['MasterUsername'] != 'admin':
                issues.append(f"Expected master username 'admin', found '{db_instance['MasterUsername']}'")
            
            # Check allocated storage
            if db_instance['AllocatedStorage'] < 20:
                issues.append(f"Expected at least 20 GB storage, found {db_instance['AllocatedStorage']} GB")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Instance exists but has issues: {'; '.join(issues)}",
                    'details': {
                        'engine': db_instance['Engine'],
                        'instance_class': db_instance['DBInstanceClass'],
                        'database': db_instance.get('DBName'),
                        'storage': db_instance['AllocatedStorage']
                    }
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'RDS instance configured correctly',
                    'details': {
                        'instance_id': self.db_identifier,
                        'engine': db_instance['Engine'],
                        'instance_class': db_instance['DBInstanceClass']
                    }
                }
                self.results['score'] += 1
                
        except self.rds_client.exceptions.DBInstanceNotFoundFault:
            self.results['tasks'][task_name] = {
                'status': 'FAIL',
                'message': f"DB instance '{self.db_identifier}' not found"
            }
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error checking instance: {str(e)}"
            }

    def test_task2_public_accessibility(self):
        """Task 2: Verify public accessibility is enabled"""
        task_name = "Task 2: Configure Public Accessibility"
        try:
            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=self.db_identifier
            )
            
            db_instance = response['DBInstances'][0]
            
            if db_instance.get('PubliclyAccessible', False):
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Public accessibility is enabled',
                    'details': {
                        'publicly_accessible': True,
                        'endpoint': db_instance.get('Endpoint', {}).get('Address', 'N/A')
                    }
                }
                self.results['score'] += 1
            else:
                self.results['tasks'][task_name] = {
                    'status': 'FAIL',
                    'message': 'Public accessibility is not enabled'
                }
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error checking public accessibility: {str(e)}"
            }

    def test_task3_security_group(self):
        """Task 3: Verify security group configuration"""
        task_name = "Task 3: Configure Security Group"
        try:
            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=self.db_identifier
            )
            
            db_instance = response['DBInstances'][0]
            vpc_security_groups = db_instance.get('VpcSecurityGroups', [])
            
            if not vpc_security_groups:
                self.results['tasks'][task_name] = {
                    'status': 'FAIL',
                    'message': 'No security group attached to instance'
                }
                return
            
            sg_id = vpc_security_groups[0]['VpcSecurityGroupId']
            
            # Check security group rules
            sg_response = self.ec2_client.describe_security_groups(
                GroupIds=[sg_id]
            )
            
            security_group = sg_response['SecurityGroups'][0]
            issues = []
            
            # Check if MySQL port (3306) is open
            mysql_rule_found = False
            for rule in security_group.get('IpPermissions', []):
                if rule.get('FromPort') == 3306 and rule.get('ToPort') == 3306:
                    mysql_rule_found = True
                    break
            
            if not mysql_rule_found:
                issues.append("MySQL port 3306 not open in security group")
            
            # Check tags
            sg_tags = {tag['Key']: tag['Value'] for tag in security_group.get('Tags', [])}
            if sg_tags.get('StudentID') != self.student_id:
                issues.append(f"Security group missing or incorrect StudentID tag")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Security group issues: {'; '.join(issues)}",
                    'details': {
                        'security_group_id': sg_id,
                        'group_name': security_group.get('GroupName')
                    }
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Security group configured correctly',
                    'details': {
                        'security_group_id': sg_id,
                        'group_name': security_group.get('GroupName')
                    }
                }
                self.results['score'] += 1
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error checking security group: {str(e)}"
            }

    def test_task4_tags(self):
        """Task 4: Verify instance tags"""
        task_name = "Task 4: Add Resource Tags"
        try:
            response = self.rds_client.describe_db_instances(
                DBInstanceIdentifier=self.db_identifier
            )
            
            db_instance = response['DBInstances'][0]
            
            # Get tags using list_tags_for_resource
            arn = db_instance['DBInstanceArn']
            tags_response = self.rds_client.list_tags_for_resource(ResourceName=arn)
            
            tags = {tag['Key']: tag['Value'] for tag in tags_response.get('TagList', [])}
            issues = []
            
            required_tags = {
                'Environment': 'Development',
                'Project': 'StudentDatabase',
                'StudentID': self.student_id
            }
            
            for key, expected_value in required_tags.items():
                if key not in tags:
                    issues.append(f"Missing tag: {key}")
                elif tags[key] != expected_value:
                    issues.append(f"Tag {key} has value '{tags[key]}', expected '{expected_value}'")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Tag issues: {'; '.join(issues)}",
                    'details': {
                        'current_tags': tags
                    }
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'All required tags present and correct',
                    'details': {
                        'tags': tags
                    }
                }
                self.results['score'] += 1
                
        except Exception as e:
            self.results['tasks'][task_name] = {
                'status': 'ERROR',
                'message': f"Error checking tags: {str(e)}"
            }

    def run_all_tests(self):
        """Run all test tasks"""
        print(f"Starting RDS Easy Assessment for Student: {self.student_id}")
        print("=" * 60)
        
        self.test_task1_db_instance_exists()
        self.test_task2_public_accessibility()
        self.test_task3_security_group()
        self.test_task4_tags()
        
        # Calculate percentage
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
            status_emoji = {
                'PASS': '✓',
                'FAIL': '✗',
                'PARTIAL': '~',
                'ERROR': '!'
            }.get(task_result['status'], '?')
            
            print(f"\n{status_emoji} {task_name}")
            print(f"  Status: {task_result['status']}")
            print(f"  {task_result['message']}")
            
            if 'details' in task_result:
                print(f"  Details: {json.dumps(task_result['details'], indent=2)}")

    def save_results(self, filename='test_report.log'):
        """Save results to file"""
        with open(filename, 'w') as f:
            f.write(f"RDS Easy Assessment Results\n")
            f.write(f"{'=' * 60}\n")
            f.write(f"Student ID: {self.results['student_id']}\n")
            f.write(f"Assessment: {self.results['assessment']}\n")
            f.write(f"Timestamp: {self.results['timestamp']}\n")
            f.write(f"Score: {self.results['score']}/{self.results['total_tasks']} ({self.results['percentage']:.1f}%)\n")
            f.write(f"\nTask Results:\n")
            f.write(f"{'-' * 60}\n")
            
            for task_name, task_result in self.results['tasks'].items():
                f.write(f"\n{task_name}\n")
                f.write(f"  Status: {task_result['status']}\n")
                f.write(f"  Message: {task_result['message']}\n")
                if 'details' in task_result:
                    f.write(f"  Details: {json.dumps(task_result['details'], indent=2)}\n")

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_rds_easy_assessment.py <student_id>")
        sys.exit(1)
    
    student_id = sys.argv[1]
    
    try:
        tester = RDSEasyAssessmentTester(student_id)
        tester.run_all_tests()
        tester.print_results()
        tester.save_results()
        
        # Exit with appropriate code
        if tester.results['percentage'] >= 70:
            print("\n✓ Assessment PASSED!")
            sys.exit(0)
        else:
            print("\n✗ Assessment FAILED. Please review the results and try again.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n✗ Assessment ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
