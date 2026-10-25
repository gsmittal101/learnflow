LearnFlow LSM: User Registration & Authentication
Brief: "Let users register and log into LearnFlow." Scope: Registration, login, JWT issuing, password reset Stack context: FastAPI (API), React 19 (UI), PostgreSQL 17 (persistence), JWT (session/auth tokens)
1. User Stories 
US-01: Registration
As a new learner, I want to create an account with my email and a password, so that I can access LearnFlow and have my progress saved.
US-02: Email Verification
As a new learner, I want to confirm my email address after registering, so that my account is verified and protected from misuse by others.
US-03: Login
As a registered user, I want to log in with my email and password, so that I can securely access my learning content and progress.
US-04: JWT Issuing
As a logged-in user, I want the system to issue me a short-lived access token and a renewable refresh token, so that I stay signed in across sessions without re-entering credentials constantly.
US-05: Logout
As a logged-in user, I want to log out and have my session invalidated, so that nobody else can use my account on a shared device.
US-06: Password Reset Request
As a user who forgot my password, I want to request a reset link by email, so that I can regain access without contacting support.
US-07: Password Reset Completion
As a user with a valid reset link, I want to set a new password, so that I can log in again and my old password is no longer valid.
US-08: Protected Access
As a platform owner, I want protected API endpoints to reject missing, expired, or tampered tokens, so that learner data is only accessible to authenticated users.
2. Acceptance Criteria
AC for US-01: Registration
ID
Given
When
Then
AC-01.1
I am on the registration page
I submit a valid email, a password meeting policy, and accept the terms
An account is created in pending_verification status and I see a confirmation message
AC-01.2
An account already exists for the email
I attempt to register with it
The response is generic ("Check your email") and does not reveal that the email is registered
AC-01.3
I am on the registration page
I submit an invalid email format
The form shows an inline validation error and no API call creates an account
AC-01.4
I am on the registration page
I submit a password that violates policy (min 12 characters, mixed character types, not on common-password list)
The API returns HTTP 422 with field-level errors
AC-01.5
An account is created
The record is persisted
The password is stored only as a salted hash (Argon2id or bcrypt), never in plaintext
AC-01.6
A client sends many registration requests
The rate limit is exceeded
The API returns HTTP 429
AC for US-02: Email Verification
ID
Given
When
Then
AC-02.1
I have registered
The system processes my registration
A single-use verification link is emailed, valid for 24 hours
AC-02.2
I have a valid verification link
I open it
My account status becomes active and I am directed to login
AC-02.3
My verification link is expired or already used
I open it
I see an error and an option to request a new link
AC for US-03: Login
ID
Given
When
Then
AC-03.1
I have an active account
I submit correct credentials
I am authenticated and redirected to my dashboard
AC-03.2
I submit a wrong password or unknown email
The login is processed
The API returns HTTP 401 with one generic message ("Invalid email or password")
AC-03.3
My account is pending_verification
I attempt to log in
Login is denied with a prompt to verify my email, with a resend option
AC-03.4
I have 5 consecutive failed attempts
I try again
The account or IP is temporarily locked for 15 minutes and the attempt is logged
AC-03.5
I am on the login page
I check the form
Submission is over HTTPS only and the password field is masked
AC for US-04: JWT Issuing
ID
Given
When
Then
AC-04.1
I authenticate successfully
The API responds
An access token (15 min expiry) and a refresh token (7 days expiry) are issued
AC-04.2
An access token is issued
I decode its claims
It contains sub (user ID), iat, exp, jti, and role, and contains no password, email, or other sensitive data
AC-04.3
Tokens are issued
They are signed
Signing uses a server-side secret or key (HS256 minimum, RS256 preferred) kept outside source control
AC-04.4
My access token expires
The client sends my valid refresh token
A new access token is issued and the refresh token is rotated, with the old one invalidated
AC-04.5
A rotated refresh token is presented again
The API receives it
The token family is revoked and the user must log in again
AC-04.6
The refresh token is delivered to the browser
It is stored
It is set as an HttpOnly, Secure, SameSite cookie, and the access token is held in memory only
AC for US-05: Logout
ID
Given
When
Then
AC-05.1
I am logged in
I click Logout
My refresh token is revoked server-side, the cookie is cleared, and I am returned to the login page
AC-05.2
I have logged out
I reuse my old refresh token
The API returns HTTP 401
AC for US-06: Password Reset Request
ID
Given
When
Then
AC-06.1
I am on the "Forgot password" page
I submit any email address
The response is always the same generic confirmation, whether or not an account exists
AC-06.2
The email belongs to an active account
The request is processed
A single-use reset link is emailed, valid for 30 minutes
AC-06.3
I request a reset again
A previous link is still unused
The previous link is invalidated and only the latest is valid
AC-06.4
Reset requests exceed the rate limit
The next request arrives
The API returns HTTP 429
AC for US-07: Password Reset Completion
ID
Given
When
Then
AC-07.1
I have a valid reset link
I submit a new password meeting policy
My password is updated, the link is consumed, and I am prompted to log in
AC-07.2
My password is reset
The change is saved
All of my existing refresh tokens are revoked, and a notification email is sent
AC-07.3
My reset link is expired, used, or invalid
I submit a new password
The API returns an error and I am offered a new reset request
AC-07.4
I submit a new password
It matches my current password
The change is rejected with a policy message
AC for US-08: Protected Access
ID
Given
When
Then
AC-08.1
A request to a protected endpoint has no token
The API receives it
It returns HTTP 401
AC-08.2
A request carries an expired or tampered token
The API validates it
It returns HTTP 401 and logs the event
AC-08.3
A valid token lacks the required role
It calls a role-restricted endpoint
The API returns HTTP 403
3. BRD Section: User Registration & Authentication
3.1 Purpose
Provide secure self-service account creation and authentication for LearnFlow LSM, so that learners can access personalised content and progress tracking, and so that the platform can enforce identity-based access control from the outset.
3.2 Business Objectives
• Reduce onboarding friction so new learners reach their first course quickly.
• Protect learner data and meet privacy obligations.
• Reduce support load through self-service password recovery.
• Establish an identity foundation for later features (roles, enrolment, reporting, SSO).
3.3 Scope
In scope
Out of scope (this release)
Email/password registration
Social login / SSO (Google, Microsoft, SAML)
Email verification
Multi-factor authentication
Login and logout
Admin user management console
JWT access and refresh tokens
Account deletion and data export
Password reset by email
Fine-grained RBAC beyond a basic role claim
3.4 Stakeholders
Product Owner, LearnFlow LSM engineering (backend, frontend), Security/InfoSec, Customer Support, Compliance/Privacy, Learners (end users).
3.5 Functional Requirements
ID
Requirement
Priority
Stories
FR-01
The system shall allow account registration with email and password.
Must
US-01
FR-02
The system shall verify email ownership via a single-use, expiring link.
Must
US-02
FR-03
The system shall authenticate users with email and password.
Must
US-03
FR-04
The system shall issue short-lived access JWTs and rotating refresh tokens.
Must
US-04
FR-05
The system shall allow users to log out and revoke their refresh tokens.
Must
US-05
FR-06
The system shall support password reset via a single-use, expiring emailed link.
Must
US-06, US-07
FR-07
The system shall reject unauthenticated or invalid-token requests to protected endpoints.
Must
US-08
FR-08
The system shall rate-limit and lock out repeated failed or abusive requests.
Must
US-01, 03, 06
3.6 Non-Functional Requirements
Category
Requirement
Security
Passwords hashed with Argon2id or bcrypt. All traffic over TLS. Generic error messages to prevent account enumeration. JWT signing keys stored in a secrets manager.
Performance
Login and token refresh respond in under 500 ms at p95 under expected load.
Availability
Authentication service meets the platform availability target (proposed 99.9%).
Auditability
Registration, login success and failure, lockout, reset, and token revocation events are logged with timestamp and user or IP reference, excluding secrets.
Privacy
Only the minimum personal data is collected. Compliance with applicable privacy law (e.g. NZ Privacy Act 2020, GDPR where relevant) to be confirmed with Compliance.
Usability
Responsive UI with inline validation and accessible forms (WCAG 2.1 AA target).
Maintainability
Auth endpoints documented in the OpenAPI schema generated by FastAPI.
3.7 Data Requirements (indicative)
• users: id (UUID), email (unique, case-insensitive), password_hash, status, role, created_at, verified_at, last_login_at, failed_attempts, locked_until.
• refresh_tokens: id, user_id, token_hash, family_id, expires_at, revoked_at.
• email_tokens: id, user_id, type (verify/reset), token_hash, expires_at, used_at.
Tokens are stored hashed, never in plaintext.
3.8 Indicative API Surface
Endpoint
Purpose
POST /auth/register
Create account
POST /auth/verify-email
Confirm email
POST /auth/login
Authenticate and issue tokens
POST /auth/refresh
Rotate refresh token, issue new access token
POST /auth/logout
Revoke refresh token
POST /auth/password/forgot
Request reset link
POST /auth/password/reset
Complete reset
3.9 Assumptions
• A transactional email service is available (provider to be selected).
• Email is the unique user identifier.
• The React 19 SPA and FastAPI API are served from domains that support secure, same-site cookie handling.
3.10 Dependencies and Risks
Risk / Dependency
Mitigation
Email delivery failures block verification and reset
Choose a reliable provider, monitor bounces, offer resend
Credential stuffing and brute force
Rate limiting, lockout, common-password checks; consider MFA in a later release
Token theft via XSS or CSRF
HttpOnly cookies for refresh tokens, in-memory access tokens, CSRF protection on cookie-based endpoints
Signing key compromise
Key rotation procedure and secrets manager
3.11 Success Metrics
• Registration completion rate (form start to verified account)
• Median time from registration to first login
• Password reset completion rate
• Auth-related support ticket volume
• Login failure rate and lockout rate (security signal)
3.12 Open Questions
1. Is email verification mandatory before first login, or can users access limited content while unverified?
2. What are the required token lifetimes and session length policy?
3. Is SSO or MFA expected within the next release cycle?
4. Are there age restrictions or consent requirements (e.g. learners under 16) affecting registration?
5. What are the data residency requirements for stored user data?
4. Authentication Edge Cases
This section enumerates edge cases for four scenarios and gives Given/When/Then acceptance criteria for each. Where an edge case refines an earlier criterion, the original AC ID is shown in the last column.
4.1 Duplicate Email
Edge cases
• Same email registered again by the same or another person
• Same email differing only by letter case or surrounding whitespace
• Existing account is still pending_verification
• Two registration requests for the same email arrive at the same moment (race condition)
ID
Given
When
Then
Refines
EC-DUP.1
An active account exists for jane@example.com
Someone registers with jane@example.com
The API returns the same generic response as a successful registration, no second account is created, and the account owner receives a "someone tried to register with your email" notice
AC-01.2
EC-DUP.2
An account exists for jane@example.com
Someone registers with Jane@Example.com
The email is trimmed and lower-cased before comparison, it is treated as a duplicate, and the response follows EC-DUP.1
AC-01.2
EC-DUP.3
An account exists in pending_verification for the email
Someone registers with it again
No new account is created, the earlier verification link is invalidated, a fresh link is sent, and the response is the same generic message
AC-01.2, AC-02.1
EC-DUP.4
No account exists for the email
Two registration requests for it are processed simultaneously
Exactly one account is created, enforced by a unique index on the normalised email in PostgreSQL, and the other request receives the same generic response rather than a 500 error
AC-01.2
EC-DUP.5
A duplicate registration is attempted
The response is returned
Response body, status code, and response time are indistinguishable from a new registration, so the email's registration status cannot be inferred
AC-01.2
4.2 Weak Password
Edge cases
• Password below minimum length
• Password on a common or breached-password list
• Password contains the user's email or name
• Password with only one character type
• Very long password (hashing denial-of-service)
• Unicode and whitespace characters
• Policy bypass through the reset flow
ID
Given
When
Then
Refines
EC-PWD.1
I am registering or resetting my password
I submit fewer than 12 characters
The API returns HTTP 422 with a field-level error stating the minimum length, and no account or password change is saved
AC-01.4
EC-PWD.2
I am registering or resetting my password
I submit a password on the common-password or breached list (e.g. Password123456)
The API returns HTTP 422 with a message that the password is too common
AC-01.4
EC-PWD.3
I am registering
My password contains my email local-part or display name
The API returns HTTP 422 with a message that the password must not contain personal information
AC-01.4
EC-PWD.4
I am registering or resetting my password
I submit a password that uses only one character type
The API returns HTTP 422 listing the unmet composition rules
AC-01.4
EC-PWD.5
I am registering or resetting my password
I submit a password longer than 128 characters
The API rejects it with HTTP 422 before hashing, so oversized input cannot exhaust server resources
AC-01.4
EC-PWD.6
I am registering or resetting my password
I submit a valid passphrase containing spaces or Unicode characters
It is accepted and normalised consistently (NFKC), and can be used to log in later
AC-01.1
EC-PWD.7
The registration form is open
I type a weak password
The UI shows live strength feedback, but the server remains the authority and re-validates every submission
AC-01.3
EC-PWD.8
A weak password is rejected
The error is logged
The password value is never written to logs or error traces
AC-01.5
4.3 Expired Token
Edge cases
• Expired access token
• Expired refresh token
• Expired email verification link
• Expired password reset link
• Token expiring mid-request or during a long form fill
• Clock skew between servers
• Tampered or malformed token
ID
Given
When
Then
Refines
EC-TOK.1
My access token has expired and my refresh token is valid
The SPA calls a protected endpoint
The API returns HTTP 401 with a token-expired code, the React client silently calls /auth/refresh once, retries the original request, and I notice nothing
AC-04.4, AC-08.2
EC-TOK.2
My refresh token has expired
The client attempts to refresh
The API returns HTTP 401, the client clears in-memory state, and I am redirected to login with a "session expired" message and my return path preserved
AC-04.1
EC-TOK.3
Several requests fail at the same moment because the access token expired
The client handles the failures
Only one refresh call is made, and the other requests wait for it and then retry, so the refresh token is not rotated multiple times
AC-04.4
EC-TOK.4
I open an email verification link older than 24 hours
The API validates it
The account stays pending_verification, I see an "expired link" page, and I can request a new link
AC-02.3
EC-TOK.5
I open a password reset link older than 30 minutes
I submit a new password
The API returns an error, the password is unchanged, and I am offered a new reset request
AC-07.3
EC-TOK.6
A token's exp is within the allowed clock-skew leeway (30 seconds)
The API validates it
The token is accepted, and a token beyond the leeway is rejected
AC-08.2
EC-TOK.7
A request carries a token with an altered payload, wrong signature, alg: none, or malformed structure
The API validates it
The API returns HTTP 401, logs the event without the token value, and counts it toward abuse monitoring
AC-08.2
EC-TOK.8
I am typing a new password when the reset link's validity ends
I submit the form
The API rejects it as expired and the form explains that a new link is needed, without losing the user's place in the flow
AC-07.3
4.4 Password Reset for a Non-Existing Account
Edge cases
• Email not registered at all
• Email malformed
• Account exists but is pending_verification or locked
• Timing differences revealing whether the account exists
• Repeated requests used to harvest registered emails
ID
Given
When
Then
Refines
EC-RST.1
No account exists for nobody@example.com
I submit it on the "Forgot password" page
The API returns the same generic confirmation ("If an account exists, we have sent a reset link") and HTTP status as for a real account
AC-06.1
EC-RST.2
No account exists for the email
The request is processed
No reset token is created and no email is sent, though the request is logged internally
AC-06.1
EC-RST.3
The request is for a non-existing account
The response is returned
Response time is within normal variance of a real-account request (for example, by queuing email work asynchronously), so timing cannot reveal account existence
AC-06.1
EC-RST.4
I submit a malformed email address
The form is validated
The UI shows an inline format error and the API returns HTTP 422, which discloses nothing about registered accounts
AC-01.3
EC-RST.5
The email belongs to a pending_verification account
I request a reset
The generic confirmation is shown, and the user receives a verification link instead of a reset link
AC-06.2, AC-02.1
EC-RST.6
A client submits many reset requests for different emails
The rate limit per IP and per email is exceeded
The API returns HTTP 429, which limits email enumeration and mailbox flooding
AC-06.4
EC-RST.7
A real account owner receives an unexpected reset email
They ignore it
Nothing changes: the password remains valid until a reset is completed, and the link expires after 30 minutes
AC-06.2
4.5 Open Points from the Edge-Case Review
1. Should a "someone tried to register with your email" notice (EC-DUP.1) be sent, given the risk of email spam toward the account owner?
2. Should a breached-password check call an external service (such as a k-anonymity API) or use a bundled list only?
3. What is the maximum accepted password length (proposed 128 characters)?
4. Is clock-skew leeway of 30 seconds acceptable to Security?
