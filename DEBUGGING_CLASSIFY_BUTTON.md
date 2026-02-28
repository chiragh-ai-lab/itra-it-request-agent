# Debugging the "Trigger Classification" Button

## Problem
The "Trigger Classification" button in the frontend doesn't appear to do anything when clicked, even though the classification works perfectly via CLI.

## What I've Added

### 1. Enhanced Frontend Logging
I've added comprehensive console logging to both files:

**`frontend/app/requests/[id]/page.tsx`** - The `handleClassify` function now logs:
- 🔵 When button is clicked
- 🔵 Request ID being used
- 🔵 API call initiation
- 🔵 API response
- 🔵 Polling attempts and status checks
- ✅ Success messages with classification results
- 🔴 Any errors that occur

**`frontend/lib/api-client.ts`** - The `apiCall` function now logs:
- 🌐 Every API call (method + path)
- 🌐 Full URL being called
- 🌐 Whether auth token exists
- 🌐 Response status
- 🌐 Response data
- 🌐 Any API errors

### 2. Test Tools

**`test-classify-frontend.sh`** - Bash script to test the classify endpoint with a real JWT token
```bash
./test-classify-frontend.sh <request_id> <jwt_token>
```

**`frontend/test-classify.html`** - Standalone HTML page to test classification without Next.js
- Open this file in a browser
- Enter your request ID
- Paste your JWT token (get from browser console)
- Click "Trigger Classification"
- Watch the detailed logs

## How to Debug

### Step 1: Check Browser Console
1. Open your app in the browser
2. Open DevTools (F12)
3. Go to the Console tab
4. Click "Trigger Classification" button
5. Look for the 🔵 blue logs

**What you should see:**
```
🔵 Classification button clicked
🔵 Request ID: req_xxxxx
🌐 API Call: POST /requests/req_xxxxx/classify
🌐 Full URL: https://a9b9lfjtn2.execute-api.us-east-1.amazonaws.com/dev/requests/req_xxxxx/classify
🌐 Has token: true
🌐 Response status: 200 OK
🌐 Response data: { message: "Classification started", request_id: "req_xxxxx" }
🔵 Starting polling for classification completion...
🔵 Poll attempt 1/15
🔵 Current request status: submitted
🔵 Poll attempt 2/15
🔵 Current request status: classified
🔵 Classification complete or timeout reached
✅ Classification complete! Check the Details section for results.
```

**If you see nothing:**
- The button click handler is not firing
- Check if there's a JavaScript error preventing the code from running
- Check if the button is actually calling `handleClassify`

**If you see errors:**
- Look for 🔴 red error messages
- Check the error details
- Common issues:
  - 401 Unauthorized: JWT token expired or invalid
  - 404 Not Found: Request ID doesn't exist or wrong API endpoint
  - 500 Internal Server Error: Lambda function error

### Step 2: Use the Test HTML Page
1. Open `frontend/test-classify.html` in a browser
2. Get your JWT token from the main app's browser console:
   ```javascript
   (await Auth.currentSession()).getIdToken().getJwtToken()
   ```
3. Copy the token
4. Paste it into the test page along with a request ID
5. Click "Trigger Classification"
6. Watch the detailed logs

This bypasses Next.js entirely and tests the raw API call.

### Step 3: Test with CLI
```bash
# Get a JWT token from browser console first
JWT_TOKEN="your_token_here"
REQUEST_ID="req_xxxxx"

# Test the classify endpoint
curl -X POST "https://a9b9lfjtn2.execute-api.us-east-1.amazonaws.com/dev/requests/$REQUEST_ID/classify" \
  -H "Content-Type: application/json" \
  -H "Authorization: $JWT_TOKEN" \
  -v

# Wait a few seconds, then check the request status
curl -X GET "https://a9b9lfjtn2.execute-api.us-east-1.amazonaws.com/dev/requests/$REQUEST_ID" \
  -H "Authorization: $JWT_TOKEN"
```

### Step 4: Check Lambda Logs
```bash
# Check classify Lambda logs
aws logs tail /aws/lambda/itra-classify-request --follow

# Look for:
# - "Classification started" message
# - "Classification complete for req_xxxxx" message
# - Any error messages
```

## Common Issues and Solutions

### Issue 1: Button Click Does Nothing
**Symptoms:** No console logs at all when clicking the button

**Possible causes:**
- JavaScript error preventing code execution
- Button not properly wired to `handleClassify`
- React state issue preventing re-render

**Solution:**
- Check browser console for any JavaScript errors
- Verify the button's `onClick` prop: `onClick={handleClassify}`
- Check if `classifying` state is stuck in `true`

### Issue 2: API Call Fails with 401
**Symptoms:** 🌐 Response status: 401 Unauthorized

**Possible causes:**
- JWT token expired (tokens expire after 1 hour)
- Token not being sent correctly
- Cognito authorizer misconfigured

**Solution:**
- Refresh the page to get a new token
- Check if token is in the Authorization header
- Verify Cognito User Pool ID and Client ID in `.env.local`

### Issue 3: API Call Fails with 404
**Symptoms:** 🌐 Response status: 404 Not Found

**Possible causes:**
- Request ID doesn't exist
- Wrong API endpoint URL
- API Gateway not deployed

**Solution:**
- Verify the request ID exists in DynamoDB
- Check `NEXT_PUBLIC_API_ENDPOINT` in `.env.local`
- Redeploy API Gateway: `cd infrastructure/terraform && terraform apply`

### Issue 4: Classification Never Completes
**Symptoms:** Polling continues for 30 seconds, status stays "submitted"

**Possible causes:**
- Lambda function error during classification
- Bedrock model access denied
- DynamoDB update failed

**Solution:**
- Check Lambda logs: `aws logs tail /aws/lambda/itra-classify-request --follow`
- Verify Bedrock model access in AWS Console
- Check IAM permissions for Lambda role

### Issue 5: Classification Completes but UI Doesn't Update
**Symptoms:** Status changes to "classified" in DynamoDB but UI still shows "submitted"

**Possible causes:**
- Polling stopped too early
- React state not updating
- API response not being processed

**Solution:**
- Refresh the page manually
- Check if `setRequest(data.request)` is being called
- Verify the polling interval is running

## Next Steps

1. **Deploy the changes**: The enhanced logging is already committed and pushed. Vercel should auto-deploy.

2. **Test with a new request**:
   - Create a new request in the app
   - Open browser DevTools Console
   - Click "Trigger Classification"
   - Watch the console logs

3. **Share the logs**: If it still doesn't work, copy ALL the console logs (🔵 and 🔴 messages) and share them.

4. **Try the test HTML page**: If the main app doesn't work, try `frontend/test-classify.html` to isolate the issue.

## Expected Behavior

When everything works correctly:
1. Click "Trigger Classification" button
2. Button text changes to "Classifying..."
3. Console shows API call logs
4. After 2-10 seconds, you see "Classification complete!" alert
5. UI updates to show:
   - Status badge changes to "classified"
   - Category appears in Details section
   - Severity appears in Details section
   - Routing Team appears in Details section
   - Classification Confidence appears in Details section

## Files Modified

- `frontend/app/requests/[id]/page.tsx` - Added detailed logging to `handleClassify`
- `frontend/lib/api-client.ts` - Added detailed logging to `apiCall`
- `test-classify-frontend.sh` - CLI test script
- `frontend/test-classify.html` - Standalone test page
- `DEBUGGING_CLASSIFY_BUTTON.md` - This guide
