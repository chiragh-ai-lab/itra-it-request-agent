# AWS Serverless Coding Standards & Pitfall Prevention

<!--
  \u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557
  \u2551  THIS FILE IS THE MOST IMPORTANT FILE IN THE STARTER KIT.      \u2551
  \u2551                                                                  \u2551
  \u2551  Every pattern here was learned the hard way through real        \u2551
  \u2551  production debugging. DO NOT remove patterns unless you are     \u2551
  \u2551  100% certain they don't apply to your project.                  \u2551
  \u2551                                                                  \u2551
  \u2551  These patterns prevent 90%+ of AWS serverless deployment bugs.  \u2551
  \u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d
-->

---

## \ud83d\udd34 CRITICAL: CORS Configuration (90% of deployment issues!)

**This is the #1 cause of failed deployments in API Gateway + Lambda architectures.**

ALWAYS follow when adding ANY API endpoint:

1. Add CORS module (OPTIONS method) for every new API resource in Terraform
2. Update ALL 4 sections in `api_gateway.tf`:
   - Resource in `triggers` block
   - Method in `triggers` block
   - CORS in `triggers` block
   - Method + CORS in `depends_on` list
3. Test CORS BEFORE browser testing:
   ```bash
   curl -X OPTIONS https://your-api/endpoint \
     -H "Origin: https://your-frontend.com" \
     -H "Access-Control-Request-Method: POST" -v
   ```
4. If CORS fails after terraform apply: the API Gateway deployment may be cached. Delete and recreate the deployment stage.

**Reusable Terraform modules:**
- Create `modules/api_method/` \u2014 reusable API Gateway method pattern
- Create `modules/api_cors/` \u2014 reusable CORS OPTIONS pattern
- Use these for EVERY endpoint to ensure consistency

**Lambda CORS headers (include in EVERY response):**
```python
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',  # Or your specific domain
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,PATCH,DELETE,OPTIONS'
}

def response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': CORS_HEADERS,
        'body': json.dumps(body)
    }
```

---

## \ud83d\udd34 CRITICAL: DynamoDB Decimal/Float Handling

**DynamoDB stores numbers as Decimal. JavaScript/React cannot render Decimal objects.**

ALWAYS use recursive conversion in ALL Lambda responses:

```python
from decimal import Decimal

def convert_decimals(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    return obj

# Use in EVERY Lambda response
return response(200, convert_decimals(data))
```

**For writes to DynamoDB:**
```python
# WRONG: DynamoDB rejects float
table.put_item(Item={'price': 29.99})

# CORRECT: Convert to Decimal via string
table.put_item(Item={'price': Decimal(str(29.99))})
```

**For PDF/Excel generation (reportlab, openpyxl):**
```python
# These libraries require float, not Decimal
# Create SEPARATE data structures
pdf_data = [{'price': float(item['price'])} for item in items]
db_data = [{'price': Decimal(str(item['price']))} for item in items]
```

---

## \ud83d\udd34 CRITICAL: S3 KMS Encryption \u2014 Signature Version 4

**If your S3 bucket uses KMS encryption (it should), ALL S3 operations will fail without SigV4.**

```python
from botocore.config import Config

# ALWAYS configure SigV4 for KMS-encrypted buckets
s3 = boto3.client('s3', config=Config(signature_version='s3v4'))
```

This applies to: presigned URLs, uploads, downloads, copies \u2014 every S3 operation.

**Symptom if missing:** XML error "Requests specifying Server Side Encryption with AWS KMS managed keys require AWS Signature Version 4"

---

## \ud83d\udd34 CRITICAL: API Gateway 29-Second Timeout

**API Gateway has a HARD 29-second timeout that cannot be increased.**

For any operation that might exceed 29 seconds (large file processing, multi-step AI pipelines, batch operations):

**Pattern: Async Lambda Self-Invocation**
```python
import boto3, json

def handler(event, context):
    mode = event.get('mode')
    
    if mode == 'process':
        # Background processing (no timeout concern)
        do_heavy_work()
        return
    
    # API Gateway handler \u2014 return immediately
    set_status_in_dynamodb('processing')
    
    # Invoke self asynchronously
    lambda_client = boto3.client('lambda')
    lambda_client.invoke(
        FunctionName=context.function_name,
        InvocationType='Event',  # Async \u2014 fire and forget
        Payload=json.dumps({**event, 'mode': 'process'})
    )
    
    return response(200, {'status': 'processing', 'message': 'Check back shortly'})
```

