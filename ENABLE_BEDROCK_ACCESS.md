# Enable Bedrock Model Access

The classification feature requires access to Claude models in AWS Bedrock.

## Steps to Enable Model Access:

1. **Open AWS Console**: https://console.aws.amazon.com/bedrock/
2. **Go to Model Access**: Click "Model access" in the left sidebar
3. **Request Access**: Click "Manage model access" or "Edit"
4. **Select Models**: Check the boxes for:
   - **Anthropic Claude 3 Haiku** (recommended for classification - fast and cheap)
   - **Anthropic Claude 3.5 Sonnet v2** (recommended for chat - best quality)
   - OR **Anthropic Claude 3 Sonnet** (fallback if others unavailable)
5. **Submit Request**: Click "Request model access" or "Save changes"
6. **Wait**: Access is usually granted immediately, but can take a few minutes

## After Enabling Access:

The classification feature will work automatically. No code changes needed.

## Current Issue:

Your AWS account shows these errors:
- Claude 3 Haiku: "Model access is denied due to IAM user or service role is not authorized to perform the required AWS Marketplace actions"
- Claude 3 Sonnet: "Access denied. This Model is marked by provider as Legacy"
- Claude 3.5 Sonnet v1: "Access denied. This Model is marked by provider as Legacy"  
- Claude 3.5 Sonnet v2: "Invocation of model ID with on-demand throughput isn't supported"

This means you need to enable model access through the Bedrock console.

## Alternative: Use a Different Region

If model access is not available in us-east-1, you could:
1. Change the region in `infrastructure/terraform/variables.tf`
2. Redeploy everything to a region where you have model access
