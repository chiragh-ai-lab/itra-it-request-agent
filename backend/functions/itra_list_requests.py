"""
List IT requests for a tenant - uses GSI1 for efficient querying.
"""
import os
from boto3.dynamodb.conditions import Key
from utils import success, error, get_tenant_id, get_dynamodb_resource

TABLE_NAME = os.environ['TABLE_NAME']

def handler(event, context):
    """List all requests for the tenant"""
    try:
        tenant_id = get_tenant_id(event)
        
        # Query GSI1 for all requests
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(TABLE_NAME)
        
        response = table.query(
            IndexName='GSI1',
            KeyConditionExpression=Key('GSI1PK').eq(f'TENANT#{tenant_id}#REQ'),
            ScanIndexForward=False  # Sort by created_at descending (newest first)
        )
        
        requests = response.get('Items', [])
        
        # Handle pagination if needed
        while 'LastEvaluatedKey' in response:
            response = table.query(
                IndexName='GSI1',
                KeyConditionExpression=Key('GSI1PK').eq(f'TENANT#{tenant_id}#REQ'),
                ScanIndexForward=False,
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            requests.extend(response.get('Items', []))
        
        return success({
            'requests': requests,
            'count': len(requests)
        })
        
    except ValueError as e:
        return error(str(e), 400)
    except Exception as e:
        print(f"Error listing requests: {str(e)}")
        return error('Failed to list requests', 500)
