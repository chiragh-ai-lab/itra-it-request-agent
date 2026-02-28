#!/bin/bash

# Test script to manually trigger classification and check logs
# Usage: ./test-classification.sh <request-id> <id-token>

REQUEST_ID=$1
ID_TOKEN=$2
API_ENDPOINT="https://a9b9lfjtn2.execute-api.us-east-1.amazonaws.com/dev"

if [ -z "$REQUEST_ID" ] || [ -z "$ID_TOKEN" ]; then
  echo "Usage: ./test-classification.sh <request-id> <id-token>"
  echo ""
  echo "To get your ID token:"
  echo "1. Open browser DevTools (F12)"
  echo "2. Go to Console tab"
  echo "3. Run: (await fetchAuthSession()).tokens.idToken.toString()"
  echo "4. Copy the token"
  exit 1
fi

echo "Triggering classification for request: $REQUEST_ID"
echo ""

# Trigger classification
RESPONSE=$(curl -s -X POST \
  "$API_ENDPOINT/requests/$REQUEST_ID/classify" \
  -H "Authorization: $ID_TOKEN" \
  -H "Content-Type: application/json")

echo "API Response:"
echo "$RESPONSE"
echo ""

# Wait a bit
echo "Waiting 5 seconds for classification to complete..."
sleep 5

# Check request status
echo ""
echo "Checking request status:"
curl -s -X GET \
  "$API_ENDPOINT/requests/$REQUEST_ID" \
  -H "Authorization: $ID_TOKEN" \
  -H "Content-Type: application/json" | jq '.'

echo ""
echo "To check CloudWatch logs:"
echo "aws logs tail /aws/lambda/itra-classify-request --follow --region us-east-1"
