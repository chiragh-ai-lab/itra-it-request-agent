#!/bin/bash

# End-to-end classification test
TENANT_ID="3408c4a8-b061-70b9-fb44-c83a6a5b0fc7"
REQUEST_ID="req_82f1fefa803d"

echo "Testing classification Lambda with actual request data..."

# Invoke Lambda with proper payload
aws lambda invoke \
  --function-name itra-classify-request \
  --region us-east-1 \
  --payload "{\"mode\":\"classify\",\"tenant_id\":\"$TENANT_ID\",\"request_id\":\"$REQUEST_ID\",\"title\":\"Need VPN access for remote work\",\"description\":\"I'm starting remote work next week and need VPN credentials to access the company network from home\"}" \
  --cli-binary-format raw-in-base64-out \
  response.json

echo ""
echo "Waiting 3 seconds for processing..."
sleep 3

echo ""
echo "Checking CloudWatch logs:"
aws logs tail /aws/lambda/itra-classify-request --since 1m --region us-east-1 --format short | tail -20

echo ""
echo "Checking DynamoDB for classification results:"
aws dynamodb get-item \
  --table-name itra-main-table \
  --region us-east-1 \
  --key "{\"PK\":{\"S\":\"TENANT#$TENANT_ID\"},\"SK\":{\"S\":\"REQ#$REQUEST_ID\"}}" \
  --query 'Item.{Status:status.S,Category:category.S,Severity:severity.N,Team:routing_team.S,Confidence:classification_confidence.N}' \
  --output json
