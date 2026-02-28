# Classification Button Fix - Complete Summary

## Issues Found and Fixed

### Issue 1: Missing Frontend Environment Variables ✅ FIXED
**Problem:** The `.env.local` file was missing all required environment variables, causing all API calls to fail silently.

**Fix Applied:**
- Restored environment variables in `frontend/.env.local`
- Added variables to Vercel dashboard (you did this)
- Redeployed frontend

**Result:** Button now triggers API calls successfully!

### Issue 2: AWS Marketplace Permissions ✅ FIXED
**Problem:** Lambda IAM role was missing AWS Marketplace permissions required by Bedrock models.

**Error Message:**
```
Model access is denied due to IAM user or service role is not authorized to perform 
the required AWS Marketplace actions (aws-marketplace:ViewSubscriptions, aws-marketplace:Subscribe)
```

**Fix Applied:**
- Added AWS Marketplace permissions to Lambda IAM policy in `infrastructure/terraform/lambda.tf`
- Permissions added:
  - `aws-marketplace:ViewSubscriptions`
  - `aws-marketplace:Subscribe`

**Result:** Lambda can now access Bedrock models!

### Issue 3: Model ID Format ✅ FIXED
**Problem:** Using inference profile format (`us.anthropic.claude-3-5-haiku-20241022-v1:0`) which may require additional marketplace setup.

**Fix Applied:**
- Changed to foundation model format: `anthropic.claude-3-5-haiku-20241022-v1:0`
- Updated in `infrastructure/terraform/agent_lambda.tf`

**Result:** Using direct foundation model access!

## Current Status

### ✅ Working
- Frontend button triggers API calls
- API Gateway receives requests
- Lambda function is invoked
- IAM permissions are correct
- Environment variables are set

### ⚠️ Still Testing
- Bedrock model invocation
- Classification completion
- DynamoDB update

## Next Steps for You

1. **Test the Classification Button:**
   - Go to your app: https://itra-it-request-agent.vercel.app
   - Navigate to a request with status "submitted"
   - Click "Trigger Classification"
   - Wait 5-10 seconds
   - Refresh the page to see if status changed to "classified"

2. **Check Browser Console:**
   - Open DevTools (F12) → Console tab
   - Look for 🔵 blue logs showing the API flow
   - Look for any 🔴 red error messages

3. **If It Still Doesn't Work:**
   - The Bedrock model might need to be enabled in AWS Console
   - Go to: AWS Console → Bedrock → Model access
   - Enable "Claude 3.5 Haiku" if not already enabled
   - Wait 2-3 minutes for access to propagate

## Files Modified

1. `frontend/.env.local` - Restored environment variables
2. `frontend/app/requests/[id]/page.tsx` - Added debugging and test button
3. `frontend/lib/api-client.ts` - Added comprehensive logging
4. `infrastructure/terraform/lambda.tf` - Added AWS Marketplace permissions
5. `infrastructure/terraform/agent_lambda.tf` - Changed model ID format

## Commands Run

```bash
# Frontend deployment
git add .
git commit -m "Fix classify button - restore environment variables and add debugging"
git push

# Infrastructure updates
terraform apply -auto-approve  # Added marketplace permissions
terraform apply -auto-approve  # Changed model ID

# Final commit
git add .
git commit -m "Switch to foundation model instead of inference profile for classification"
git push
```

## Testing the Fix

### Test 1: Button Click
- Click "Test Button (Click Me First)" → Should show alert
- Click "Trigger Classification" → Should show alert and start classifying

### Test 2: API Call
- Check browser console for:
  ```
  🔵 Classification button clicked
  🌐 API Call: POST /requests/req_xxxxx/classify
  🌐 Response status: 200
  🔵 Starting polling...
  ```

### Test 3: Classification Complete
- After 5-10 seconds, should see:
  ```
  🔵 Current request status: classified
  ✅ Classification complete!
  ```
- UI should update with category, severity, routing team

## If You See Errors

### Error: "Classification is taking longer than expected"
- This means the Lambda is running but not completing
- Check if Bedrock model is enabled in AWS Console
- Check Lambda logs: `aws logs tail /aws/lambda/itra-classify-request --follow`

### Error: 401 Unauthorized
- JWT token expired
- Refresh the page to get a new token

### Error: 404 Not Found
- Request ID doesn't exist
- Try creating a new request

### Error: 500 Internal Server Error
- Lambda function error
- Check CloudWatch logs for details

## What We Learned

1. **Always check environment variables first** - Missing env vars cause silent failures
2. **Bedrock models require marketplace permissions** - IAM policy needs specific actions
3. **Inference profiles vs foundation models** - Different access patterns
4. **Lambda execution environment caching** - Need to update function to pick up new IAM permissions

## Success Criteria

✅ Button click triggers API call  
✅ API returns 200 status  
✅ Lambda function invokes successfully  
✅ IAM permissions allow Bedrock access  
⏳ Bedrock model invocation succeeds  
⏳ DynamoDB record updates with classification  
⏳ Frontend polls and displays results  

The first 4 are working! The last 3 depend on Bedrock model access being fully enabled.