**Frontend polling pattern:**
```typescript
const pollForCompletion = async (id: string) => {
  const interval = setInterval(async () => {
    const result = await getStatus(id);
    if (result.status !== 'processing') {
      clearInterval(interval);
      updateUI(result);
    }
  }, 2000); // Poll every 2 seconds
};
```

**Lambda config for heavy processing:**
```hcl
resource "aws_lambda_function" "heavy_processor" {
  memory_size = 2048   # Increase from default 128MB
  timeout     = 300    # 5 minutes (Lambda max is 900s)
}
```

---

## \ud83d\udd34 CRITICAL: Terraform State & Deployment

### API Gateway Not Redeploying
**Symptom:** Code changes don't take effect after `terraform apply`
**Cause:** Lambda zip hash unchanged or API Gateway cache
**Fix:**
```bash
rm backend/lambda_functions.zip    # Force rebuild
terraform apply -auto-approve
```

### Manual Console Changes Get Wiped
**NEVER make manual changes in AWS Console.** `terraform apply` will overwrite them.
Everything must be in `.tf` files.

### State Lock Issues
**Symptom:** "Error acquiring the state lock"
**Fix:**
```bash
terraform force-unlock <LOCK_ID>   # Only if no other operation is running
```

---

## \ud83d\udfe1 IMPORTANT: DynamoDB Single-Table Design Patterns

### Key Structure (Tenant Isolation)
```
PK: TENANT#{tenant_id}
SK: {ENTITY_TYPE}#{entity_id}
```

### GSI Patterns
```
GSI1PK: TENANT#{tenant_id}#{ENTITY_TYPE}    # Query all entities of a type
GSI1SK: {timestamp} or {parent_id}#{timestamp}  # Sort by time or group by parent
```

### Tenant Isolation (Enforce in EVERY Lambda)
```python
def get_tenant_id(event):
    """Extract tenant_id from Cognito JWT \u2014 use this for ALL DynamoDB operations"""
    claims = event['requestContext']['authorizer']['claims']
    return claims['sub']  # Or custom claim

# EVERY query must be scoped to tenant
response = table.query(
    KeyConditionExpression=Key('PK').eq(f'TENANT#{tenant_id}')
)
```

---

## \ud83d\udfe1 IMPORTANT: S3 Path Organization & Skip Lists

### Standard Path Structure
```
{tenant_id}/
\u251c\u2500\u2500 uploads/           # User uploads (may trigger processing)
\u251c\u2500\u2500 exports/           # Generated exports (Excel, PDF)
\u251c\u2500\u2500 generated/         # AI-generated content
\u2514\u2500\u2500 internal/          # System files
```

### Extraction/Processing Skip List
If S3 events trigger Lambda processing (e.g., document extraction), maintain a skip list:
```python
SKIP_PREFIXES = ['/exports/', '/generated/', '/internal/']

def should_skip(s3_key):
    return any(prefix in s3_key for prefix in SKIP_PREFIXES)
```

**Why:** Without this, generated files trigger re-processing in infinite loops.

---

## \ud83d\udfe1 IMPORTANT: Lambda Response Pattern

Standard Lambda response structure (use for ALL functions):

```python
import json
from decimal import Decimal

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,PATCH,DELETE,OPTIONS'
}

def convert_decimals(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    return obj

def success(body, status_code=200):
    return {
        'statusCode': status_code,
        'headers': CORS_HEADERS,
        'body': json.dumps(convert_decimals(body))
    }

def error(message, status_code=400):
    return {
        'statusCode': status_code,
        'headers': CORS_HEADERS,
        'body': json.dumps({'error': message})
    }

def get_tenant_id(event):
    return event['requestContext']['authorizer']['claims']['sub']

def handler(event, context):
    try:
        tenant_id = get_tenant_id(event)
        # ... your logic ...
        return success({'data': result})
    except Exception as e:
        print(f"Error: {str(e)}")
        return error(str(e), 500)
```

---

## \ud83d\udfe1 IMPORTANT: Presigned URL Pattern

For file uploads/downloads through S3:

```python
def generate_presigned_url(bucket, key, operation='put_object', expiry=3600):
    s3 = boto3.client('s3', config=Config(signature_version='s3v4'))
    url = s3.generate_presigned_url(
        ClientMethod=operation,
        Params={'Bucket': bucket, 'Key': key},
        ExpiresIn=expiry  # 1 hour default
    )
    return url
```

