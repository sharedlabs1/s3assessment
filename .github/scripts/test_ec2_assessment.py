#!/usr/bin/env python3
"""
EC2 Assessment Test Cases
Tests learner's EC2 configuration against requirements
"""

import boto3
import json
import traceback
from datetime import datetime
from typing import Dict, List, Tuple

class EC2AssessmentTester:
    def __init__(self, student_id=None):
        self.ec2_client = boto3.client('ec2')
        self.sts_client = boto3.client('sts')
        self.account_id = self.sts_client.get_caller_identity()['Account']
        
        self.student_id = student_id
        self.instance_name = f'webserver-{student_id}' if student_id else None
        self.sg_name = f'web-sg-{student_id}' if student_id else None
        self.eip_name = f'webserver-eip-{student_id}' if student_id else None
        
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def log_result(self, passed: bool, test_name: str, details: str):
        """Log test result"""
        status = "[PASS]" if passed else "[FAIL]"
        self.results.append(f"{status} {test_name}")
        self.results.append(f"       {details}")
        self.results.append("")
        
        if passed:
            self.passed += 1
        else:
            self.failed += 1
    
    def test_task1_instance_launch(self):
        """Test Task 1: EC2 instance launch and configuration"""
        print("Testing Task 1: EC2 Instance Launch...")
        
        # Find instance by name tag
        try:
            response = self.ec2_client.describe_instances(
                Filters=[
                    {'Name': 'tag:Name', 'Values': [self.instance_name]},
                    {'Name': 'instance-state-name', 'Values': ['running', 'stopped']}
                ]
            )
            
            instances = []
            for reservation in response['Reservations']:
                instances.extend(reservation['Instances'])
            
            if instances:
                instance = instances[0]
                self.log_result(True,
                    "Task 1.1 - Instance Exists",
                    f"Instance '{self.instance_name}' found with ID: {instance['InstanceId']}")
                
                # Check instance type
                if instance['InstanceType'] == 't2.micro':
                    self.log_result(True,
                        "Task 1.2 - Instance Type",
                        f"Correct instance type: t2.micro")
                else:
                    self.log_result(False,
                        "Task 1.2 - Instance Type",
                        f"Incorrect instance type. Expected: t2.micro, Got: {instance['InstanceType']}")
                
                # Check tags
                tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                required_tags = {
                    'Environment': 'Development',
                    'Project': 'WebServer',
                    'StudentID': self.student_id
                }
                
                missing_tags = []
                for key, value in required_tags.items():
                    if tags.get(key) != value:
                        missing_tags.append(f"{key}={value}")
                
                if not missing_tags:
                    self.log_result(True,
                        "Task 1.3 - Instance Tags",
                        "All required tags present and correct")
                else:
                    self.log_result(False,
                        "Task 1.3 - Instance Tags",
                        f"Missing or incorrect tags: {', '.join(missing_tags)}")
            else:
                self.log_result(False,
                    "Task 1.1 - Instance Exists",
                    f"Instance '{self.instance_name}' not found")
                self.log_result(False,
                    "Task 1.2 - Instance Type",
                    "Cannot verify - instance not found")
                self.log_result(False,
                    "Task 1.3 - Instance Tags",
                    "Cannot verify - instance not found")
        
        except Exception as e:
            self.log_result(False, "Task 1 - Critical Error", f"Error: {str(e)}")
    
    def test_task2_security_group(self):
        """Test Task 2: Security group configuration"""
        print("Testing Task 2: Security Group Configuration...")
        
        try:
            response = self.ec2_client.describe_security_groups(
                Filters=[{'Name': 'group-name', 'Values': [self.sg_name]}]
            )
            
            if response['SecurityGroups']:
                sg = response['SecurityGroups'][0]
                self.log_result(True,
                    "Task 2.1 - Security Group Exists",
                    f"Security group '{self.sg_name}' found")
                
                # Check ingress rules
                ingress_rules = sg.get('IpPermissions', [])
                
                # Check for SSH, HTTP, HTTPS
                has_ssh = any(rule.get('FromPort') == 22 for rule in ingress_rules)
                has_http = any(rule.get('FromPort') == 80 for rule in ingress_rules)
                has_https = any(rule.get('FromPort') == 443 for rule in ingress_rules)
                
                if has_ssh and has_http and has_https:
                    self.log_result(True,
                        "Task 2.2 - Security Group Rules",
                        "All required ports configured (SSH:22, HTTP:80, HTTPS:443)")
                else:
                    missing = []
                    if not has_ssh: missing.append("SSH (22)")
                    if not has_http: missing.append("HTTP (80)")
                    if not has_https: missing.append("HTTPS (443)")
                    self.log_result(False,
                        "Task 2.2 - Security Group Rules",
                        f"Missing ports: {', '.join(missing)}")
            else:
                self.log_result(False,
                    "Task 2.1 - Security Group Exists",
                    f"Security group '{self.sg_name}' not found")
                self.log_result(False,
                    "Task 2.2 - Security Group Rules",
                    "Cannot verify - security group not found")
        
        except Exception as e:
            self.log_result(False, "Task 2 - Critical Error", f"Error: {str(e)}")
    
    def test_task3_elastic_ip(self):
        """Test Task 3: Elastic IP allocation and association"""
        print("Testing Task 3: Elastic IP...")
        
        try:
            response = self.ec2_client.describe_addresses(
                Filters=[{'Name': 'tag:Name', 'Values': [self.eip_name]}]
            )
            
            if response['Addresses']:
                eip = response['Addresses'][0]
                self.log_result(True,
                    "Task 3.1 - Elastic IP Allocated",
                    f"Elastic IP allocated: {eip.get('PublicIp')}")
                
                if eip.get('AssociationId'):
                    self.log_result(True,
                        "Task 3.2 - Elastic IP Associated",
                        f"Elastic IP is associated with instance")
                else:
                    self.log_result(False,
                        "Task 3.2 - Elastic IP Associated",
                        "Elastic IP is not associated with any instance")
            else:
                self.log_result(False,
                    "Task 3.1 - Elastic IP Allocated",
                    f"Elastic IP with tag Name='{self.eip_name}' not found")
                self.log_result(False,
                    "Task 3.2 - Elastic IP Associated",
                    "Cannot verify - Elastic IP not found")
        
        except Exception as e:
            self.log_result(False, "Task 3 - Critical Error", f"Error: {str(e)}")
    
    def generate_report(self):
        """Generate test report"""
        report = []
        report.append("=" * 70)
        report.append("AWS EC2 ASSESSMENT - TEST REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report.append(f"Account ID: {self.account_id}")
        if self.student_id:
            report.append(f"Student ID: {self.student_id}")
        report.append("")
        report.append(f"SUMMARY: {self.passed} passed, {self.failed} failed")
        report.append("=" * 70)
        report.append("")
        
        report.extend(self.results)
        
        report.append("=" * 70)
        if self.failed == 0:
            report.append("STATUS: ✓ ALL TESTS PASSED - Excellent work!")
        else:
            report.append(f"STATUS: ✗ {self.failed} TEST(S) FAILED - Please review and fix")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def run_all_tests(self):
        """Run all test cases"""
        try:
            self.test_task1_instance_launch()
        except Exception as e:
            self.log_result(False, "Task 1 - Critical Error", f"Error: {str(e)}")
        
        try:
            self.test_task2_security_group()
        except Exception as e:
            self.log_result(False, "Task 2 - Critical Error", f"Error: {str(e)}")
        
        try:
            self.test_task3_elastic_ip()
        except Exception as e:
            self.log_result(False, "Task 3 - Critical Error", f"Error: {str(e)}")
        
        report = self.generate_report()
        
        # Write report to file
        with open('test_report.log', 'w') as f:
            f.write(report)
        
        print(report)
        
        return self.failed == 0

if __name__ == "__main__":
    import sys
    # Get student_id from command line argument if provided
    student_id = sys.argv[1] if len(sys.argv) > 1 else None
    
    try:
        tester = EC2AssessmentTester(student_id=student_id)
        success = tester.run_all_tests()
        exit(0 if success else 1)
    except Exception as e:
        # Create error report when initialization fails
        error_type = type(e).__name__
        error_msg = str(e)
        
        error_report = [
            "=" * 70,
            "AWS EC2 ASSESSMENT - TEST REPORT",
            "=" * 70,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "Account ID: Unable to retrieve (credentials error)",
        ]
        
        if student_id:
            error_report.append(f"Student ID: {student_id}")
        
        error_report.extend([
            "",
            "SUMMARY: 0 passed, 7 failed",
            "=" * 70,
            "",
            f"[FAIL] Initialization Failed",
            f"       Error Type: {error_type}",
            f"       Error: {error_msg}",
            "",
            "Stack Trace:",
            traceback.format_exc(),
            "",
            "=" * 70,
            "STATUS: ✗ ALL TESTS FAILED - AWS Configuration Error",
            "=" * 70
        ])
        
        report_text = "\n".join(error_report)
        with open('test_report.log', 'w') as f:
            f.write(report_text)
        print(report_text)
        exit(1)
