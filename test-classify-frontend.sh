#!/bin/bash

# Test the classify endpoint with a real JWT token
# Usage: ./test-classify-frontend.sh <request_id> <jwt_token>

REQUEST_ID=$1
JWT_TOKEN=$2
API_ENDPOINT="https://a9b9lfjtn2.execute-api.us-east-1.amazonaws.com/dev"

if [ -z "$REQUEST_ID" ] || [ -z "$JWT_TOKEN" ]; then
  echo "Usage: ./test-classify-frontend.sh <request_id> <jwt_token>"
  echo ""
  echo "To get your JWT token:"
  echo "1. Open browser DevTools (F12)"
  echo "2. Go to Console tab"
  echo "3. Run: (await Auth.currentSession()).getIdToken().getJwtToken()"
  echo "4. Copy the token"
  exit 1
fi

echo "Testing classify endpoint..."
echo "Request ID: $REQUEST_ID"
echo "API Endpoint: $API_ENDPOINT/requests/$REQUEST_ID/classify"
echo ""

curl -X POST "$API_ENDPOINT/requests/$REQUEST_ID/classify" \
  -H "Content-Type: application/json" \
  -H "Authorization: $JWT_TOKEN" \
  -v

echo ""
echo ""
echo "If you see 'Classification started', the endpoint is working!"
echo "Now check the request status after a few seconds:"
echo ""
echo "curl -X GET \"$API_ENDPOINT/requests/$REQUEST_ID\" \\"
echo "  -H \"Authorization: $JWT_TOKEN\""