**Frontend upload pattern:**
```typescript
// 1. Get presigned URL from your API
const { upload_url, file_key } = await getUploadUrl(filename);

// 2. Upload directly to S3 (bypasses Lambda/API Gateway size limits)
await fetch(upload_url, {
  method: 'PUT',
  body: file,
  headers: { 'Content-Type': file.type }
});
```

---

## \ud83d\udfe1 IMPORTANT: Next.js Dual Deployment (If Using Next.js)

**Only applies if deploying to BOTH Vercel (SSR) AND S3/CloudFront (static).**

- `next.config.js` must conditionally set `output: 'export'`:
  ```javascript
  const nextConfig = {
    ...(process.env.VERCEL ? {} : { output: 'export' })
  };
  ```
- All `[id]` pages need `generateStaticParams()` returning `[]`
- Dynamic route pages split into: server wrapper (page.tsx) + client component (*Client.tsx)
- CloudFront Function rewrites dynamic URLs to placeholder pages
- `patch-package` may be needed for Next.js static export bugs
- NEVER add `output: 'export'` unconditionally \u2014 it breaks Vercel SSR

**If deploying to Vercel only:** Ignore all of the above. SSR handles everything natively.

---

## \ud83d\udfe1 IMPORTANT: SES Email Configuration

- Sandbox mode: Can only send to verified email addresses
- Production mode: Request access via AWS Console (24-hour approval)
- Always verify sender address first
- Use multipart MIME (HTML + plain text fallback) for deliverability
- SES IAM permissions: `ses:SendEmail`, `ses:SendRawEmail`

---

## \ud83d\udfe2 GOOD PRACTICE: Error Handling in Lambda

```python
# Always catch specific exceptions first
try:
    result = table.get_item(Key={'PK': pk, 'SK': sk})
    item = result.get('Item')
    if not item:
        return error('Item not found', 404)
    return success(item)
except ClientError as e:
    error_code = e.response['Error']['Code']
    if error_code == 'ConditionalCheckFailedException':
        return error('Conflict: item already exists', 409)
    raise  # Re-raise unexpected errors
except Exception as e:
    print(f"Unexpected error: {str(e)}")
    return error('Internal server error', 500)
```

---

## \ud83d\udfe2 GOOD PRACTICE: Bedrock AI Cost Control

- Use Haiku for simple classification tasks (10x cheaper than Sonnet)
- Use Sonnet only for complex extraction/analysis requiring reasoning
- Set `max_tokens` explicitly to cap output cost
- Monitor via CloudWatch: set billing alerts at $10, $50, $100
- Output tokens cost 5x more than input tokens \u2014 design prompts for concise responses
- Consider Batch API (50% discount) for non-real-time processing

---

## \ud83d\udfe2 GOOD PRACTICE: Frontend API Client Pattern

```typescript
const API_ENDPOINT = process.env.NEXT_PUBLIC_API_ENDPOINT;

async function apiCall(path: string, options: RequestInit = {}) {
  const session = await Auth.currentSession();
  const token = session.getIdToken().getJwtToken();
  
  const response = await fetch(`${API_ENDPOINT}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token,
      ...options.headers,
    },
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'API call failed');
  }
  
  return response.json();
}

// Usage
const projects = await apiCall('/projects');
const result = await apiCall('/projects', {
  method: 'POST',
  body: JSON.stringify({ name: 'New Project' }),
});
```

---

## Quick Reference: Common Symptoms \u2192 Fixes

| Symptom | Cause | Fix |
|---------|-------|-----|
| CORS error in browser | Missing OPTIONS method or API Gateway not redeployed | Add CORS module + update all 4 sections in api_gateway.tf |
| "[object Object]" in React | Decimal not converted to float | Add `convert_decimals()` to Lambda response |
| S3 XML signature error | Missing SigV4 for KMS bucket | Add `Config(signature_version='s3v4')` |
| Lambda timeout | Default 3s too short | Increase timeout in Terraform; use async pattern for >29s |
| Code changes not taking effect | Stale Lambda zip | Delete zip file, re-run terraform apply |
| Terraform state lock | Interrupted previous run | `terraform force-unlock <LOCK_ID>` |
| Generated files triggering processing | Missing S3 path skip list | Add path to skip list in processing Lambda |
| Email sending fails | SES sandbox mode | Verify recipients or request production access |
| DynamoDB "Float not supported" | Using float instead of Decimal | Convert via `Decimal(str(value))` |
| Frontend auth errors | Expired/missing JWT token | Check Cognito session refresh logic |
