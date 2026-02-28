# Project Context — IT Request Agent (itra-)

## Business Context

**TEKsystems** (AWS Premier Tier Services Partner) — Building a productized AgentCore offering that delivers AI-powered enterprise applications in weeks instead of months.

**This software is** a reference implementation / demo application being built to validate the TEKsystems AgentCore delivery methodology and exercise all 7 AWS Bedrock AgentCore services end-to-end.

## Product Overview

Smart IT Request Agent that processes natural language IT requests through AI classification with enterprise guardrails:

1. **Request Submission**: Users submit IT requests in natural language ("I need VPN access", "My laptop screen is cracked", "Production database is down")
2. **AI Classification**: Agent classifies category (access, hardware, software, cloud, network), severity (1-4), and routing team
3. **Policy-Checked Actions**: Agent executes approved actions (notify, escalate, auto-resolve) — Policy blocks unauthorized actions deterministically
4. **Memory & Learning**: Agent remembers past resolutions and gets smarter over time
5. **Observability**: Real-time dashboard monitors agent behavior, accuracy, and costs

## Target Users

- **Employees**: Submit IT requests via natural language, track status
- **IT Admins**: Review escalated requests, approve high-privilege actions, monitor agent performance

## Success Metrics

- All 7 AgentCore services integrated and demonstrable
- Starter Kit reuse: zero CORS/Decimal/SigV4 debugging (all prevented by coding-standards.md)
- Customer handoff: developer adds new feature by copying template spec + delegating to Kiro
- Destroy/rebuild: entire app recoverable from GitHub in under 15 minutes

## Competitive Advantage

- 3-layer delivery model (Platform 100% reuse, Domain 70-80% reuse, Customer custom)
- Kiro spec-driven workflow with automated quality hooks
- AgentCore Policy engine provides deterministic guardrails outside the agent loop

## Resource Naming

ALL AWS resources use the `itra-` prefix. This prevents collisions with existing apps in the same account:
- `proc-` = AI Procurement Agent
- `vrfq-` = Visual RFQ Portal
- `itra-` = IT Request Agent (THIS PROJECT)

## Reference Codebases

### Primary: Visual RFQ Portal (`C:\Users\cqureshi\Documents\Projects\1-AI-Projects\Visual-RFQ-Portal`)
More recent, refined patterns. Use as the FIRST reference for:
- Terraform module structure and api_gateway.tf
- DynamoDB single-table design with GSIs
- Lambda function structure and utils.py
- Frontend components, auth wrapper, API client
- CORS configuration and deployment patterns
- Export patterns (Excel/PDF if needed)

### Secondary: AI Procurement Agent (`C:\Users\cqureshi\Documents\Projects\1-AI-Projects\ai-procurement-agent`)
Use ONLY for patterns the VRFQ Portal does not have:
- Bedrock classification Lambda (boq_classify.py)
- Chat agent with intent routing (chat_agent.py)
- Async Lambda self-invocation for heavy processing
- SES email composition and sending

**Critical docs to read BEFORE implementing:**
- `ai-procurement-agent/docs/troubleshooting.md` — CORS, Decimal, SigV4, SES, Lambda timeout fixes
- `ai-procurement-agent/docs/API_PATTERNS.md` — Lambda handler structure, presigned URLs, export patterns
- `ai-procurement-agent/docs/DEVELOPMENT.md` — Terraform workflow, Lambda rebuild, CORS testing

### Conflict Resolution
If both projects implement the same pattern differently,
ALWAYS follow the VRFQ Portal version — it is more recent
and contains fixes for issues found in the procurement agent.

### What NOT to Copy
Do NOT reuse any procurement/FF&E/RFQ/BOQ business logic.
Only reuse infrastructure and utility patterns.
Adapt all patterns to use the `itra-` prefix.
