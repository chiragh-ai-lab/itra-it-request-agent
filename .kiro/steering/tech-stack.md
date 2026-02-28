# Technology Stack — IT Request Agent

## Frontend: Next.js 14+ via Vercel

- Next.js 14+ with TypeScript (App Router)
- React + Tailwind CSS for styling
- Shadcn/UI (Radix primitives) for component library
- Inter font family, Lucide icons only
- AWS Amplify UI React for Cognito authentication
- Deployment: Vercel (SSR) — auto-deploy from GitHub on push to main

**Vercel Configuration:**
- Root directory: `frontend/`
- Framework: Next.js (auto-detected)
- Environment variables from Terraform outputs:
  - `NEXT_PUBLIC_API_ENDPOINT` → API Gateway URL
  - `NEXT_PUBLIC_COGNITO_POOL_ID` → Cognito Pool ID
  - `NEXT_PUBLIC_COGNITO_CLIENT_ID` → Cognito Client ID
  - `NEXT_PUBLIC_AWS_REGION` → us-east-1

## Backend (Battle-Tested Defaults)

- Python 3.12 Lambda functions
- boto3 for AWS SDK (S3, DynamoDB, Bedrock, SES, etc.)
- All Lambda responses use shared `utils.py` (CORS headers, Decimal conversion, SigV4, tenant extraction)

## AI/ML

- **Classification**: AWS Bedrock with Claude Haiku (fast + cheap for intent classification)
- **Chat Agent**: AWS Bedrock with Claude Sonnet (multi-turn conversation, streaming)
- **Agent Actions**: AWS Bedrock with Claude Sonnet (reasoning for action decisions)
- All model IDs via environment variables — NEVER hardcode

**Environment Variables:**
```
CLASSIFICATION_MODEL=anthropic.claude-3-5-haiku-20241022-v1:0
CHAT_MODEL=anthropic.claude-3-7-sonnet-20250219-v1:0
ACTION_MODEL=anthropic.claude-3-7-sonnet-20250219-v1:0
DEFAULT_MODEL=anthropic.claude-3-7-sonnet-20250219-v1:0
```

## AgentCore Services

| Service | Implementation |
|---------|---------------|
| Runtime | Agent multi-step pipeline (classify → check → act) |
| Memory | Session + long-term + episodic via AgentCore Memory |
| Gateway | Existing Lambdas registered as agent tools |
| Identity | Cognito as identity provider, employee vs admin roles |
| Policy | Cedar rules for deterministic guardrails |
| Observability | CloudWatch dashboards |
| Evaluations | Test dataset of 30 sample requests |

## Infrastructure (Battle-Tested Defaults)

- Terraform 1.5+ for Infrastructure-as-Code
- AWS serverless: Lambda, API Gateway, DynamoDB, S3, Cognito
- Single-table DynamoDB design with tenant isolation
- KMS encryption on S3 buckets
- AWS SES for notification/escalation emails
- Resource prefix: `itra-` on ALL resources

## CI/CD

- **Backend**: GitHub Actions → terraform plan on PR, terraform apply on merge to main
- **Frontend**: Vercel auto-deploy on push to main
- **Principle**: GitHub is the source of truth. AWS is disposable.

## Key Dependencies

| Package | Purpose | Required? |
|---------|---------|-----------|
| boto3 | AWS SDK | Always |
| @aws-amplify/ui-react | Cognito auth | Always |
| tailwindcss | Styling | Always |
| shadcn/ui | Component library | Always |
| lucide-react | Icons | Always |
