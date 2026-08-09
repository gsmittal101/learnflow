## 1 User Stories

### US-01 · Registration

**As a** new visitor,  
**I want to** create a LearnFlow account by providing my full name, email, and a strong password,  
**so that** I receive a personal, secured profile on the learning platform.

### US-02 · Email Verification

**As a** newly registered user,  
**I want to** verify my email address through a confirmation link,  
**so that** the platform can trust that my email is valid and I can receive future communications.

### US-03 · Login

**As a** registered user,  
**I want to** log in with my email and password,  
**so that** I can access my enrolled courses, progress data, and account settings.

### US-04 · JWT Token Lifecycle

**As an** authenticated user,  
**I want** the system to issue, refresh, and revoke JWT tokens transparently,  
**so that** I stay securely signed in across sessions without repeatedly entering my credentials.

### US-05 · Logout

**As a** logged-in user,  
**I want to** log out from my current session (or all sessions),  
**so that** no one else can use my tokens if I walk away from a shared device.

### US-06 · Password Reset (Forgot Password)

**As a** user who has forgotten my password,  
**I want to** request a reset link via email and set a new password,  
**so that** I can regain access to my account without contacting support.

----------

## 2 Acceptance Criteria (Given / When / Then)

### AC-01 · Registration — Happy Path

#

Given

When

Then

1

A visitor is on the registration page

They submit a valid full name, unique email, and a password that meets complexity rules (≥ 8 chars, upper + lower + digit + special)

The system creates a user record with a **bcrypt/argon2-hashed** password, returns **201 Created**, and sends a verification email

2

A visitor submits an email that already exists

They press "Register"

The system returns **409 Conflict** with the message _"An account with this email already exists"_

3

A visitor submits a password that fails complexity rules

They press "Register"

The system returns **400 Bad Request** with a list of all unmet password rules

4

A visitor omits any required field (name, email, password)

They press "Register"

The system returns **422 Unprocessable Entity** identifying the missing field(s)

### AC-02 · Email Verification

#

Given

When

Then

1

A user has just registered and received a verification email

They click the verification link within 24 hours

The system marks the account as **verified**, returns **200 OK**, and redirects to the login page

2

A verification token has expired (> 24 h)

The user clicks the link

The system returns **410 Gone** and prompts the user to request a new verification email

3

An unverified user attempts to log in

They submit valid credentials

The system returns **403 Forbidden** with the message _"Please verify your email before logging in"_ and offers a resend option

### AC-03 · Login

#

Given   When  Then

1

A verified user enters a correct email and password

They submit the login form

The system returns **200 OK** with a JWT access token (in the response body) and a refresh token (in an **httpOnly** secure cookie)

2

A user enters an incorrect password

They submit the login form

The system returns **401 Unauthorized** with a generic message _"Invalid email or password"_ (no account enumeration)

3

An unregistered email is submitted

The form is submitted

The system returns the same **401** generic message (no account enumeration)

4

A user fails login **5 times** within 15 minutes

They attempt a 6th login

The system returns **429 Too Many Requests**, locks the account for 15 minutes, and logs the event

### AC-04 · JWT Token Lifecycle

#

Given  When   Then

1

A user has successfully logged in

The backend authenticates them

It issues a signed **access token** (expiry: 15 min) and a signed **refresh token** (expiry: 7 days), both containing the user's `sub` (user ID) and `role` claims

2

An access token has expired

The client sends a valid, non-revoked refresh token to `POST /auth/refresh`

The system issues a new access token (and optionally rotates the refresh token), returning **200 OK**

3

A refresh token is expired, revoked, or malformed

The client sends it to the refresh endpoint

The system returns **401 Unauthorized** and the client must redirect the user to the login page

4

A request is made to any protected endpoint

The access token is missing or invalid

The system returns **401 Unauthorized**

### AC-05 · Logout

#

Given  When  Then

1

A logged-in user triggers logout

They call `POST /auth/logout`

The system adds the refresh token to a server-side **blocklist** (PostgreSQL table or Redis), clears the httpOnly cookie, and returns **200 OK**

2

A user triggers "Log out all sessions"

They call `POST /auth/logout-all`

The system revokes **all** refresh tokens for that user ID and returns **200 OK**

### AC-06 · Password Reset

#

Given  When  Then

1

A user requests a reset for a registered email

They submit the forgot-password form

The system generates a single-use, time-limited token (expiry: 1 hour), stores its hash, sends a reset link to the email, and returns **200 OK** with a generic message _"If that email exists, a reset link has been sent"_

2

A user requests a reset for an **unregistered** email

They submit the form

The system returns the **same 200 OK** generic message (no account enumeration) without sending any email

3

A user clicks a valid, unexpired reset link

They submit a new password that meets complexity rules

The system hashes and stores the new password, invalidates the reset token, revokes all existing refresh tokens for the user, and returns **200 OK**

4

A reset token is expired or already used

The user tries to submit a new password

The system returns **410 Gone** with the message _"This reset link has expired. Please request a new one"_

5

A user submits a new password that fails complexity rules

They click "Reset Password"

The system returns **400 Bad Request** listing the unmet rules

