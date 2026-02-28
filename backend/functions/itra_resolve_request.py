"""
Resolve IT request - mark as resolved and capture resolution details.
"""
import json
import os
from datetime import datetime
from utils import success, error, get_tenant_id, get_dynamodb_resource

TABLE_NAME = os.environ['TABLE_NAME']

def handler(event, context):
    """Resolve request"""
    try:
        tenant_id = get_tenant_id(event)
        request_id = event['pathParameters']['id']
        body = json.loads(event.get('body', '{}'))
        
        resolution_text = body.get('resolution', '').strip()
        resolved_by = body.get('resolved_by', 'agent')
        
        if not resolution_text:
            return error('Resolution text is required', 400)
        
        # Get request from DynamoDB
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(TABLE_NAME)
        
        response = table.get_item(
            Key={
                'PK': f'TENANT#{tenant_id}',
                'SK': f'REQ#{request_id}'
            }
        )
        
        request_item = response.get('Item')
        if not request_item:
            return error('Request not found', 404)
        
        # Check if already resolved
        if request_item.get('status') == 'resolved':
            return error('Request is already resolved', 400)
        
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        # Create resolution object
        resolution = {
            'resolution_text': resolution_text,
            'resolved_by': resolved_by,
            'resolved_at': timestamp
        }
        
        # Update request
        update_response = table.update_item(
            Key={
                'PK': f'TENANT#{tenant_id}',
                'SK': f'REQ#{request_id}'
            },
            UpdateExpression="""
                SET resolution = :resolution,
                    #status = :status,
                    updated_at = :updated_at
            """,
            ExpressionAttributeNames={
                '#status': 'status'
            },
            ExpressionAttributeValues={
                ':resolution': resolution,
                ':status': 'resolved',
                ':updated_at': timestamp
            },
            ReturnValues='ALL_NEW'
        )
        
        # TODO: Send resolution notification to submitter
        
        return success({
            'message': 'Request resolved successfully',
            'request': update_response['Attributes']
        })
        
    except ValueError as e:
        return error(str(e), 400)
    except KeyError as e:
        return error(f'Missing required field: {str(e)}', 400)
    except Exception as e:
        print(f"Error resolving request: {str(e)}")
        return error('Failed to resolve request', 500)
