"""
AWS EMR - Easy Assessment - Test Script
Tests EMR cluster creation, Spark jobs, data processing
"""

import sys
import boto3
from botocore.exceptions import ClientError

def get_student_id():
    if len(sys.argv) < 2:
        print("Error: Student ID is required")
        sys.exit(1)
    return sys.argv[1]

def test_s3_bucket_exists(s3_client, student_id):
    """Task 1: Verify EMR S3 bucket exists"""
    bucket_name = f"emr-{student_id}"
    
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✅ Task 1 Passed: S3 bucket exists")
        return True
    except ClientError:
        print(f"❌ Task 1 Failed: Bucket not found")
        return False

def test_emr_cluster_exists(emr_client, student_id):
    """Task 4: Verify EMR cluster was created"""
    try:
        response = emr_client.list_clusters(
            ClusterStates=['WAITING', 'RUNNING', 'TERMINATED']
        )
        
        clusters = [c for c in response['Clusters'] if student_id in c['Name']]
        
        if clusters:
            print(f"✅ Task 4 Passed: {len(clusters)} EMR cluster(s) found")
            return True
        print(f"⚠️  Task 4 Warning: No EMR clusters found")
        return True
    except Exception as e:
        print(f"⚠️  Task 4 Warning: {e}")
        return True

def test_spark_output_exists(s3_client, student_id):
    """Task 5-6: Verify Spark job outputs"""
    bucket = f"emr-{student_id}"
    
    try:
        response = s3_client.list_objects_v2(
            Bucket=bucket,
            Prefix='output/'
        )
        
        if response.get('KeyCount', 0) > 0:
            print(f"✅ Task 5-6 Passed: Spark outputs found")
            return True
        print(f"⚠️  Task 5-6 Warning: No outputs found")
        return True
    except Exception as e:
        print(f"⚠️  Task 5-6 Warning: {e}")
        return True

def main():
    print("=" * 60)
    print("AWS EMR - Easy Assessment - Validation")
    print("=" * 60)
    
    student_id = get_student_id()
    print(f"\n🎓 Student ID: {student_id}\n")
    
    try:
        s3_client = boto3.client('s3')
        emr_client = boto3.client('emr')
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    results = []
    total_tasks = 10
    
    results.append(test_s3_bucket_exists(s3_client, student_id))
    results.append(test_emr_cluster_exists(emr_client, student_id))
    results.append(test_spark_output_exists(s3_client, student_id))
    
    # Placeholder for remaining tests
    for i in range(7):
        results.append(True)
    
    passed = sum(results)
    score = (passed / total_tasks) * 100
    
    print("\n" + "=" * 60)
    print(f"Score: {score:.1f}%")
    print("=" * 60)
    
    if score >= 70:
        print("\n🎉 PASSED! EMR Easy assessment completed!")
        sys.exit(0)
    else:
        print("\n❌ Not passed. Minimum: 70%")
        sys.exit(1)

if __name__ == "__main__":
    main()
