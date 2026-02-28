"""
Shared utilities for Lambda functions.
Prevents CORS, Decimal, SigV4, and tenant isolation bugs.
"""
import json
import boto3
from decimal import Decimal
from botocore.config import Config

# CORS headers for ALL responses
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,PATCH,DELETE,OPTIONS'
}

def convert_decimals(obj):
    """
    Recursively convert Decimal objects to float.
    DynamoDB returns Decimal, but JavaScript cannot render it.
    """
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    return obj

def success(body, status_code=200):
    """Standard success response with CORS headers"""
    return {
        'statusCode': status_code,
        'headers': CORS_HEADERS,
        'body': json.dumps(convert_decimals(body))
    }

def error(message, status_code=400):
    """Standard error response with CORS headers"""
    return {
        'statusCode': status_code,
        'headers': CORS_HEADERS,
        'body': json.dumps({'error': message})
    }

def get_tenant_id(event):
    """
    Extract tenant_id from Cognito JWT claims.
    Use this for ALL DynamoDB operations to enforce tenant isolation.
    """
    try:
        claims = event['requestContext']['authorizer']['claims']
        return claims['sub']  # Cognito user ID as tenant_id
    except (KeyError, TypeError):
        raise ValueError("Missing or invalid authorization claims")

def get_s3_client():
    """
    Get S3 client configured with SigV4.
    Required for KMS-encrypted buckets.
    """
    return boto3.client('s3', config=Config(signature_version='s3v4'))

def get_dynamodb_resource():
    """Get DynamoDB resource"""
    return boto3.resource('dynamodb')

def get_bedrock_client():
    """Get Bedrock runtime client"""
    return boto3.client('bedrock-runtime')

def generate_presigned_url(bucket, key, operation='put_object', expiry=3600):
    """
    Generate presigned URL for S3 operations.
    Uses SigV4 for KMS-encrypted buckets.
    
    Args:
        bucket: S3 bucket name
        key: S3 object key
        operation: 'put_object' or 'get_object'
        expiry: URL expiry in seconds (default 1 hour)
    """
    s3_client = get_s3_client()
    url = s3_client.generate_presigned_url(
        ClientMethod=operation,
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=expiry
    )
    return url

# S3 path skip list for processing triggers
SKIP_PREFIXES = ['/exports/', '/generated/', '/internal/']

def should_skip_processing(s3_key):
    """
    Check if S3 key should be skipped from processing.
    Prevents infinite loops when generated files trigger processing.
    """
    return any(prefix in s3_key for prefix in SKIP_PREFIXES)
