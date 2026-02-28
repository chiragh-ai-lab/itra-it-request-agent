# Design: AWS Serverless Infrastructure

## Architecture Diagram

```
Frontend (Vercel / S3+CloudFront / Netlify)
    \u2502
    \u25bc
API Gateway (REST) \u2500\u2500\u2500 Cognito JWT Authorizer
    \u2502
    \u25bc
Lambda Functions (Python 3.12)
    \u2502
    \u251c\u2500\u2500 DynamoDB (single-table, tenant-isolated)
    \u251c\u2500\u2500 S3 (KMS encrypted, organized paths)
    \u251c\u2500\u2500 Bedrock (AI features \u2014 optional)
    \u2514\u2500\u2500 SES (email \u2014 optional)
```

## DynamoDB Schema Template

<!--
  Replace ENTITY_A, ENTITY_B with your actual entity types.
  Add/remove GSIs as needed. GSI1 (entity type query) is almost always needed.
-->

| Entity | PK | SK | GSI1PK | GSI1SK |
|--------|----|----|--------|--------|
| Entity A | TENANT#{tid} | ENTITY_A#{id} | TENANT#{tid}#ENTITY_A | {timestamp} |
| Entity B | TENANT#{tid} | ENTITY_B#{id} | TENANT#{tid}#ENTITY_B | {timestamp} |
| Child of A | TENANT#{tid} | CHILD_B#{parent_id}#{id} | ENTITY_A#{parent_id} | {timestamp} |

## Terraform Module Structure

```
infrastructure/terraform/
\u251c\u2500\u2500 main.tf                 # Provider, S3 backend for state
\u251c\u2500\u2500 variables.tf            # Input variables
\u251c\u2500\u2500 outputs.tf              # API endpoint, Cognito IDs
\u251c\u2500\u2500 dynamodb.tf             # Single table + GSIs
\u251c\u2500\u2500 s3.tf                   # Bucket with KMS encryption
\u251c\u2500\u2500 cognito.tf              # User pool + app client
\u251c\u2500\u2500 lambda.tf               # Lambda functions + shared IAM role
\u251c\u2500\u2500 api_gateway.tf          # REST API + Cognito authorizer + deployment
\u251c\u2500\u2500 [feature]_api.tf        # Feature-specific API routes (one per feature)
\u251c\u2500\u2500 [feature]_lambda.tf     # Feature-specific Lambdas (if many)
\u251c\u2500\u2500 cloudfront.tf           # Optional: static frontend distribution
\u251c\u2500\u2500 ses.tf                  # Optional: email configuration
\u2514\u2500\u2500 modules/
    \u251c\u2500\u2500 api_method/         # Reusable API Gateway method
    \u2514\u2500\u2500 api_cors/           # Reusable CORS OPTIONS method
```

## Lambda Shared Utilities

Create `backend/functions/utils.py` with standard patterns:
- `convert_decimals()` \u2014 recursive Decimal to float
- `success()` / `error()` \u2014 standard response with CORS headers
- `get_tenant_id()` \u2014 extract from JWT claims
- `get_s3_client()` \u2014 preconfigured with SigV4

## Security Model

- Cognito JWT \u2192 tenant_id in claims
- Every Lambda scoped to `PK = TENANT#{tenant_id}`
- S3 paths prefixed with tenant_id
- KMS encryption at rest
- API Gateway Cognito authorizer on all endpoints

---

# Tasks: AWS Serverless Infrastructure

## Task 1: Terraform Foundation
- [ ] Create `main.tf` with AWS provider and S3 backend
- [ ] Create `variables.tf` (project_name, region, environment)
- [ ] Create `outputs.tf` (API endpoint, Cognito IDs, CloudFront domain)

## Task 2: DynamoDB
- [ ] Create table with PK (String) + SK (String) composite key
- [ ] Add GSI1 for entity type queries (GSI1PK + GSI1SK)
- [ ] Add additional GSIs as needed for query patterns
- [ ] Set billing to PAY_PER_REQUEST

## Task 3: S3 + KMS
- [ ] Create bucket with KMS server-side encryption
- [ ] Create KMS key with key policy
- [ ] Add S3 event notifications for processing triggers (if needed)
- [ ] Define path structure with skip list prefixes

## Task 4: Cognito
- [ ] Create User Pool (email as username)
- [ ] Create App Client (no secret for SPA)
- [ ] Configure password policies
- [ ] Output Pool ID and Client ID for frontend

## Task 5: Lambda Foundation
- [ ] Create shared IAM role with scoped policies
- [ ] Create `backend/functions/utils.py` with standard patterns
- [ ] Create Lambda Layer for third-party dependencies (if needed)
- [ ] Configure auto-zip in Terraform

## Task 6: API Gateway
- [ ] Create REST API with Cognito authorizer
- [ ] Create `modules/api_method/` and `modules/api_cors/`
- [ ] Set up deployment with triggers for ALL resources, methods, and CORS
- [ ] Test CORS on first endpoint before building more

## Task 7: CI/CD
- [ ] Create GitHub Actions workflow for terraform apply on merge to main
- [ ] Create GitHub Actions workflow for terraform plan on PR
- [ ] Configure AWS credentials as GitHub secrets
- [ ] Set up frontend auto-deploy (Vercel/Netlify/S3)

## Task 8: Validation
- [ ] Test Cognito sign-up/sign-in flow
- [ ] Test API Gateway + CORS from browser
- [ ] Test Lambda \u2192 DynamoDB with tenant isolation
- [ ] Test S3 presigned URLs with KMS/SigV4
- [ ] Test AI integration via Bedrock (if applicable)
