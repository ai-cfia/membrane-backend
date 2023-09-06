# Louis Single Sign-On (SSO) Documentation

This document outlines the Single Sign-On (SSO) process for the Louis application. We've broken it down into states and scenarios to provide a comprehensive understanding.

## States:

1. **INITIAL_STATE**: This is the initial state of the Louis Login back-end. Typically, it represents the starting point for the SSO process.
2. **AWAITING_EMAIL**: The system enters this state after the user is redirected to the Louis Login front-end and is awaiting the user's email input.
3. **EMAIL_SENT**: Once the user provides a valid email, and the system sends out the verification email, it transitions to this state.
4. **USER_AUTHENTICATED**: The system enters this state once the user clicks on the verification link from their email, and the token is validated.

## SSO Process Overview:

### 1. Client Application Visit:
- The user goes to the client application website.
- The client app checks for a session cookie to determine if the user is already logged in.
  - **Yes**: Redirect to the client application main page.
  - **No**: Check for a JWT token in the request from Louis Login Back-end.
    - **No**: Generate JWT token with app id & redirect URL, then redirect to Louis Login backend with JWT in the URL query.
    - **Yes**: Decode and validate the JWT to extract token information, then generate a session cookie.

### 2. Louis Login Back-end & Front-end Interaction:
- On receiving the JWT with app id and redirect URL, Louis Login back-end decodes the token.
- If valid, the system redirects the user to the Louis Login front-end, passing on the token in the URL query.
- At the Louis Login front-end, the user is prompted to enter their email address.

### 3. Email Verification Process:
- After the user submits a valid email, the system sends an HTTP request to Louis login.
- The back-end then generates and sends a verification link with a token to the provided email address.

### 4. Verification Link:
- The user clicks on the verification link.
- They are redirected to Louis Login back-end for link validation.
- If everything is in order, the user is redirected to the original client application where the SSO process starts again (refer to step 1). This time, a JWT is present in the request, and thus, a session cookie gets generated, transitioning the user to the main page.

## Error Handling Scenarios:

### Scenario 1: Verification Link in a Different Browser:
- If a user opens the verification link in a different browser, the state in this new browser is `INITIAL_STATE`.
- Despite being in `INITIAL_STATE`, the back-end processes the token from the verification link.
- If the token is valid, the system redirects the user to the client application.

### Scenario 2: Unexpected Token in `AWAITING_EMAIL` State:
- In the `AWAITING_EMAIL` state, if the back-end receives a URL token without an accompanying email JSON:
  - The system attempts to decode the token.
  - If it's a client JWT, it redirects the user back to the Louis Login front-end.
  - If it's a verification token, the token is processed, and if valid, the user is redirected to the client application.

### Scenario 3: Client JWT During `EMAIL_SENT` State:
- If the back-end in the `EMAIL_SENT` state receives a Client JWT (indicating a restart of the SSO process) instead of a verification link:
  - The system tries to decode the token.
  - If it's a valid client JWT, the user is redirected back to the Louis Login front-end.

---

This documentation provides a holistic view of the SSO process.