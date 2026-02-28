# Requirements: Agent Actions & Classification

## Introduction

AI-powered classification pipeline and agent action execution. This is where AgentCore services come together: Runtime orchestrates the pipeline, Policy guards actions, Memory provides context, and Observability tracks everything.

### Requirement 1: Request Classification
**User Story:** As the system, I automatically classify incoming requests by category, severity, and routing team.
#### Acceptance Criteria
1. WHEN a request is created THEN async classification SHALL be triggered via Lambda self-invocation
2. WHEN classifying THEN Claude Haiku SHALL be used (fast + cheap) with structured JSON output
3. WHEN classification confidence is below 0.60 THEN request SHALL be flagged for human review
4. WHEN classification completes THEN request status SHALL update to `classified`
5. WHEN classification fails THEN status SHALL be `classification_failed` with error logged

### Requirement 2: Agent Action Execution
**User Story:** As the agent, I execute approved actions (notify, escalate, auto-resolve) based on classification.
#### Acceptance Criteria
1. WHEN agent decides on an action THEN Policy SHALL check Cedar rules BEFORE execution
2. WHEN Policy blocks an action THEN the block SHALL be logged and request escalated to human
3. WHEN action executes THEN it SHALL be recorded in the agent_actions array on the request
4. WHEN agent exceeds 5 actions on a single request THEN Cedar rate-limit policy SHALL block further actions
5. WHEN actions complete THEN request status SHALL update to `in_progress` or `resolved`

### Requirement 3: Chat Agent
**User Story:** As a user, I chat with the agent about my request for status updates and additional context.
#### Acceptance Criteria
1. WHEN chatting THEN Claude Sonnet SHALL be used with streaming via Bedrock
2. WHEN context is needed THEN AgentCore Memory SHALL provide past resolutions for similar requests
3. WHEN user asks about request status THEN agent SHALL retrieve current request data from DynamoDB
4. WHEN conversation exceeds context window THEN oldest messages SHALL be summarized

### Requirement 4: Notification
**User Story:** As the system, I notify relevant teams when requests are classified or escalated.
#### Acceptance Criteria
1. WHEN request is classified THEN routing_team SHALL receive email notification via SES
2. WHEN severity is 1 (critical) THEN immediate escalation notification SHALL be sent
3. WHEN Policy blocks an action THEN admin SHALL be notified

---

# Design: Agent Actions

## Classification Prompt (Haiku)

```
You are an IT request classification agent.

Classify the following IT request into:
- category: one of [access, hardware, software, cloud, network]
- severity: 1 (critical/production down), 2 (high/blocking work), 3 (medium/workaround exists), 4 (low/nice to have)
- routing_team: one of [helpdesk, cloud-ops, security, infrastructure, development]
- suggested_actions: array of recommended actions

Request title: {title}
Request description: {description}

Return ONLY valid JSON. No markdown, no explanation.
{
  "category": "...",
  "severity": N,
  "routing_team": "...",
  "confidence": 0.XX,
  "suggested_actions": ["..."],
  "reasoning": "one sentence why"
}
```

## Lambda Functions

| Function | Memory | Timeout | Purpose |
|----------|--------|---------|---------|
| itra_classify_request.py | 1024MB | 120s | Bedrock Haiku classification (async) |
| itra_agent_action.py | 1024MB | 120s | Execute agent actions with Policy check |
| itra_chat_agent.py | 1024MB | 120s | Multi-turn chat with Sonnet streaming |
| itra_send_notification.py | 256MB | 30s | SES email notifications |
| itra_resolve_request.py | 256MB | 30s | Mark request resolved, capture resolution |

## API Endpoints

| Method | Path | Lambda | Purpose |
|--------|------|--------|---------|
| POST | /requests/{id}/classify | itra_classify_request | Trigger classification (or auto on create) |
| POST | /requests/{id}/action | itra_agent_action | Execute agent action |
| POST | /requests/{id}/chat | itra_chat_agent | Chat with agent about request |
| POST | /requests/{id}/resolve | itra_resolve_request | Resolve request |

## AgentCore Service Wiring

| Service | Implementation |
|---------|---------------|
| **Runtime** | itra_classify → check Policy → itra_agent_action → itra_send_notification |
| **Memory** | Session context per chat, long-term storage of past resolutions |
| **Gateway** | Register itra_classify, itra_agent_action, itra_send_notification as tools |
| **Identity** | Cognito JWT → employee vs admin role → determines allowed actions |
| **Policy** | Cedar rules checked before every agent action |
| **Observability** | CloudWatch dashboard: classification accuracy, policy blocks, costs |
| **Evaluations** | 30 test requests in tests/fixtures/ with expected classifications |

## Cedar Policy Rules

```cedar
// Block provisioning without manager approval
forbid (
  principal,
  action == Action::"provision_resource",
  resource
) unless {
  context.request.has_manager_approval == true
};

// Force escalation for severity 1
forbid (
  principal,
  action == Action::"auto_resolve",
  resource
) when {
  resource.severity == 1
};

// Rate limit: max 5 agent actions per request
forbid (
  principal,
  action == Action::"agent_action",
  resource
) when {
  resource.action_count >= 5
};
```

---

# Tasks: Agent Actions

## Task 1: Classification Lambda
- [ ] Implement `itra_classify_request.py` with async self-invocation pattern
- [ ] Design classification prompt with 3-5 few-shot examples
- [ ] Parse Bedrock JSON response, handle malformed output gracefully
- [ ] Update request with category, severity, routing_team, confidence
- [ ] Chain to itra_agent_action if confidence > 0.60

## Task 2: Agent Action Lambda
- [ ] Implement `itra_agent_action.py` with Policy check before execution
- [ ] Implement action types: notify_team, escalate, auto_resolve, request_info
- [ ] Log each action in agent_actions array on request
- [ ] Respect Cedar rate-limit policy (max 5 actions)

## Task 3: Chat Agent Lambda
- [ ] Implement `itra_chat_agent.py` with Bedrock Sonnet streaming
- [ ] Retrieve request context from DynamoDB for grounding
- [ ] Query AgentCore Memory for similar past resolutions
- [ ] Handle conversation history truncation for long chats

## Task 4: Notification Lambda
- [ ] Implement `itra_send_notification.py` with SES
- [ ] HTML + plain text multipart MIME
- [ ] Templates for: new request, escalation, resolution, policy block

## Task 5: Cedar Policies
- [ ] Define Cedar schema (Principal, Action, Resource types)
- [ ] Implement 4 policies: no-provision-without-approval, force-escalation-sev1, restrict-payroll-access, rate-limit-actions
- [ ] Test each policy with demo scenarios

## Task 6: Observability Dashboard
- [ ] Create CloudWatch dashboard with key metrics
- [ ] Track: classification accuracy, policy blocks, action counts, Bedrock costs
- [ ] Set billing alarms at $10, $50, $100

## Task 7: Evaluations Test Dataset
- [ ] Create 30 test requests in tests/fixtures/sample-requests.json
- [ ] Include expected category, severity, routing_team for each
- [ ] Include 5+ edge cases (ambiguous, multi-category)
- [ ] Run baseline accuracy test
