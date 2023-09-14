# Louis Login Backend

Louis Login Backend is a centralized authentication system designed for Single Sign-On (SSO) functionality. It streamlines user authentication across multiple client applications by providing a seamless flow for token-based email verification.

## Workflow Overview:

### 1. Client Application Check
* The user accesses the client application website.
* The application checks for a session cookie to determine if the user is already authenticated.
  * If a session cookie exists: The user is redirected to the client application's main page.
  * If no session cookie:
    * The application checks for a JWT token from Louis Login Backend.
      * If no JWT token: 
        1. The application generates a JWT token containing an app ID and a redirect URL.
        2. It then redirects the user to Louis Login Frontend, passing the JWT in the URL query.
      * If JWT token exists:
        1. The token is decoded and validated to extract the information.
        2. A session cookie is generated.

### 2. Interaction with Louis Login Backend
* If the client application doesn't have a session cookie and has been redirected to the Louis Login Backend with a JWT:
  * Louis Login Backend decodes and validates the token.
  * If the token is valid, the user is redirected to the Louis Login Front-end, with the token passed along in the URL query.
  * At the Louis Login Front-end, the user is prompted to input their email address to receive a verification link.

### 3. Email Verification
* On submission of a valid email:
  * An HTTP request is sent to Louis Login Backend containing the email.
  * A verification link embedded with a token is generated and dispatched to the provided email address.

### 4. Link Verification & Redirection
* The user clicks the verification link, initiating a redirection to Louis Login Backend.
* The link is validated, and if all checks pass, the user is directed back to the original client application.
* The client application then revisits Step 1, this time recognizing the JWT from Louis Login Backend, decoding and validating it to generate a session cookie. The user is finally led to the main page, completing the SSO process.

## API Endpoint: `authenticate`

This endpoint performs multifaceted duties:

* **Client JWT & No Email**:
  * The request originates from the client application.
  * Louis Login Backend validates the token.
  * If valid, the user is redirected to Louis Login Front-end to provide an email address.

* **Client JWT & Email**:
  * Louis Login Backend processes the JWT and email.
  * If both are valid, a verification link embedded with a token is generated and emailed to the user.

* **No Client JWT & Verification Token**:
  * Indicates an attempt to verify an email link.
  * The user is redirected back to the initiating client application.
  * The client application then processes and establishes a signed-in session cookie.

---
## Workflow Sequence Diagram:

![Workflow Diagram](./diagrams/Louis%20Login%20Backend%20Sequence%20Diagram.png)
