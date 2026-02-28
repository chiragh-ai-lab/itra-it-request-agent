# IT Request Agent — Kiro Starter Kit (Pre-Filled)

## What Is This?

A **ready-to-go Kiro spec-driven scaffolding** for the IT Request Agent (itra-) project. This is the universal AWS Serverless Starter Kit **pre-filled** with all ITRA-specific context, feature specs, and AgentCore service mappings.

## What's Inside

```
.kiro/
├── steering/                          # Kiro reads these on EVERY prompt
│   ├── project-context.md             # ✅ FILLED — ITRA business context + reference codebases
│   ├── tech-stack.md                  # ✅ FILLED — Next.js + Vercel + Haiku/Sonnet + AgentCore
│   └── coding-standards.md            # ⭐ UNIVERSAL — all pitfall prevention (DO NOT EDIT)
│
├── specs/
│   ├── 01-infrastructure/             # AWS foundation (DynamoDB, S3, Cognito, API GW, Lambda)
│   │   ├── requirements.md            # Universal serverless requirements
│   │   └── design.md                  # Architecture + Terraform structure + tasks
│   ├── 02-feature-template/           # 📋 COPY THIS for additional features
│   │   └── requirements.md            # Template with CRUD, uploads, AI, exports
│   ├── 03-frontend/                   # Frontend app (auth, API client, pages)
│   │   └── requirements.md            # Next.js + Vercel deployment
│   ├── 04-ai-integration/             # ✅ FILLED — Haiku classification + Sonnet chat
│   │   └── requirements.md            # Model selection, cost control, streaming
│   ├── 05-request-intake/             # ✅ FILLED — Core request CRUD
│   │   └── requirements.md            # Data model, Lambda specs, API endpoints, tasks
│   └── 06-agent-actions/              # ✅ FILLED — Classification + actions + chat + Cedar
│       └── requirements.md            # AgentCore wiring, Cedar policies, Evaluations
│
└── hooks/
    └── hooks.md                       # 8 automated quality checks (incl. itra- prefix check)
```

## How To Use

### Step 1: Create Project Folder

```powershell
mkdir C:\Users\cqureshi\Documents\Projects\1-AI-Projects\IT-Request-Agent
cd C:\Users\cqureshi\Documents\Projects\1-AI-Projects\IT-Request-Agent
git init
```

### Step 2: Copy This Kit

```powershell
# Copy the .kiro folder into your new project root
xcopy /E /I path\to\itra-kiro-starter-kit\.kiro .\.kiro
```

### Step 3: Verify Reference Codebase Paths

Open `.kiro/steering/project-context.md` and verify the paths match your machine:
- Primary: `C:\Users\cqureshi\Documents\Projects\1-AI-Projects\Visual-RFQ-Portal`
- Secondary: `C:\Users\cqureshi\Documents\Projects\1-AI-Projects\ai-procurement-agent`

### Step 4: Open in Kiro and Delegate

Work through specs in order:
1. **01-infrastructure** — Deploy AWS foundation. Test CORS on first endpoint.
2. **05-request-intake** — Build request CRUD. This is your "Hello World."
3. **06-agent-actions** — Wire classification, actions, chat, Cedar policies.
4. **03-frontend** — Build Next.js pages for dashboard, request list, detail, chat.
5. **04-ai-integration** — Fine-tune prompts, set up cost monitoring.

### Step 5: DO NOT TOUCH coding-standards.md

This file prevents 90%+ of AWS serverless deployment bugs. Leave it as-is.

## Reference: Implementation Guide

See `ITRA-IT-Request-Agent-Implementation-Guide.docx` for the full 17-section guide covering naming conventions, AgentCore service mapping, data model, two-day build plan, and cost estimates.
