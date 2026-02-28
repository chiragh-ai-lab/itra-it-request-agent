# Requirements: Request Intake

## Introduction

Core CRUD for IT request submission, listing, and management. This is the foundation feature — everything else (classification, agent actions, chat) builds on top of requests.

### Requirement 1: Request CRUD
**User Story:** As an employee, I submit IT requests in natural language and track their status.
#### Acceptance Criteria
1. WHEN creating a request THEN DynamoDB entity SHALL use `SK: REQ#{request_id}` with tenant isolation via `PK: TENANT#{tenant_id}`
2. WHEN listing requests THEN GSI1 query on `TENANT#{tenant_id}#REQ` SHALL return all requests sorted by created_at
3. WHEN responding THEN ALL Decimal values SHALL be converted to float via `convert_decimals()`
4. WHEN submitting THEN title (required) and description (required) SHALL be captured; all other fields (category, severity, routing_team) are set by AI classification

### Requirement 2: Request Status Lifecycle
**User Story:** As a user, I see the current status of my request as it moves through the pipeline.
#### Acceptance Criteria
1. WHEN created THEN status SHALL be `submitted`
2. WHEN AI classifies THEN status SHALL change to `classified`
3. WHEN agent takes action THEN status SHALL change to `in_progress`
4. WHEN resolved THEN status SHALL change to `resolved`
5. WHEN classification fails THEN status SHALL be `classification_failed` and flagged for human review

### Requirement 3: Request Filtering
**User Story:** As an IT admin, I filter requests by status, category, and severity.
#### Acceptance Criteria
1. WHEN filtering by status THEN frontend SHALL filter client-side from full list (Phase 1)
2. WHEN filtering by category THEN requests SHALL be filterable by: access, hardware, software, cloud, network
3. WHEN filtering by severity THEN requests SHALL be filterable by: 1 (critical), 2 (high), 3 (medium), 4 (low)

---

# Design: Request Intake

## Data Model

| Entity | PK | SK | GSI1PK | GSI1SK |
|--------|----|----|--------|--------|
| Request | TENANT#{tid} | REQ#{req_id} | TENANT#{tid}#REQ | {created_at} |
| Comment | TENANT#{tid} | COMMENT#{req_id}#{comment_id} | REQ#{req_id} | {created_at} |
| Resolution | TENANT#{tid} | RES#{req_id} | REQ#{req_id} | {resolved_at} |
| Agent Log | TENANT#{tid} | ALOG#{req_id}#{log_id} | REQ#{req_id} | {timestamp} |

## Request Entity Fields

```json
{
  "PK": "TENANT#t_001",
  "SK": "REQ#req_001",
  "request_id": "req_001",
  "title": "Need VPN access for remote work",
  "description": "I'm starting remote work next week and need VPN credentials...",
  "status": "classified",
  "category": "access",
  "severity": 3,
  "routing_team": "helpdesk",
  "classification_confidence": 0.92,
  "submitter_email": "jane@company.com",
  "submitter_name": "Jane Smith",
  "agent_actions": [
    {"action": "notify_helpdesk", "timestamp": "2026-02-28T10:05:00Z", "result": "sent"}
  ],
  "resolution": null,
  "created_at": "2026-02-28T10:00:00Z",
  "updated_at": "2026-02-28T10:05:00Z"
}
```

## Lambda Functions

| Function | Memory | Timeout | Purpose |
|----------|--------|---------|---------|
| itra_create_request.py | 256MB | 30s | Create request, trigger async classification |
| itra_list_requests.py | 256MB | 30s | List requests via GSI1 |
| itra_get_request.py | 256MB | 30s | Get single request with comments/logs |
| itra_update_request.py | 256MB | 30s | Update request fields (status, resolution) |

## API Endpoints

| Method | Path | Lambda | Purpose |
|--------|------|--------|---------|
| POST | /requests | itra_create_request | Submit new request |
| GET | /requests | itra_list_requests | List all requests |
| GET | /requests/{id} | itra_get_request | Get request detail |
| PATCH | /requests/{id} | itra_update_request | Update request |

**CORS: Every endpoint above needs a corresponding OPTIONS method in Terraform.**

---

# Tasks: Request Intake

## Task 1: Backend Lambda Functions
- [ ] Implement `itra_create_request.py` — generate UUID, set status=submitted, store in DynamoDB, trigger async classification
- [ ] Implement `itra_list_requests.py` — GSI1 query with Decimal conversion
- [ ] Implement `itra_get_request.py` — get request + related comments/logs
- [ ] Implement `itra_update_request.py` — update status, add resolution

## Task 2: Terraform API Routes
- [ ] Create `itra_request_api.tf` with all 4 endpoints + CORS modules
- [ ] Update `api_gateway.tf` — ALL 4 sections (resource, method, CORS, depends_on)
- [ ] Test CORS on POST /requests before building more endpoints

## Task 3: Frontend Pages
- [ ] Dashboard page (`/`) — summary stats, recent requests
- [ ] Request list page (`/requests`) — table with status/category/severity filters
- [ ] Submit request page (`/requests/new`) — form with title + description
- [ ] Request detail page (`/requests/[id]`) — full detail with timeline, agent actions, chat

## Task 4: Validation
- [ ] Test create → list → get flow end-to-end
- [ ] Test tenant isolation (Tenant A cannot see Tenant B requests)
- [ ] Test CORS from Vercel frontend origin
- [ ] Verify Decimal conversion in all responses
