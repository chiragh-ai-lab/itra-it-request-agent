# Requirements: Frontend Application

<!--
  Adapt based on your chosen frontend framework from tech-stack.md.
  The authentication and API client patterns are universal.
-->

## Introduction

Frontend application with Cognito authentication, authenticated API client, and responsive UI.

### Requirement 1: Authentication
**User Story:** As a user, I sign in via AWS Cognito and access tenant-isolated data.
#### Acceptance Criteria
1. WHEN authenticating THEN Cognito flows (sign-up, sign-in, password reset) SHALL be handled
2. WHEN authenticated THEN JWT token SHALL be included in all API requests automatically
3. WHEN tokens expire THEN automatic refresh SHALL occur without user intervention

### Requirement 2: Authenticated API Client
**User Story:** As the frontend, all API calls include authentication and handle errors consistently.
#### Acceptance Criteria
1. WHEN making API calls THEN JWT token SHALL be attached from Cognito session
2. WHEN API returns error THEN user-friendly message SHALL be displayed
3. WHEN 401 is received THEN user SHALL be redirected to sign-in

### Requirement 3: Responsive Layout
**User Story:** As a user, I access the app from desktop and mobile devices.
#### Acceptance Criteria
1. WHEN on desktop THEN full navigation sidebar SHALL be visible
2. WHEN on mobile THEN responsive layout SHALL adapt (hamburger menu or bottom nav)

### Requirement 4: Deployment (Choose One)
**Option A: Vercel Only (Simplest)**
- Auto-deploy from GitHub on push to main
- SSR handles dynamic routes natively
- No CloudFront/S3 configuration needed

**Option B: Vercel + S3/CloudFront (Dual)**
- Vercel for development, S3/CloudFront for production/cost optimization
- Requires: conditional `output: 'export'`, `generateStaticParams()`, CloudFront Functions
- See coding-standards.md for full dual deployment requirements

**Option C: S3/CloudFront Only**
- Static export, all client-side rendering
- CloudFront Functions for SPA routing
- Lowest cost at scale

---

# Tasks: Frontend Application

## Task 1: Project Setup
- [ ] Initialize project with chosen framework + TypeScript + Tailwind CSS
- [ ] Configure environment variables from Terraform outputs
- [ ] Set up Cognito authentication (Amplify UI React or Amplify JS)
- [ ] Create authenticated API client wrapper (`lib/api.ts`)

## Task 2: Layout & Navigation
- [ ] Create app layout with sidebar/header navigation
- [ ] Create authentication wrapper component
- [ ] Create loading/error state components

## Task 3: Feature Pages
- [ ] For each feature spec, create:
  - [ ] List page with filtering/sorting
  - [ ] Detail page with relevant actions
  - [ ] Create/edit forms or modals
  - [ ] API client functions in `lib/[feature]-api.ts`

## Task 4: Deployment
- [ ] Configure chosen deployment target
- [ ] Set up auto-deploy from GitHub
- [ ] Test authentication flow end-to-end
- [ ] Verify API calls work with CORS in deployed environment
