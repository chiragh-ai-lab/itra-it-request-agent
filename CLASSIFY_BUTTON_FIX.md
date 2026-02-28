# Classification Button Fix - Root Cause Found

## Problem
The "Trigger Classification" button appeared to do nothing when clicked in the deployed Vercel app.

## Root Cause
The `frontend/.env.local` file was missing the required environment variables. It only contained a Vercel OIDC token but was missing:
- `NEXT_PUBLIC_API_ENDPOINT`
- `NEXT_PUBLIC_COGNITO_USER_POOL_ID`
- `NEXT_PUBLIC_COGNITO_CLIENT_ID`
- `NEXT_PUBLIC_AWS_REGION`

Without these variables:
- `API_ENDPOINT` in `api-client.ts` was `undefined`
- All API calls were failing with `fetch(undefined/requests/...)` 
- Errors were likely being caught silently or not displayed
- The button appeared to do nothing because the API calls never reached the backend

## Fix Applied

### 1. Restored Environment Variables
Updated `frontend/.env.local` with the correct values:
```env
NEXT_PUBLIC_AWS_REGION=us-east-1
NEXT_PUBLIC_COGNITO_USER_POOL_ID=us-east-1_ZIncHIiO8
NEXT_PUBLIC_COGNITO_CLIENT_ID=6or5ebop78efpfhtncp0en7vf5
NEXT_PUBLIC_API_ENDPOINT=https://a9b9lfjtn2.execute-api.us-east-1.amazonaws.com/dev
```

### 2. Added Enhanced Debugging
- Added alert() at the start of `handleClassify` to confirm button clicks
- Added comprehensive console logging throughout the flow
- Added a test button to verify basic button functionality

### 3. Added Test Button
Added a simple test button that shows an alert to verify:
- React is working
- Button clicks are being registered
- The issue is specifically with the API calls

## Testing Steps

### Local Testing (if running locally)
1. Ensure `frontend/.env.local` has all the variables
2. Run `npm run dev` in the frontend directory
3. Open http://localhost:3000
4. Navigate to a request with status "submitted"
5. Click "Test Button" - should show alert
6. Click "Trigger Classification" - should show alert and then classify

### Vercel Deployment
The environment variables also need to be set in Vercel dashboard:

1. Go to https://vercel.com/chiragh-qureshi-s-projects/frontend
2. Go to Settings → Environment Variables
3. Add these variables for all environments (Production, Preview, Development):
   - `NEXT_PUBLIC_AWS_REGION` = `us-east-1`
   - `NEXT_PUBLIC_COGNITO_USER_POOL_ID` = `us-east-1_ZIncHIiO8`
   - `NEXT_PUBLIC_COGNITO_CLIENT_ID` = `6or5ebop78efpfhtncp0en7vf5`
   - `NEXT_PUBLIC_API_ENDPOINT` = `https://a9b9lfjtn2.execute-api.us-east-1.amazonaws.com/dev`
4. Redeploy the app (or push a new commit to trigger auto-deploy)

## Why This Happened
The `.env.local` file was likely overwritten by the Vercel CLI when linking the project. The Vercel CLI creates a `.env.local` file with just the OIDC token, replacing any existing content.

## Prevention
1. Never commit `.env.local` to git (it's in `.gitignore`)
2. Always set environment variables in Vercel dashboard for deployed apps
3. Keep `.env.local.example` updated as a reference
4. Document all required environment variables in README

## Next Steps
1. Push these changes to GitHub
2. Verify environment variables are set in Vercel dashboard
3. Wait for Vercel to redeploy
4. Test the classification button
5. Remove the test button once confirmed working

## Files Modified
- `frontend/.env.local` - Restored environment variables
- `frontend/app/requests/[id]/page.tsx` - Added debugging and test button
- `frontend/lib/api-client.ts` - Added comprehensive logging
- `CLASSIFY_BUTTON_FIX.md` - This document
