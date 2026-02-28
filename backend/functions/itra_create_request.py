"""
Create IT request - stores in DynamoDB and triggers async classification.
"""
import json
import os
import uuid
from datetime import datetime
from decimal import Decimal
from utils import success, error, get_tenant_id, get_dynamodb_resource

TABLE_NAME = os.environ['TABLE_NAME']

def handler(event, context):
    """Create new IT request"""
    try:
        tenant_id = get_tenant_id(event)
        body = json.loads(event.get('body', '{}'))
        
        # Validate required fields
        title = body.get('title', '').strip()
        description = body.get('description', '').strip()
        
        if not title:
            return error('Title is required', 400)
        if not description:
            return error('Description is required', 400)
        
        # Extract submitter info from JWT claims
        claims = event['requestContext']['authorizer']['claims']
        submitter_email = claims.get('email', 'unknown@example.com')
        submitter_name = claims.get('name', submitter_email.split('@')[0])
        
        # Generate request ID
        request_id = f"req_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        # Create request entity
        request_item = {
            'PK': f'TENANT#{tenant_id}',
            'SK': f'REQ#{request_id}',
            'GSI1PK': f'TENANT#{tenant_id}#REQ',
            'GSI1SK': timestamp,
            'request_id': request_id,
            'title': title,
            'description': description,
            'status': 'submitted',
            'category': None,
            'severity': None,
            'routing_team': None,
            'classification_confidence': None,
            'submitter_email': submitter_email,
            'submitter_name': submitter_name,
            'agent_actions': [],
            'resolution': None,
            'created_at': timestamp,
            'updated_at': timestamp
        }
        
        # Store in DynamoDB
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(TABLE_NAME)
        table.put_item(Item=request_item)
        
        # TODO: Trigger async classification Lambda
        # This will be implemented in the AI integration feature
        
        return success({
            'request_id': request_id,
            'status': 'submitted',
            'message': 'Request created successfully'
        }, 201)
        
    except ValueError as e:
        return error(str(e), 400)
    except Exception as e:
        print(f"Error creating request: {str(e)}")
        return error('Failed to create request', 500)
