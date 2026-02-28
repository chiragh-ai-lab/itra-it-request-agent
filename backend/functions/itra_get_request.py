"""
Get single IT request with related entities (comments, logs, resolution).
"""
import os
from boto3.dynamodb.conditions import Key
from utils import success, error, get_tenant_id, get_dynamodb_resource

TABLE_NAME = os.environ['TABLE_NAME']

def handler(event, context):
    """Get request detail"""
    try:
        tenant_id = get_tenant_id(event)
        request_id = event['pathParameters']['id']
        
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(TABLE_NAME)
        
        # Get main request
        response = table.get_item(
            Key={
                'PK': f'TENANT#{tenant_id}',
                'SK': f'REQ#{request_id}'
            }
        )
        
        request_item = response.get('Item')
        if not request_item:
            return error('Request not found', 404)
        
        # Get related entities (comments, logs, resolution) via GSI1
        related_response = table.query(
            IndexName='GSI1',
            KeyConditionExpression=Key('GSI1PK').eq(f'REQ#{request_id}')
        )
        
        related_items = related_response.get('Items', [])
        
        # Separate by entity type
        comments = [item for item in related_items if item['SK'].startswith('COMMENT#')]
        logs = [item for item in related_items if item['SK'].startswith('ALOG#')]
        resolution = next((item for item in related_items if item['SK'].startswith('RES#')), None)
        
        return success({
            'request': request_item,
            'comments': comments,
            'logs': logs,
            'resolution': resolution
        })
        
    except ValueError as e:
        return error(str(e), 400)
    except KeyError:
        return error('Missing request ID in path', 400)
    except Exception as e:
        print(f"Error getting request: {str(e)}")
        return error('Failed to get request', 500)
