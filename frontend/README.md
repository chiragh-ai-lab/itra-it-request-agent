# IT Request Agent - Frontend

Next.js 14 frontend application with AWS Cognito authentication and AI-powered request management.

## Features

- AWS Cognito authentication with Amplify UI
- Dashboard with request statistics
- Request list with filtering and search
- Submit new requests with AI classification
- Request detail page with agent actions timeline
- Chat with AI agent about requests
- Responsive design with Tailwind CSS
- Shadcn/UI components

## Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.local.example .env.local
```

Edit `.env.local` with your AWS configuration from Terraform outputs.

3. Run development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Environment Variables

Required environment variables (from Terraform outputs):

- `NEXT_PUBLIC_AWS_REGION` - AWS region (us-east-1)
- `NEXT_PUBLIC_COGNITO_USER_POOL_ID` - Cognito User Pool ID
- `NEXT_PUBLIC_COGNITO_CLIENT_ID` - Cognito App Client ID
- `NEXT_PUBLIC_API_ENDPOINT` - API Gateway endpoint URL

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout with auth wrapper
│   ├── page.tsx                # Dashboard page
│   ├── globals.css             # Global styles
│   └── requests/
│       ├── page.tsx            # Request list page
│       ├── new/
│       │   └── page.tsx        # Submit request form
│       └── [id]/
│           └── page.tsx        # Request detail page
├── components/
│   ├── auth-wrapper.tsx        # Amplify authentication wrapper
│   ├── sidebar.tsx             # Navigation sidebar
│   └── ui/                     # Shadcn/UI components
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       ├── textarea.tsx
│       ├── badge.tsx
│       └── label.tsx
└── lib/
    ├── amplify-config.ts       # Cognito configuration
    ├── api-client.ts           # Authenticated API wrapper
    └── utils.ts                # Utility functions
```

## Pages

### Dashboard (/)
- Overview statistics (total, submitted, in progress, resolved)
- Recent requests list
- Quick navigation

### Requests (/requests)
- Full request list with pagination
- Search by title/description
- Filter by status and category
- Sort options

### New Request (/requests/new)
- Submit new IT request
- Title and description fields
- Automatic AI classification on submit

### Request Detail (/requests/[id])
- Full request details
- Agent actions timeline
- Chat with AI agent
- Resolve request
- Trigger manual classification

## Authentication

The app uses AWS Cognito with Amplify UI React for authentication:

- Sign up with email verification
- Sign in with email/password
- Password reset flow
- Automatic token refresh
- JWT token attached to all API calls

## API Integration

All API calls go through the authenticated API client (`lib/api-client.ts`):

- Automatic JWT token attachment
- Error handling with user-friendly messages
- 401 redirect to sign-in
- Type-safe request/response handling

## Deployment

### Vercel (Recommended)

1. Connect your GitHub repository to Vercel
2. Add environment variables in Vercel dashboard
3. Deploy automatically on push to main

### Manual Build

```bash
npm run build
npm start
```

## Development

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Run production build
npm start

# Lint code
npm run lint
```

## Design System

The app uses Shadcn/UI design system with:

- Inter font family
- Lucide React icons
- Tailwind CSS for styling
- CSS variables for theming
- Responsive breakpoints

## Troubleshooting

### Authentication Issues

- Verify Cognito configuration in `.env.local`
- Check User Pool and Client ID match Terraform outputs
- Ensure email verification is enabled in Cognito

### API Errors

- Verify API endpoint URL in `.env.local`
- Check CORS configuration in API Gateway
- Ensure Lambda functions are deployed
- Check CloudWatch logs for backend errors

### Build Errors

- Clear `.next` directory: `rm -rf .next`
- Delete `node_modules` and reinstall: `rm -rf node_modules && npm install`
- Check TypeScript errors: `npm run lint`