----------

## 3 Business Requirements Document (BRD) — Summary

### 3.1 Purpose

Provide secure, standards-compliant authentication for the LearnFlow Learning Management System so that learners, instructors, and administrators can register, access, and manage their accounts with confidence.

### 3.2 Scope

In Scope

Out of Scope (Future Phases)

Self-service registration with email + password

Social / OAuth login (Google, GitHub)

Email verification flow

Multi-factor authentication (TOTP / SMS)

Credential-based login

Role-based access control (RBAC) beyond basic `role` claim

JWT access + refresh token lifecycle

Single Sign-On (SSO / SAML)

Secure logout (single + all sessions)

Biometric authentication

Forgot-password / reset-password flow

Admin-initiated password reset

### 3.3 Technical Constraints & Decisions

Area

Decision

**Password hashing** 

bcrypt (cost factor 12) or argon2id; plaintext storage is a zero-tolerance violation

**Access token**

Signed JWT (HS256 or RS256), 15-minute expiry, carried in `Authorization: Bearer` header

**Refresh token**

Opaque or signed JWT, 7-day expiry, stored in an **httpOnly, Secure, SameSite=Strict** cookie

**Token revocation**

Refresh tokens tracked in a `refresh_tokens` PostgreSQL table (or Redis set) with a revoked/used flag

**Rate limiting**

5 failed logins per 15 min per email; 3 reset requests per hour per email — enforced at the FastAPI middleware or reverse-proxy layer

**Account enumeration prevention**

Login and reset endpoints always return generic messages regardless of email existence

**Email delivery**

Delegated to a transactional email provider (e.g., AWS SES, Resend, SendGrid); the system must not block on send

**Frontend token handling**

React 19 stores the access token in memory (not localStorage); refresh handled via silent cookie-based call to `/auth/refresh`

### 3.4 Data Model (Key Entities)

```
users
├── id              UUID  PK
├── full_name       VARCHAR(120)  NOT NULL
├── email           VARCHAR(255)  UNIQUE NOT NULL
├── password_hash   VARCHAR(255)  NOT NULL
├── is_verified     BOOLEAN       DEFAULT FALSE
├── is_active       BOOLEAN       DEFAULT TRUE
├── created_at      TIMESTAMPTZ
└── updated_at      TIMESTAMPTZ

refresh_tokens
├── id              UUID  PK
├── user_id         UUID  FK → users.id
├── token_hash      VARCHAR(255)  NOT NULL
├── expires_at      TIMESTAMPTZ   NOT NULL
├── is_revoked      BOOLEAN       DEFAULT FALSE
└── created_at      TIMESTAMPTZ

password_reset_tokens
├── id              UUID  PK
├── user_id         UUID  FK → users.id
├── token_hash      VARCHAR(255)  NOT NULL
├── expires_at      TIMESTAMPTZ   NOT NULL
├── is_used         BOOLEAN       DEFAULT FALSE
└── created_at      TIMESTAMPTZ
```
3.5 API Endpoint Summary
Method	Route							Purpose									Auth Required
POST	/auth/register					Create new account						No
GET		/auth/verify-email?token=		Confirm email address					No
POST	/auth/resend-verification		Resend verification email				No
POST	/auth/login						Authenticate and issue tokens			No
POST	/auth/refresh					Rotate access token						Refresh	cookie
POST	/auth/logout					Revoke current refresh token			Yes
POST	/auth/logout-all				Revoke all user sessions				Yes
POST	/auth/forgot-password			Send password reset email				No
POST	/auth/reset-password			Set new password with token				No (token-validated)

### 3.6 Non-Functional Requirements

Category

Requirement

**Security**

OWASP Top-10 compliance; all secrets in env vars, never committed; HTTPS enforced; CORS restricted to the React frontend origin

**Performance**

Login and registration endpoints respond within 500 ms at p95 under normal load

**Availability**

Auth service uptime target of 99.9 %

**Logging & Audit**

Every login attempt (success/failure), token issuance, revocation, and password reset event is logged with timestamp, IP, and user-agent (PII-safe)

**Data Privacy**

Passwords never logged or returned in API responses; reset tokens are single-use and hashed at rest

### 3.7 Success Metrics

Metric

Target

Registration-to-verified conversion rate

≥ 80 % within 24 h

Login failure rate (credential errors)

< 5 % of all attempts

Password reset link redemption rate

≥ 70 % of requests

Median login latency (p50)

< 300 ms

Plaintext password exposure incidents

**Zero**

### 3.8 Key Risks & Mitigations

Risk

Impact

Mitigation

Refresh token theft (XSS)

Session hijack

httpOnly + Secure + SameSite=Strict cookie; CSP headers; no localStorage for tokens

Brute-force attacks

Account compromise

Rate-limiting at middleware + reverse proxy; account lockout after 5 failures

Email provider outage

Users cannot verify/reset

Queue-based email dispatch with retry; fallback provider

JWT secret leak

All tokens forgeable

Secret rotated via env/vault; RS256 key pair preferred for production

Account enumeration

Privacy leakage / phishing prep

Generic responses on login failure and reset request