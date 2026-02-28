# Test the classification API endpoint
$API_ENDPOINT = "https://a9b9lfjtn2.execute-api.us-east-1.amazonaws.com/dev"
$REQUEST_ID = "req_82f1fefa803d"

# You need to get a real JWT token from Cognito
# For now, let's check the Lambda logs to see what's happening

Write-Host "Checking recent Lambda invocations..."
aws logs tail /aws/lambda/itra-classify-request --since 30m --region us-east-1 --format short | Select-String -Pattern "Error|Classification|START|END" | Select-Object -Last 20
