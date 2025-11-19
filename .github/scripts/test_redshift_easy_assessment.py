#!/usr/bin/env python3
"""
Redshift Easy Assessment Test Script
Validates basic Redshift cluster configuration for student assessment
"""

import boto3
import sys
import json
from datetime import datetime

class RedshiftEasyAssessmentTester:
    def __init__(self, student_id):
        self.student_id = student_id
        self.redshift_client = boto3.client('redshift')
        self.ec2_client = boto3.client('ec2')
        self.results = {
            'student_id': student_id,
            'assessment': 'redshift_easy',
            'timestamp': datetime.utcnow().isoformat(),
            'tasks': {},
            'score': 0,
            'total_tasks': 4
        }
        self.cluster_id = f"analytics-cluster-{student_id}"
        self.sg_name = f"redshift-sg-{student_id}"

    def test_task1_cluster_exists(self):
        """Task 1: Verify Redshift cluster exists with correct configuration"""
        task_name = "Task 1: Create Redshift Cluster"
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
            if cluster['NodeType'] != 'dc2.large':
                issues.append(f"Expected node type 'dc2.large', found '{cluster['NodeType']}'")
            
            # Check number of nodes
            if cluster['NumberOfNodes'] != 2:
                issues.append(f"Expected 2 nodes, found {cluster['NumberOfNodes']}")
            
            # Check database name
            if cluster['DBName'] != 'analyticsdb':
                issues.append(f"Expected database 'analyticsdb', found '{cluster['DBName']}'")
            
            # Check master username
            if cluster['MasterUsername'] != 'awsuser':
                issues.append(f"Expected master username 'awsuser', found '{cluster['MasterUsername']}'")
            
            if issues:
                self.results['tasks'][task_name] = {
                    'status': 'PARTIAL',
                    'message': f"Cluster exists but has issues: {'; '.join(issues)}",
                    'details': {
                        'node_type': cluster['NodeType'],
                        'num_nodes': cluster['NumberOfNodes'],
                        'database': cluster['DBName']
                    }
                }
                self.results['score'] += 0.5
            else:
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Redshift cluster configured correctly',
                    'details': {
                        'cluster_id': self.cluster_id,
                        'node_type': cluster['NodeType'],
                        'num_nodes': cluster['NumberOfNodes'],
                        'status': cluster['ClusterStatus']
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
                'message': f"Error checking cluster: {str(e)}"
            }

    def test_task2_security_group(self):
        """Task 2: Verify security group configuration"""
        task_name = "Task 2: Configure Security Group"
        try:
            response = self.redshift_client.describe_clusters(
                ClusterIdentifier=self.cluster_id
            )
            
            cluster = response['Clusters'][0]
            vpc_security_groups = cluster.get('VpcSecurityGroups', [])
            
            if not vpc_security_groups:
                self.results['tasks'][task_name] = {
                    'status': 'FAIL',
                    'message': 'No security group attached to cluster'
                }
                return
            
            sg_id = vpc_security_groups[0]['VpcSecurityGroupId']
            
            # Check security group rules
            sg_response = self.ec2_client.describe_security_groups(
                GroupIds=[sg_id]
            )
            
            security_group = sg_response['SecurityGroups'][0]
            issues = []
            
            # Check if Redshift port (5439) is open
            redshift_rule_found = False
            for rule in security_group.get('IpPermissions', []):
                if rule.get('FromPort') == 5439 and rule.get('ToPort') == 5439:
                    redshift_rule_found = True
                    break
            
            if not redshift_rule_found:
                issues.append("Redshift port 5439 not open in security group")
            
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

    def test_task3_public_accessibility(self):
        """Task 3: Verify public accessibility"""
        task_name = "Task 3: Configure Public Accessibility"
        try:
            response = self.redshift_client.describe_clusters(
                ClusterIdentifier=self.cluster_id
            )
            
            cluster = response['Clusters'][0]
            
            if cluster.get('PubliclyAccessible', False):
                endpoint = cluster.get('Endpoint', {})
                self.results['tasks'][task_name] = {
                    'status': 'PASS',
                    'message': 'Public accessibility is enabled',
                    'details': {
                        'publicly_accessible': True,
                        'endpoint': endpoint.get('Address', 'N/A'),
                        'port': endpoint.get('Port', 'N/A')
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

    def test_task4_tags(self):
        """Task 4: Verify cluster tags"""
        task_name = "Task 4: Add Resource Tags"
        try:
            response = self.redshift_client.describe_clusters(
                ClusterIdentifier=self.cluster_id
            )
            
            cluster = response['Clusters'][0]
            
            # Get tags
            tags = {tag['Key']: tag['Value'] for tag in cluster.get('Tags', [])}
            issues = []
            
            required_tags = {
                'Environment': 'Development',
                'Project': 'Analytics',
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
        print(f"Starting Redshift Easy Assessment for Student: {self.student_id}")
        print("=" * 60)
        
        self.test_task1_cluster_exists()
        self.test_task2_security_group()
        self.test_task3_public_accessibility()
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
            f.write(f"Redshift Easy Assessment Results\n")
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
        print("Usage: python test_redshift_easy_assessment.py <student_id>")
        sys.exit(1)
    
    student_id = sys.argv[1]
    
    try:
        tester = RedshiftEasyAssessmentTester(student_id)
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
