"""
Health check endpoint - tests API Gateway, Lambda, and basic connectivity.
No authentication required.
"""
import json
from utils import CORS_HEADERS

def handler(event, context):
    """Simple health check"""
    return {
        'statusCode': 200,
        'headers': CORS_HEADERS,
        'body': json.dumps({
            'status': 'healthy',
            'service': 'itra-api',
            'version': '1.0.0'
        })
    }
