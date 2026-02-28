---
inclusion: auto
fileMatchPattern: "**/*bedrock*|**/*lambda*|**/*agent*"
---

# AWS Bedrock Troubleshooting Guide

## CRITICAL: Inference Profiles Required for On-Demand Access

**Always use inference profiles (with `us.` prefix) for AWS Bedrock models, NOT direct model IDs.**

### ❌ WRONG - Direct Model IDs
```python
# These will fail with "on-demand throughput isn't supported"
CLASSIFICATION_MODEL = "anthropic.claude-3-5-haiku-20241022-v1:0"
CHAT_MODEL = "anthropic.claude-3-7-sonnet-20250219-v1:0"
```

### ✅ CORRECT - Inference Profiles
```python
# Use the us. prefix for cross-region inference profiles
CLASSIFICATION_MODEL = "us.anthropic.claude-3-5-haiku-20241022-v1:0"
CHAT_MODEL = "us.anthropic.claude-sonnet-4-5-20250514-v1:0"
ACTION_MODEL = "us.anthropic.claude-sonnet-4-5-20250514-v1:0"
```

## Common Bedrock Errors and Solutions

### Error: "on-demand throughput isn't supported"
**Cause:** Using direct model ID instead of inference profile
**Solution:** Add `us.` prefix to model ID

### Error: "Model access is denied due to IAM user or service role is not authorized to perform the required AWS Marketplace actions"
**Cause:** Missing AWS Marketplace permissions in IAM policy
**Solution:** Add these permissions to Lambda IAM role:
```json
{
  "Effect": "Allow",
  "Action": [
    "aws-marketplace:ViewSubscriptions",
    "aws-marketplace:Subscribe"
  ],
  "Resource": "*"
}
```

### Error: "AccessDeniedException" when calling InvokeModel
**Cause:** Model not enabled in AWS Bedrock console
**Solution:** 
1. Go to AWS Console → Bedrock → Model access
2. Enable the required models (Claude 3.5 Haiku, Claude Sonnet 4.5, etc.)
3. Wait 2-3 minutes for access to propagate

## Bedrock IAM Policy Template

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/*",
        "arn:aws:bedrock:*:${account_id}:inference-profile/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "aws-marketplace:ViewSubscriptions",
        "aws-marketplace:Subscribe"
      ],
      "Resource": "*"
    }
  ]
}
```

## Model Selection Guide

### For Classification (Fast + Cheap)
- **Model:** Claude 3.5 Haiku
- **ID:** `us.anthropic.claude-3-5-haiku-20241022-v1:0`
- **Use Case:** Intent classification, category detection, simple analysis
- **Cost:** ~10x cheaper than Sonnet

### For Chat/Reasoning (Best Quality)
- **Model:** Claude Sonnet 4.5
- **ID:** `us.anthropic.claude-sonnet-4-5-20250514-v1:0`
- **Use Case:** Multi-turn conversations, complex reasoning, agent actions
- **Cost:** Higher but better quality

### For Agent Actions (Balanced)
- **Model:** Claude Sonnet 4.5
- **ID:** `us.anthropic.claude-sonnet-4-5-20250514-v1:0`
- **Use Case:** Decision making, policy evaluation, action execution

## Bedrock Client Configuration

Always configure the Bedrock client with explicit region:

```python
import boto3
from botocore.config import Config

def get_bedrock_client():
    """Get Bedrock client with proper configuration"""
    return boto3.client(
        'bedrock-runtime',
        region_name='us-east-1',  # Explicit region required
        config=Config(
            retries={'max_attempts': 3, 'mode': 'adaptive'}
        )
    )
```

## Testing Bedrock Access

### Test 1: Check Model Access
```bash
aws bedrock list-foundation-models --region us-east-1
```

### Test 2: Test Inference Profile
```bash
aws bedrock-runtime invoke-model \
  --model-id us.anthropic.claude-3-5-haiku-20241022-v1:0 \
  --body '{"anthropic_version":"bedrock-2023-05-31","max_tokens":100,"messages":[{"role":"user","content":"Hello"}]}' \
  --region us-east-1 \
  response.json
```

### Test 3: Check IAM Permissions
```bash
aws iam get-role-policy \
  --role-name itra-lambda-role \
  --policy-name itra-lambda-bedrock-policy
```

## Debugging Checklist

When Bedrock calls fail, check in this order:

1. ✅ **Model ID Format** - Does it have `us.` prefix?
2. ✅ **IAM Permissions** - Does role have bedrock:InvokeModel and marketplace permissions?
3. ✅ **Model Access** - Is model enabled in Bedrock console?
4. ✅ **Region Configuration** - Is client using correct region (us-east-1)?
5. ✅ **Request Format** - Is the request body valid JSON with required fields?
6. ✅ **Lambda Timeout** - Is timeout sufficient (120s recommended)?
7. ✅ **CloudWatch Logs** - Check logs for detailed error messages

## Cost Optimization

- Use Haiku for simple tasks (classification, extraction)
- Use Sonnet for complex reasoning (chat, agent actions)
- Set `max_tokens` explicitly to cap costs
- Monitor via CloudWatch metrics
- Set billing alerts at $10, $50, $100

## Reference Links

- [AWS Bedrock Model IDs](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html)
- [Inference Profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html)
- [IAM Permissions](https://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html)
- [Pricing](https://aws.amazon.com/bedrock/pricing/)

## Lessons Learned

1. **Always use inference profiles** - Direct model IDs don't support on-demand access
2. **Check error messages carefully** - "on-demand throughput" error means wrong model ID format
3. **Enable models first** - Access must be enabled in Bedrock console before use
4. **Add marketplace permissions** - Required for some models even if not obvious
5. **Test with CLI first** - Faster to debug IAM/access issues before coding
