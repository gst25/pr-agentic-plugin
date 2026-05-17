# Sample PRD: Forgot Password Feature

## Overview
Add a "Forgot Password" flow to the User Management application. Users should be able to request a password reset via their registered email address, receive a secure token, and use it to set a new password.

## User Stories

### US-1: Request Password Reset
**As a** registered user,
**I want to** request a password reset by providing my email,
**So that** I can regain access to my account if I forget my password.

### US-2: Reset Password with Token
**As a** user who requested a reset,
**I want to** use the token I received to set a new password,
**So that** my account is secured with a new password of my choice.

## Acceptance Criteria

### For US-1 (Request Reset):
- POST `/api/auth/forgot-password` accepts `{ "email": "user@example.com" }`.
- If the email exists, generate a UUID token and store it in a `password_reset_tokens` table.
- Token must expire after 15 minutes.
- API returns `200 OK` with `{ "message": "If the email exists, a reset link has been sent." }` (do not reveal whether the email exists).
- If the email does not exist, still return the same 200 response (security best practice).

### For US-2 (Reset Password):
- POST `/api/auth/reset-password` accepts `{ "token": "uuid-token", "newPassword": "SecurePass123!" }`.
- Validate the token exists and has not expired.
- If valid, update the user's password (hashed with BCrypt) and delete the token.
- If invalid or expired, return `400 Bad Request` with an error message.

## Technical Notes
- Use Spring Boot's `@RestController`.
- Password must be hashed using BCryptPasswordEncoder.
- Token should be stored in a new JPA entity `PasswordResetToken` with fields: `id`, `token`, `userId`, `expiresAt`, `createdAt`.
