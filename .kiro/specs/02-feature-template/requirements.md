# Feature Spec Template

<!--
  \u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557
  \u2551  COPY THIS ENTIRE DIRECTORY for each new feature.               \u2551
  \u2551                                                                  \u2551
  \u2551  Example: For a "User Profiles" feature, copy to:               \u2551
  \u2551    .kiro/specs/02-user-profiles/                                 \u2551
  \u2551                                                                  \u2551
  \u2551  Replace all [BRACKETED] sections with your feature details.     \u2551
  \u2551  Delete sections that don't apply (e.g., no AI, no exports).    \u2551
  \u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d
-->

---

# Requirements: [Feature Name]

## Introduction

[1-2 sentences: What this feature does and why it exists.]

### Requirement 1: [Core CRUD]
**User Story:** As a [user type], I [action] so that [benefit].
#### Acceptance Criteria
1. WHEN [trigger] THEN [expected behavior] SHALL [happen]
2. WHEN [creating] THEN DynamoDB entity SHALL use `SK: [ENTITY_TYPE]#{id}` with tenant isolation
3. WHEN [listing] THEN GSI1 query on `TENANT#{tenant_id}#[ENTITY_TYPE]` SHALL return results
4. WHEN [responding] THEN ALL Decimal values SHALL be converted to float

### Requirement 2: [File Upload / Processing] (if applicable)
**User Story:** As a [user type], I upload [file type] and the system [processes it].
#### Acceptance Criteria
1. WHEN uploading THEN presigned S3 URL SHALL be generated at `{tenant_id}/[path]/`
2. WHEN S3 client is used THEN SigV4 SHALL be configured for KMS encryption
3. WHEN processing exceeds 29 seconds THEN async Lambda self-invocation SHALL be used
4. WHEN generated files are stored THEN their S3 path SHALL be in the processing skip list

### Requirement 3: [AI Integration] (if applicable)
**User Story:** As a [user type], I [get AI-powered analysis/extraction/generation].
#### Acceptance Criteria
1. WHEN invoking AI THEN AWS Bedrock with Claude [Sonnet/Haiku] SHALL be used
2. WHEN processing images THEN Claude Vision SHALL handle the input
3. WHEN responding THEN `max_tokens` SHALL be set to cap output cost
4. WHEN classification is needed THEN Haiku SHALL be used (10x cheaper than Sonnet)

### Requirement 4: [Export / PDF / Email] (if applicable)
**User Story:** As a [user type], I [export/email/generate documents].
#### Acceptance Criteria
1. WHEN generating Excel THEN openpyxl SHALL be used with Lambda Layer
2. WHEN generating PDF THEN reportlab SHALL be used with float values (not Decimal)
3. WHEN emailing THEN AWS SES SHALL be used with multipart MIME
4. WHEN storing exports THEN S3 path SHALL be in the processing skip list

---

# Design: [Feature Name]

## Data Model

| Entity | PK | SK | GSI1PK | GSI1SK |
|--------|----|----|--------|--------|
| [Entity] | TENANT#{tid} | [TYPE]#{id} | TENANT#{tid}#[TYPE] | {timestamp} |

## Lambda Functions

| Function | Memory | Timeout | Purpose |
|----------|--------|---------|---------|
| [feature]_create.py | 256MB | 30s | Create [entity] |
| [feature]_list.py | 256MB | 30s | List [entities] via GSI1 |
| [feature]_get.py | 256MB | 30s | Get [entity] details |
| [feature]_update.py | 256MB | 30s | Update [entity] |
| [feature]_delete.py | 256MB | 30s | Delete [entity] + cleanup |
| [feature]_process.py | 2048MB | 300s | Heavy processing (if needed) |

## API Endpoints

| Method | Path | Lambda | Purpose |
|--------|------|--------|---------|
| POST | /[feature] | [feature]_create | Create |
| GET | /[feature] | [feature]_list | List all |
| GET | /[feature]/{id} | [feature]_get | Get one |
| PATCH | /[feature]/{id} | [feature]_update | Update |
| DELETE | /[feature]/{id} | [feature]_delete | Delete |

**CORS: Every endpoint above needs a corresponding OPTIONS method in Terraform.**

---

# Tasks: [Feature Name]

## Task 1: Backend Lambda Functions
- [ ] Implement `[feature]_create.py` using standard utils (CORS headers, Decimal conversion, tenant isolation)
- [ ] Implement `[feature]_list.py` with GSI1 query
- [ ] Implement `[feature]_get.py` with Decimal conversion
- [ ] Implement `[feature]_update.py`
- [ ] Implement `[feature]_delete.py` with S3 cleanup (if applicable)

## Task 2: Terraform API Routes
- [ ] Create `[feature]_api.tf` with API methods + CORS modules
- [ ] Update `api_gateway.tf` \u2014 ALL 4 sections (resource, method, CORS, depends_on)
- [ ] Add Lambda function definitions to `[feature]_lambda.tf` (or `lambda.tf`)
- [ ] Test CORS before browser testing

## Task 3: Frontend Pages
- [ ] Create list page `/[feature]`
- [ ] Create detail page `/[feature]/[id]` (with server/client split if using Next.js static export)
- [ ] Create form/modal for create/edit
- [ ] Add API client functions to `lib/[feature]-api.ts`

## Task 4: AI Integration (if applicable)
- [ ] Design Bedrock prompt with examples and constraints
- [ ] Implement extraction/analysis Lambda
- [ ] Set `max_tokens` to control output cost
- [ ] Use Haiku for classification, Sonnet for complex reasoning

## Task 5: Testing
- [ ] Unit tests with pytest + moto for AWS mocking
- [ ] Test CORS on all endpoints
- [ ] Test Decimal conversion in responses
- [ ] Test S3 SigV4 with KMS
- [ ] Test async processing pattern (if applicable)
- [ ] End-to-end browser testing
