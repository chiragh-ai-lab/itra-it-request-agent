"""
Multi-turn chat agent using AWS Bedrock Claude Sonnet with streaming.
Provides context-aware responses about IT requests.
"""
import json
import os
from utils import success, error, get_tenant_id, get_dynamodb_resource, get_bedrock_client

TABLE_NAME = os.environ['TABLE_NAME']
CHAT_MODEL = os.environ.get('CHAT_MODEL', 'us.anthropic.claude-sonnet-4-6-20260217')

SYSTEM_PROMPT = """You are a helpful IT support agent assistant. You help users with their IT requests by:
- Providing status updates on their requests
- Answering questions about IT policies and procedures
- Offering troubleshooting guidance
- Explaining what actions have been taken on their requests

Be concise, professional, and helpful. If you don't know something, say so clearly."""

def get_request_context(tenant_id, request_id, table):
    """Retrieve request context for grounding"""
    response = table.get_item(
        Key={
            'PK': f'TENANT#{tenant_id}',
            'SK': f'REQ#{request_id}'
        }
    )
    
    request_item = response.get('Item')
    if not request_item:
        return None
    
    # Format request context for the agent
    context = f"""Current Request Context:
- Request ID: {request_item['request_id']}
- Title: {request_item['title']}
- Description: {request_item['description']}
- Status: {request_item['status']}
- Category: {request_item.get('category', 'Not yet classified')}
- Severity: {request_item.get('severity', 'Not yet classified')}
- Routing Team: {request_item.get('routing_team', 'Not yet assigned')}
- Created: {request_item['created_at']}
- Last Updated: {request_item['updated_at']}
"""
    
    # Add agent actions if any
    agent_actions = request_item.get('agent_actions', [])
    if agent_actions:
        context += "\nAgent Actions Taken:\n"
        for action in agent_actions:
            context += f"- {action['action']} at {action['timestamp']}: {action.get('result', {}).get('message', 'No details')}\n"
    
    return context

def handler(event, context):
    """Chat with agent about a request"""
    try:
        tenant_id = get_tenant_id(event)
        request_id = event['pathParameters']['id']
        body = json.loads(event.get('body', '{}'))
        
        user_message = body.get('message', '').strip()
        conversation_history = body.get('history', [])
        
        if not user_message:
            return error('Message is required', 400)
        
        # Get request context
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(TABLE_NAME)
        
        request_context = get_request_context(tenant_id, request_id, table)
        if not request_context:
            return error('Request not found', 404)
        
        # Build messages for Claude
        messages = []
        
        # Add conversation history (limit to last 10 messages to avoid context overflow)
        for msg in conversation_history[-10:]:
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        # Add current user message with request context
        messages.append({
            'role': 'user',
            'content': f"{request_context}\n\nUser Question: {user_message}"
        })
        
        # Call Bedrock
        bedrock = get_bedrock_client()
        
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "system": SYSTEM_PROMPT,
            "messages": messages
        }
        
        # Non-streaming response for simplicity (streaming requires different API pattern)
        response = bedrock.invoke_model(
            modelId=CHAT_MODEL,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        assistant_message = response_body['content'][0]['text']
        
        return success({
            'message': assistant_message,
            'request_id': request_id
        })
        
    except ValueError as e:
        return error(str(e), 400)
    except KeyError as e:
        return error(f'Missing required field: {str(e)}', 400)
    except Exception as e:
        print(f"Error in chat: {str(e)}")
        return error('Chat failed', 500)
