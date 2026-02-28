"""
Send email notifications via AWS SES.
Supports HTML + plain text multipart MIME.
"""
import json
import os
import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from utils import success, error

SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'noreply@example.com')
SES_REGION = os.environ.get('AWS_REGION', 'us-east-1')

def get_ses_client():
    """Get SES client"""
    return boto3.client('ses', region_name=SES_REGION)

def create_notification_email(notification_type, request_data):
    """Create email content based on notification type"""
    
    if notification_type == 'new_request':
        subject = f"New IT Request: {request_data['title']}"
        html_body = f"""
        <html>
        <body>
            <h2>New IT Request Submitted</h2>
            <p><strong>Request ID:</strong> {request_data['request_id']}</p>
            <p><strong>Title:</strong> {request_data['title']}</p>
            <p><strong>Description:</strong> {request_data['description']}</p>
            <p><strong>Category:</strong> {request_data.get('category', 'Not classified')}</p>
            <p><strong>Severity:</strong> {request_data.get('severity', 'Not classified')}</p>
            <p><strong>Submitted by:</strong> {request_data['submitter_name']} ({request_data['submitter_email']})</p>
            <p><strong>Status:</strong> {request_data['status']}</p>
        </body>
        </html>
        """
        text_body = f"""
New IT Request Submitted

Request ID: {request_data['request_id']}
Title: {request_data['title']}
Description: {request_data['description']}
Category: {request_data.get('category', 'Not classified')}
Severity: {request_data.get('severity', 'Not classified')}
Submitted by: {request_data['submitter_name']} ({request_data['submitter_email']})
Status: {request_data['status']}
        """
    
    elif notification_type == 'escalation':
        subject = f"ESCALATION: {request_data['title']}"
        html_body = f"""
        <html>
        <body>
            <h2 style="color: red;">Request Escalated</h2>
            <p><strong>Request ID:</strong> {request_data['request_id']}</p>
            <p><strong>Title:</strong> {request_data['title']}</p>
            <p><strong>Severity:</strong> {request_data.get('severity', 'Unknown')}</p>
            <p><strong>Reason:</strong> {request_data.get('escalation_reason', 'Manual escalation')}</p>
            <p>This request requires immediate attention.</p>
        </body>
        </html>
        """
        text_body = f"""
REQUEST ESCALATED

Request ID: {request_data['request_id']}
Title: {request_data['title']}
Severity: {request_data.get('severity', 'Unknown')}
Reason: {request_data.get('escalation_reason', 'Manual escalation')}

This request requires immediate attention.
        """
    
    elif notification_type == 'policy_block':
        subject = f"Policy Block: {request_data['action']}"
        html_body = f"""
        <html>
        <body>
            <h2>Agent Action Blocked by Policy</h2>
            <p><strong>Request ID:</strong> {request_data['request_id']}</p>
            <p><strong>Action:</strong> {request_data['action']}</p>
            <p><strong>Reason:</strong> {request_data['reason']}</p>
            <p>Manual review required.</p>
        </body>
        </html>
        """
        text_body = f"""
Agent Action Blocked by Policy

Request ID: {request_data['request_id']}
Action: {request_data['action']}
Reason: {request_data['reason']}

Manual review required.
        """
    
    else:
        subject = "IT Request Notification"
        html_body = "<html><body><p>IT Request notification</p></body></html>"
        text_body = "IT Request notification"
    
    return subject, html_body, text_body

def send_email(recipient, subject, html_body, text_body):
    """Send multipart MIME email via SES"""
    ses = get_ses_client()
    
    # Create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient
    
    # Attach parts
    part1 = MIMEText(text_body, 'plain')
    part2 = MIMEText(html_body, 'html')
    
    msg.attach(part1)
    msg.attach(part2)
    
    # Send
    response = ses.send_raw_email(
        Source=SENDER_EMAIL,
        Destinations=[recipient],
        RawMessage={'Data': msg.as_string()}
    )
    
    return response['MessageId']

def handler(event, context):
    """Send notification email"""
    try:
        body = json.loads(event.get('body', '{}'))
        
        notification_type = body.get('type')
        recipient = body.get('recipient')
        request_data = body.get('request_data', {})
        
        if not notification_type:
            return error('Notification type is required', 400)
        if not recipient:
            return error('Recipient email is required', 400)
        
        # Create email content
        subject, html_body, text_body = create_notification_email(notification_type, request_data)
        
        # Send email
        message_id = send_email(recipient, subject, html_body, text_body)
        
        return success({
            'message': 'Notification sent successfully',
            'message_id': message_id,
            'recipient': recipient
        })
        
    except Exception as e:
        print(f"Error sending notification: {str(e)}")
        return error('Failed to send notification', 500)
