# Requirements: AI Integration via AWS Bedrock

## Introduction

AI-powered features using AWS Bedrock with Claude models. ITRA uses two models: Haiku for fast classification and Sonnet for chat/reasoning.

### Requirement 1: Model Selection Strategy
**User Story:** As the system, I use the right model for each task to optimize cost and quality.
#### Acceptance Criteria
1. WHEN classifying requests THEN Claude Haiku SHALL be used (fast, ~$0.001 per request)
2. WHEN chatting or reasoning about actions THEN Claude Sonnet SHALL be used
3. WHEN setting parameters THEN `max_tokens` SHALL always be specified to cap cost
4. WHEN model IDs are configured THEN environment variables SHALL be used — NEVER hardcode

### Requirement 2: Classification Pipeline
**User Story:** As the system, I classify IT requests into category, severity, and routing team.
#### Acceptance Criteria
1. WHEN classifying THEN structured JSON output SHALL be enforced via prompt design
2. WHEN Bedrock returns malformed JSON THEN retry once, then flag for human review
3. WHEN classification confidence < 0.60 THEN request SHALL NOT be auto-routed
4. WHEN processing exceeds 29 seconds THEN async Lambda self-invocation SHALL be used

### Requirement 3: Chat Interface
**User Story:** As a user, I chat with the agent about my request.
#### Acceptance Criteria
1. WHEN chatting THEN Bedrock streaming API SHALL be used for real-time responses
2. WHEN context is needed THEN request data + past resolutions SHALL be included in prompt
3. WHEN context exceeds token limit THEN oldest messages SHALL be summarized

### Requirement 4: Cost Control
**User Story:** As the operator, AI costs stay predictable.
#### Acceptance Criteria
1. WHEN billing is monitored THEN CloudWatch alarms SHALL be set at $10, $50, $100
2. WHEN classification uses Haiku THEN per-request cost SHALL be under $0.01
3. WHEN chat uses Sonnet THEN max_tokens SHALL be capped at 2000

---

# Design: AI Integration

## Model Configuration

```python
import os

def get_model_id(task: str) -> str:
    model_map = {
        "classification": os.environ.get("CLASSIFICATION_MODEL"),
        "chat": os.environ.get("CHAT_MODEL"),
        "action": os.environ.get("ACTION_MODEL"),
    }
    return model_map.get(task, os.environ.get("DEFAULT_MODEL"))
```

## Environment Variables
```
CLASSIFICATION_MODEL=us.anthropic.claude-haiku-4-5-20251001
CHAT_MODEL=us.anthropic.claude-sonnet-4-6-20260217
ACTION_MODEL=us.anthropic.claude-sonnet-4-6-20260217
DEFAULT_MODEL=us.anthropic.claude-sonnet-4-6-20260217
```

## Cost Estimates

| Task | Model | Est. Cost Per Request | Volume |
|------|-------|-----------------------|--------|
| Classification | Haiku | ~$0.001 | Every request |
| Chat turn | Sonnet | ~$0.01-0.03 | On-demand |
| Agent reasoning | Sonnet | ~$0.01-0.02 | Per action decision |

Monthly estimate at 100 requests/day: ~$5-15 Bedrock costs.

---

# Tasks: AI Integration

## Task 1: Bedrock Setup
- [ ] Add Bedrock InvokeModel + InvokeModelWithResponseStream permissions to Lambda IAM role
- [ ] Create shared `bedrock_utils.py` with invocation helpers
- [ ] Verify model access in Bedrock console (Haiku + Sonnet)

## Task 2: Classification Prompt
- [ ] Design system prompt with 5 few-shot examples covering all 5 categories
- [ ] Enforce JSON-only output format
- [ ] Set max_tokens=500 for classification (small output)
- [ ] Test prompt manually in Bedrock console before coding Lambda

## Task 3: Chat Prompt
- [ ] Design system prompt with request context injection
- [ ] Implement streaming response handling
- [ ] Set max_tokens=2000 for chat responses
- [ ] Handle conversation history management

## Task 4: Cost Monitoring
- [ ] Create CloudWatch billing alarms ($10, $50, $100)
- [ ] Log token usage from Bedrock response metadata
- [ ] Track per-task costs in Observability dashboard
