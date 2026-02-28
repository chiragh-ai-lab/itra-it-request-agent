# Agent Hooks — Automated Quality Checks

<!--
  These hooks run automatically when files are saved in Kiro IDE.
  They catch the most common bugs BEFORE deployment.
  Add project-specific hooks as you discover new patterns.
-->

## Hook 1: CORS Verification on API Route Changes
**Trigger:** File save in `infrastructure/terraform/*_api.tf`
**Prompt:** For every new API method module in this file, verify:
1. A corresponding CORS module exists for the same resource
2. api_gateway.tf has been updated in ALL 4 sections (resource triggers, method triggers, CORS triggers, depends_on)
List any missing configurations with exact file locations and line numbers.

## Hook 2: Decimal Conversion Check on Lambda Changes
**Trigger:** File save in `backend/functions/*.py`
**Prompt:** Scan this Lambda function for:
1. Any DynamoDB responses (table.query, table.get_item, table.scan) that are included in the HTTP response body
2. Verify that `convert_decimals()` (or equivalent) is applied to ALL response data before `json.dumps()`
3. Check for any `float()` values being written to DynamoDB (should use `Decimal(str(value))` instead)
Flag any path where Decimal objects might leak into JSON responses or float values might be written to DynamoDB.

## Hook 3: S3 SigV4 Check
**Trigger:** File save in `backend/functions/*.py`
**Prompt:** If this Lambda creates an S3 client (`boto3.client('s3')`), verify it includes `config=Config(signature_version='s3v4')`. Flag any S3 client instantiation missing SigV4 configuration.

## Hook 4: S3 Skip List Check
**Trigger:** File save in S3 event-triggered Lambda files
**Prompt:** Verify that all internal S3 paths (exports, agent-logs) are in the processing skip list. Cross-reference with the S3 path structure defined in coding-standards.md steering file. Flag any paths that could trigger infinite processing loops.

## Hook 5: Tenant Isolation Check
**Trigger:** File save in `backend/functions/*.py`
**Prompt:** Verify that:
1. `get_tenant_id(event)` (or equivalent) is called to extract tenant_id from JWT claims
2. ALL DynamoDB queries use `PK = TENANT#{tenant_id}` (or equivalent tenant-scoped key)
3. ALL S3 paths include `{tenant_id}/` prefix
Flag any DynamoDB query or S3 operation that does not enforce tenant isolation.

## Hook 6: API Gateway Timeout Check
**Trigger:** File save in `backend/functions/*.py`
**Prompt:** If this Lambda function calls Bedrock, processes files, or performs multi-step operations that could exceed 29 seconds:
1. Verify it uses the async self-invocation pattern (return immediately, process in background)
2. Check that the Lambda timeout in Terraform is set appropriately (>30s for background processors)
3. Verify frontend has polling logic for async operations
Flag any Lambda that might exceed API Gateway's 29-second timeout.

## Hook 7: itra- Prefix Check
**Trigger:** File save in `infrastructure/terraform/*.tf`
**Prompt:** Verify ALL AWS resource names use the `itra-` prefix. Check:
1. S3 bucket names start with `itra-`
2. DynamoDB table name starts with `itra-`
3. Lambda function names start with `itra-`
4. API Gateway name starts with `itra-`
5. Cognito user pool name starts with `itra-`
6. IAM role names start with `itra-`
Flag any resource missing the prefix — this prevents collisions with proc- and vrfq- apps in the same account.

## Hook 8: Model ID Hardcode Check
**Trigger:** File save in `backend/functions/*.py`
**Prompt:** Scan for any hardcoded Bedrock model IDs (strings containing "anthropic.claude" or "us.anthropic"). All model IDs MUST come from environment variables via `get_model_id()` or `os.environ.get()`. Flag any hardcoded model strings.
