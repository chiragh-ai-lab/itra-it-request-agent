"""
Classify IT request using AWS Bedrock Claude Haiku.
Uses async self-invocation pattern to avoid API Gateway timeout.
"""
import json
import os
import boto3
from utils import success, error, get_tenant_id, get_dynamodb_resource, get_bedrock_client

TABLE_NAME = os.environ['TABLE_NAME']
CLASSIFICATION_MODEL = os.environ.get('CLASSIFICATION_MODEL', 'us.anthropic.claude-3-5-haiku')

CLASSIFICATION_PROMPT = """You are an IT request classification agent.

Classify the following IT request into:
- category: one of [access, hardware, software, cloud, network]
- severity: 1 (critical/production down), 2 (high/blocking work), 3 (medium/workaround exists), 4 (low/nice to have)
- routing_team: one of [helpdesk, cloud-ops, security, infrastructure, development]
- suggested_actions: array of recommended actions

Request title: {title}
Request description: {description}

Return ONLY valid JSON. No markdown, no explanation.
{{
  "category": "...",
  "severity": N,
  "routing_team": "...",
  "confidence": 0.XX,
  "suggested_actions": ["..."],
  "reasoning": "one sentence why"
}}"""

def classify_with_bedrock(title, description):
    """Call Bedrock to classify the request"""
    bedrock = get_bedrock_client()
    
    prompt = CLASSIFICATION_PROMPT.format(title=title, description=description)
    
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    response = bedrock.invoke_model(
        modelId=CLASSIFICATION_MODEL,
        body=json.dumps(request_body)
    )
    
    response_body = json.loads(response['body'].read())
    
    # Extract text from Claude response
    content = response_body['content'][0]['text']
    
    # Parse JSON from response
    try:
        # Remove markdown code blocks if present
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        
        classification = json.loads(content)
        return classification
    except json.JSONDecodeError as e:
        print(f"Failed to parse classification JSON: {content}")
        raise ValueError(f"Invalid JSON response from classification model: {str(e)}")

def handler(event, context):
    """Classify request - async mode or API mode"""
    try:
        mode = event.get('mode')
        
        if mode == 'classify':
            # Background classification processing
            tenant_id = event['tenant_id']
            request_id = event['request_id']
            title = event['title']
            description = event['description']
            
            # Call Bedrock for classification
            classification = classify_with_bedrock(title, description)
            
            # Validate classification
            valid_categories = ['access', 'hardware', 'software', 'cloud', 'network']
            valid_teams = ['helpdesk', 'cloud-ops', 'security', 'infrastructure', 'development']
            
            if classification['category'] not in valid_categories:
                raise ValueError(f"Invalid category: {classification['category']}")
            if classification['routing_team'] not in valid_teams:
                raise ValueError(f"Invalid routing_team: {classification['routing_team']}")
            if not (1 <= classification['severity'] <= 4):
                raise ValueError(f"Invalid severity: {classification['severity']}")
            
            # Update request in DynamoDB
            dynamodb = get_dynamodb_resource()
            table = dynamodb.Table(TABLE_NAME)
            
            update_expression = """
                SET category = :category,
                    severity = :severity,
                    routing_team = :routing_team,
                    classification_confidence = :confidence,
                    #status = :status,
                    updated_at = :updated_at
            """
            
            from datetime import datetime
            from decimal import Decimal
            
            table.update_item(
                Key={
                    'PK': f'TENANT#{tenant_id}',
                    'SK': f'REQ#{request_id}'
                },
                UpdateExpression=update_expression,
                ExpressionAttributeNames={
                    '#status': 'status'
                },
                ExpressionAttributeValues={
                    ':category': classification['category'],
                    ':severity': classification['severity'],
                    ':routing_team': classification['routing_team'],
                    ':confidence': Decimal(str(classification['confidence'])),
                    ':status': 'classified' if classification['confidence'] >= 0.60 else 'classification_failed',
                    ':updated_at': datetime.utcnow().isoformat() + 'Z'
                }
            )
            
            print(f"Classification complete for {request_id}: {classification}")
            
            # TODO: Trigger agent action if confidence is high enough
            # TODO: Send notification to routing team
            
            return
        
        # API Gateway mode - trigger async classification
        tenant_id = get_tenant_id(event)
        request_id = event['pathParameters']['id']
        
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
        
        # Invoke self asynchronously for background processing
        lambda_client = boto3.client('lambda')
        lambda_client.invoke(
            FunctionName=context.function_name,
            InvocationType='Event',  # Async
            Payload=json.dumps({
                'mode': 'classify',
                'tenant_id': tenant_id,
                'request_id': request_id,
                'title': request_item['title'],
                'description': request_item['description']
            })
        )
        
        return success({
            'message': 'Classification started',
            'request_id': request_id
        })
        
    except ValueError as e:
        return error(str(e), 400)
    except KeyError as e:
        return error(f'Missing required field: {str(e)}', 400)
    except Exception as e:
        print(f"Error in classification: {str(e)}")
        return error('Classification failed', 500)
