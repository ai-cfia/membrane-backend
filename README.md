## Setting Up a Quart Application

Follow the instructions below to set up a Quart application in your environment:

### 1. Check Pip Version:

Before you start, ensure you have `pip` installed. Check its version with:

```bash
pip --version
```

### 2. Upgrade Pip, Setuptools, and Virtualenv:

It's a good practice to keep your tools updated. Run the following command:

```bash
python -m pip install --upgrade pip setuptools virtualenv
```

### 3. Create a Virtual Environment:

To create an isolated environment for your project, set up a virtual environment named `venv` (or another name you prefer):

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment:

Before installing any packages, activate your virtual environment:

**On Windows:**

```bash
venv\Scripts\activate
```

### 5. Install Project Dependencies:

Ensure you have a `requirements.txt` file in your project directory. Install all dependencies with:

```bash
pip install -r requirements.txt
```

---

Now, you can proceed with running your Quart application or any other tasks. Always ensure that your virtual environment is activated when working on the project to maintain dependencies separately from your global Python environment.

## 6. Environment Variable Configuration:

To run the Quart application correctly, it requires some environment variables to be set. Follow the steps below to set them up:

1. Navigate to the root directory of the project and create a new file named `.env`.
2. Open this `.env` file using your preferred text editor.

Now, define each of the following variables:

### MEMBRANE_ALLOWED_ORIGINS

- **Description:** List of origins allowed for cross-origin requests (CORS).
- **Format:** Comma-separated list of domains.
- **Example:** `MEMBRANE_ALLOWED_ORIGINS=http://example.com,https://example2.com`

### MEMBRANE_SECRET_KEY

- **Description:** The secret key used for creating encrypted tokens.
- **Recommendation:** Generate a strong random value for this.

### MEMBRANE_CLIENT_PUBLIC_KEYS_DIRECTORY

- **Description:** Path to the directory where client public keys are stored for JWT validation.
- **Example:** `MEMBRANE_CLIENT_PUBLIC_KEYS_DIRECTORY=keys/public_keys`

### MEMBRANE_SERVER_PRIVATE_KEY

- **Description:** Path to the server's private key file used for creating and signing tokens.
- **Example:** `MEMBRANE_SERVER_PRIVATE_KEY=keys/server_private.pem`

### MEMBRANE_SERVER_PUBLIC_KEY

- **Description:** Path to the server's public key file used for verifying tokens.
- **Example:** `MEMBRANE_SERVER_PUBLIC_KEY=keys/server_public.pem`

### MEMBRANE_JWT_ACCESS_TOKEN_EXPIRE_SECONDS

- **Description:** Expiration time (in minutes) for the JWT access token.
- **Example:** `MEMBRANE_JWT_ACCESS_TOKEN_EXPIRE_SECONDS=30`

### MEMBRANE_JWT_EXPIRE_SECONDS

- **Description:** General JWT expiration time in minutes.
- **Example:** `MEMBRANE_JWT_EXPIRE_SECONDS=60`

### MEMBRANE_SESSION_LIFETIME_SECONDS

- **Description:** Duration (in minutes) after which the session will expire.
- **Example:** `MEMBRANE_SESSION_LIFETIME_SECONDS=30`

### MEMBRANE_SESSION_TYPE

- **Description:** Specifies the storage for session data. Options: 'filesystem', 'redis', 'memcached', etc.
- **Example:** `MEMBRANE_SESSION_TYPE=filesystem`

### MEMBRANE_LOGGING_LEVEL

- **Description:** Specifies the logging level for the application.
- **Example:** `MEMBRANE_LOGGING_LEVEL=INFO`

### MEMBRANE_ALLOWED_EMAIL_DOMAINS

- **Description:** List of email domains accepted by the application.
- **Format:** Comma-separated list of domains.
- **Example:** `MEMBRANE_ALLOWED_EMAIL_DOMAINS=gc.ca,canada.ca`

### MEMBRANE_COMM_CONNECTION_STRING

- **Description:** Connection string for the email service.
- **Example:** `MEMBRANE_COMM_CONNECTION_STRING=smtp://example.com:587`

### MEMBRANE_SENDER_EMAIL

- **Description:** Email address that will send emails.
- **Example:** `MEMBRANE_SENDER_EMAIL=noreply@example.com`

### MEMBRANE_EMAIL_SUBJECT

- **Description:** Subject line for outgoing emails.
- **Example:** `MEMBRANE_EMAIL_SUBJECT=Your Subject Here`

### MEMBRABE_EMAIL_SEND_SUCCESS

- **Description:** Indicates if the email was sent successfully.
- **Example:** `MEMBRABE_EMAIL_SEND_SUCCESS=true`

