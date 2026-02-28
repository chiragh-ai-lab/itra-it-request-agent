"""
Execute agent actions with Cedar policy checks.
Actions: notify_team, escalate, auto_resolve, request_info
"""
import json
import os
from datetime import datetime
from utils import success, error, get_tenant_id, get_dynamodb_resource

TABLE_NAME = os.environ['TABLE_NAME']

VALID_ACTIONS = ['notify_team', 'escalate', 'auto_resolve', 'request_info']

def check_cedar_policy(action, request_item):
    """
    Check Cedar policies before executing action.
    Returns (allowed: bool, reason: str)
    """
    # Rate limit: max 5 actions per request
    action_count = len(request_item.get('agent_actions', []))
    if action_count >= 5:
        return False, "Rate limit exceeded: maximum 5 actions per request"
    
    # Force escalation for severity 1 (critical)
    if action == 'auto_resolve' and request_item.get('severity') == 1:
        return False, "Cannot auto-resolve severity 1 (critical) requests - escalation required"
    
    # Block provisioning without manager approval (placeholder for future)
    if action == 'provision_resource' and not request_item.get('has_manager_approval'):
        return False, "Provisioning requires manager approval"
    
    return True, "Policy check passed"

def execute_action(action, request_item, parameters):
    """Execute the specified action"""
    result = {}
    
    if action == 'notify_team':
        # TODO: Trigger notification Lambda
        result = {
            'status': 'sent',
            'team': request_item.get('routing_team'),
            'message': 'Team notification sent'
        }
    
    elif action == 'escalate':
        # TODO: Trigger escalation notification
        result = {
            'status': 'escalated',
            'escalated_to': 'admin',
            'message': 'Request escalated to admin team'
        }
    
    elif action == 'auto_resolve':
        # TODO: Trigger resolve Lambda
        result = {
            'status': 'resolved',
            'resolution': parameters.get('resolution', 'Auto-resolved by agent'),
            'message': 'Request auto-resolved'
        }
    
    elif action == 'request_info':
        result = {
            'status': 'info_requested',
            'info_needed': parameters.get('info_needed', []),
            'message': 'Additional information requested from user'
        }
    
    return result

def handler(event, context):
    """Execute agent action with policy check"""
    try:
        tenant_id = get_tenant_id(event)
        request_id = event['pathParameters']['id']
        body = json.loads(event.get('body', '{}'))
        
        action = body.get('action')
        parameters = body.get('parameters', {})
        
        if not action:
            return error('Action is required', 400)
        
        if action not in VALID_ACTIONS:
            return error(f'Invalid action. Must be one of: {", ".join(VALID_ACTIONS)}', 400)
        
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
        
        # Check Cedar policy
        allowed, reason = check_cedar_policy(action, request_item)
        
        if not allowed:
            # Log policy block
            print(f"Policy blocked action '{action}' for request {request_id}: {reason}")
            
            # Record policy block in agent_actions
            policy_block = {
                'action': action,
                'status': 'blocked',
                'reason': reason,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            
            table.update_item(
                Key={
                    'PK': f'TENANT#{tenant_id}',
                    'SK': f'REQ#{request_id}'
                },
                UpdateExpression='SET agent_actions = list_append(if_not_exists(agent_actions, :empty_list), :action)',
                ExpressionAttributeValues={
                    ':action': [policy_block],
                    ':empty_list': []
                }
            )
            
            return error(f'Action blocked by policy: {reason}', 403)
        
        # Execute action
        result = execute_action(action, request_item, parameters)
        
        # Record action in agent_actions array
        action_record = {
            'action': action,
            'parameters': parameters,
            'result': result,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        # Update request
        update_response = table.update_item(
            Key={
                'PK': f'TENANT#{tenant_id}',
                'SK': f'REQ#{request_id}'
            },
            UpdateExpression="""
                SET agent_actions = list_append(if_not_exists(agent_actions, :empty_list), :action),
                    #status = :status,
                    updated_at = :updated_at
            """,
            ExpressionAttributeNames={
                '#status': 'status'
            },
            ExpressionAttributeValues={
                ':action': [action_record],
                ':empty_list': [],
                ':status': 'in_progress' if action != 'auto_resolve' else 'resolved',
                ':updated_at': datetime.utcnow().isoformat() + 'Z'
            },
            ReturnValues='ALL_NEW'
        )
        
        return success({
            'message': 'Action executed successfully',
            'action': action,
            'result': result,
            'request': update_response['Attributes']
        })
        
    except ValueError as e:
        return error(str(e), 400)
    except KeyError as e:
        return error(f'Missing required field: {str(e)}', 400)
    except Exception as e:
        print(f"Error executing action: {str(e)}")
        return error('Action execution failed', 500)
