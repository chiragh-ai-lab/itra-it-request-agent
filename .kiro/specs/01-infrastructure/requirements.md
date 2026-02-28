# Requirements: AWS Serverless Infrastructure

<!--
  This spec is reusable across ANY AWS serverless application.
  Modify entity types and GSI patterns to match your data model.
  The core patterns (tenant isolation, KMS, CORS, Lambda) are universal.
-->

## Introduction

Complete AWS serverless infrastructure deployed via Terraform, supporting a multi-tenant application with AI capabilities.

### Requirement 1: DynamoDB Single-Table Design
**User Story:** As a system, I need a single DynamoDB table with tenant isolation to store all entity types efficiently.
#### Acceptance Criteria
1. WHEN any entity is created THEN PK SHALL be `TENANT#{tenant_id}` and SK SHALL be `{ENTITY_TYPE}#{entity_id}`
2. WHEN querying entities THEN GSI1 (`TENANT#{tenant_id}#{ENTITY_TYPE}`) SHALL return all entities of a given type
3. WHEN any user accesses data THEN tenant isolation SHALL be enforced via JWT claims mapped to PK prefix
4. WHEN billing mode is set THEN PAY_PER_REQUEST SHALL be used (no capacity planning needed)

### Requirement 2: S3 Storage with KMS Encryption
**User Story:** As the platform, I need encrypted S3 storage with organized paths and processing skip logic.
#### Acceptance Criteria
1. WHEN files are stored THEN S3 SHALL use KMS encryption requiring SigV4 signatures
2. WHEN internal/generated files exist THEN the processing pipeline SHALL skip them via prefix matching
3. WHEN presigned URLs are generated THEN they SHALL use SigV4 and have configurable expiry (default 1 hour)

### Requirement 3: API Gateway with Cognito Authorization
**User Story:** As the frontend, I need a REST API with JWT authentication and CORS on every endpoint.
#### Acceptance Criteria
1. WHEN any API endpoint is created THEN it SHALL have a corresponding CORS OPTIONS method
2. WHEN API Gateway triggers are updated THEN ALL 4 sections in api_gateway.tf SHALL be updated
3. WHEN requests arrive THEN Cognito JWT authorizer SHALL validate tokens and extract tenant_id
4. WHEN reusable modules are defined THEN `modules/api_method/` and `modules/api_cors/` SHALL be used for consistency

### Requirement 4: Lambda Functions with Shared IAM Role
**User Story:** As the backend, Lambda functions need least-privilege access to required AWS services.
#### Acceptance Criteria
1. WHEN Lambda functions are deployed THEN they SHALL share a single IAM role with scoped policies
2. WHEN heavy processing is needed THEN memory (up to 2048MB) and timeout (up to 300s) SHALL be configurable
3. WHEN code changes THEN Terraform SHALL auto-zip and redeploy from backend/functions/
4. WHEN third-party libraries are needed THEN Lambda Layers SHALL be used

### Requirement 5: Cognito Authentication
**User Story:** As a user, I sign in securely and receive JWT tokens for API access.
#### Acceptance Criteria
1. WHEN signing up THEN email SHALL be the username
2. WHEN authenticated THEN JWT token SHALL contain tenant_id (sub claim)
3. WHEN tokens expire THEN automatic refresh SHALL be handled by frontend

### Requirement 6: CI/CD Pipeline
**User Story:** As a developer, I need automated deployment on push to main.
#### Acceptance Criteria
1. WHEN backend code is pushed to main THEN GitHub Actions SHALL run terraform apply
2. WHEN a PR is opened THEN GitHub Actions SHALL run terraform plan
3. WHEN frontend code is pushed THEN Vercel (or chosen platform) SHALL auto-deploy

### Requirement 7: AI Integration via Bedrock (If Applicable)
**User Story:** As the platform, I need AI capabilities via AWS Bedrock.
#### Acceptance Criteria
1. WHEN AI features are used THEN Bedrock InvokeModel permission SHALL be in Lambda IAM role
2. WHEN using Claude Vision THEN image tokens SHALL be accounted for in cost estimates
3. WHEN streaming responses are needed THEN Bedrock streaming API SHALL be used