### MEMBRANE_FRONTEND

- **Description:** Redirect URL leading users to the login frontend.
- **Example:** `MEMBRANE_FRONTEND=https://login.membranefrontend.com/`

### MEMBRANE_EMAIL_SEND_POLLER_WAIT_TIME

- **Description:** Time to wait (in seconds) while polling for email sending status.
- **Example:** `MEMBRANE_EMAIL_SEND_POLLER_WAIT_TIME=10`

### MEMBRANE_EMAIL_SEND_HTLM_TEMPLATE

- **Description:** Path to the HTML template used for outgoing emails.
- **Example:** `MEMBRANE_EMAIL_SEND_HTLM_TEMPLATE=\<html>\<h1>{}\</h1>\</html>

### MEMBRANE_TOKEN_BLACKLIST

- **Description:** List of revoked tokens or sessions for security.
- **Format:** Comma-separated list of tokens.
- **Example:** `MEMBRANE_TOKEN_BLACKLIST=token1,token2`

Once you have defined all these variables, save and close the `.env` file. The Quart application will now use these environment variable values when it runs.

### 7. Run the Main Quart Application:

With your virtual environment activated, start the main `app.py`:

```bash
quart run
```

### 8. Simulate a Client Application:

Open a separate terminal or command prompt. Make sure the virtual environment is activated and then run the `testapp1.py` to simulate a client application:

```bash
quart --app testapp1.py run --port=4000
```

### 9. Interact with Louis Login Frontend:

Ensure that the Louis Login Frontend React application is running, ideally on `localhost`. This application will serve as the frontend interface for users to provide their email addresses to Louis Login Backend.

---

You can now interact with both the main Quart application and the client simulator to validate the entire authentication flow.

## Running the app from dockerfile

### 1. Generate Server, Client Keys, and Environment Files

#### Prerequisites

- OpenSSL installed on your machine (in WSL).
- An Azure Communication Service connection string
- An Azure MailFrom email address connected to the Azure Communication Service resource

#### Steps

1. Navigate to the project's root directory.
2. Run the initialization script:

   ```bash
   ./init_project.sh <your-test-app-id>
   ```

   This script will:

   - Generate keys in a `keys` folder for both the server and the specified app id.
   - Copy `.env.template` to `.env`.
   - Copy `.env.tests.template` to `.env.tests`.

#### Note

- If the keys or environment files already exist, the script will overwrite them.
- Logs are written to `init.log`.

### 2. Configure Environment Variables

1. Open the `.env` file generated in the project's root directory.
2. Generate a secret key:

   ```bash
   openssl rand -hex 32
   ```

3. Populate the following variables in the `.env` file:

   ```
   # CORS settings
   MEMBRANE_ALLOWED_ORIGINS=#comma separated urls to connected frontends

   # Frontend
   MEMBRANE_FRONTEND=#the membrane frontend url

   # Secrets and Keys
   MEMBRANE_SECRET_KEY=#your secret key generated at step 2
   MEMBRANE_CLIENT_PUBLIC_KEYS_DIRECTORY=keys/
   MEMBRANE_SERVER_PRIVATE_KEY=keys/server_private_key.pem
   MEMBRANE_SERVER_PUBLIC_KEY=keys/server_public_key.pem

   # JWT and Session settings
   MEMBRANE_JWT_ACCESS_TOKEN_EXPIRE_SECONDS=4
   MEMBRANE_JWT_EXPIRE_SECONDS=4
   MEMBRANE_SESSION_LIFETIME_SECONDS=4
   MEMBRANE_SESSION_TYPE=null

   # Logging and Debugging
   MEMBRANE_LOGGING_LEVEL=DEBUG

   # Email settings
   MEMBRANE_ALLOWED_EMAIL_DOMAINS=gc.ca,canada.ca,inspection.gc.ca
   MEMBRANE_COMM_CONNECTION_STRING=#your azure communication service connection string
   MEMBRANE_SENDER_EMAIL=#your azure mailfrom email address
   MEMBRANE_EMAIL_SUBJECT=Please Verify Your Email Address
   MEMBRABE_EMAIL_SEND_SUCCESS=Valid email address. Email sent with JWT link
   ```

### 3. Running the App with Docker

1. Build the Docker image:

   ```bash
   docker build -t your_app_name .
   ```

2. Set your desired port number:

   ```bash
   export PORT=<your_port_here>
   ```

3. Run the Docker container:

   ```bash
   docker run -v $(pwd)/keys:/app/keys -p $PORT:$PORT -e PORT=$PORT --env-file .env your_app_name
   ```
