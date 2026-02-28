"""
Update IT request - status, resolution, classification results, etc.
"""
import json
import os
from datetime import datetime
from decimal import Decimal
from utils import success, error, get_tenant_id, get_dynamodb_resource

TABLE_NAME = os.environ['TABLE_NAME']

VALID_STATUSES = ['submitted', 'classified', 'in_progress', 'resolved', 'classification_failed']
VALID_CATEGORIES = ['access', 'hardware', 'software', 'cloud', 'network']
VALID_SEVERITIES = [1, 2, 3, 4]

def handler(event, context):
    """Update request fields"""
    try:
        tenant_id = get_tenant_id(event)
        request_id = event['pathParameters']['id']
        body = json.loads(event.get('body', '{}'))
        
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(TABLE_NAME)
        
        # Build update expression
        update_parts = []
        expression_values = {}
        expression_names = {}
        
        # Status update
        if 'status' in body:
            status = body['status']
            if status not in VALID_STATUSES:
                return error(f'Invalid status. Must be one of: {", ".join(VALID_STATUSES)}', 400)
            update_parts.append('#status = :status')
            expression_values[':status'] = status
            expression_names['#status'] = 'status'
        
        # Category update (from classification)
        if 'category' in body:
            category = body['category']
            if category and category not in VALID_CATEGORIES:
                return error(f'Invalid category. Must be one of: {", ".join(VALID_CATEGORIES)}', 400)
            update_parts.append('category = :category')
            expression_values[':category'] = category
        
        # Severity update (from classification)
        if 'severity' in body:
            severity = body['severity']
            if severity and severity not in VALID_SEVERITIES:
                return error(f'Invalid severity. Must be one of: {VALID_SEVERITIES}', 400)
            update_parts.append('severity = :severity')
            expression_values[':severity'] = severity
        
        # Routing team update (from classification)
        if 'routing_team' in body:
            update_parts.append('routing_team = :routing_team')
            expression_values[':routing_team'] = body['routing_team']
        
        # Classification confidence
        if 'classification_confidence' in body:
            update_parts.append('classification_confidence = :confidence')
            expression_values[':confidence'] = Decimal(str(body['classification_confidence']))
        
        # Resolution
        if 'resolution' in body:
            update_parts.append('resolution = :resolution')
            expression_values[':resolution'] = body['resolution']
        
        # Agent actions (append to list)
        if 'agent_action' in body:
            update_parts.append('agent_actions = list_append(if_not_exists(agent_actions, :empty_list), :action)')
            expression_values[':action'] = [body['agent_action']]
            expression_values[':empty_list'] = []
        
        if not update_parts:
            return error('No valid fields to update', 400)
        
        # Always update timestamp
        update_parts.append('updated_at = :updated_at')
        expression_values[':updated_at'] = datetime.utcnow().isoformat() + 'Z'
        
        # Execute update
        update_expression = 'SET ' + ', '.join(update_parts)
        
        response = table.update_item(
            Key={
                'PK': f'TENANT#{tenant_id}',
                'SK': f'REQ#{request_id}'
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_values,
            ExpressionAttributeNames=expression_names if expression_names else None,
            ReturnValues='ALL_NEW',
            ConditionExpression='attribute_exists(PK)'  # Ensure request exists
        )
        
        return success({
            'request': response['Attributes'],
            'message': 'Request updated successfully'
        })
        
    except ValueError as e:
        return error(str(e), 400)
    except KeyError:
        return error('Missing request ID in path', 400)
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return error('Request not found', 404)
    except Exception as e:
        print(f"Error updating request: {str(e)}")
        return error('Failed to update request', 500)
