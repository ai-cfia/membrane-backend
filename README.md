<<<<<<< HEAD
## Work Flow

Louis Login Backend offers a comprehensive workflow that ensures a seamless Single Sign-On (SSO) experience. The system operates through a series of steps starting from the client application check to email verification and eventual redirection after verification. 

For a detailed step-by-step breakdown and to understand how the API endpoints function within this process, please refer to the [WORKFLOW documentation](./WORKFLOW.md).

## Setting Up a Flask Application
=======
Membrane-Backend is a Single Sign-On (SSO) solution specifically designed for AI-Lab products. This repository contains two key components:
>>>>>>> c2d29b5 (issue #35: update README)

1. **SSO Server**: A centralized authentication and authorization service built with Flask, designed to provide a single point of entry for multiple services within the AI-Lab ecosystem.

<<<<<<< HEAD
### Using virtual environment

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
=======
2. **Client Packages**: These are the required packages that need to be installed on client backends to enable Membrane functionality. These packages facilitate secure and seamless interaction with the SSO server.
>>>>>>> c2d29b5 (issue #35: update README)

---

## Server

<<<<<<< HEAD
##  Environment Variable Configuration:

To run the Flask application correctly, it requires some environment variables to be set. Follow the steps below to set them up:

1. Navigate to the root directory of the project and create a new file named `.env`.
2. Open this `.env` file using your preferred text editor.

Now, define each of the following variables:

### Mandatory Variables

#### MEMBRANE_CORS_ALLOWED_ORIGINS

- **Description:** List of origins allowed for cross-origin requests (CORS).
- **Format:** Comma-separated list of origins.
- **Example:** `MEMBRANE_CORS_ALLOWED_ORIGINS=http://localhost:3000`
- **Reference:** https://pypi.org/project/flask-cors/

#### MEMBRANE_FRONTEND

- **Description:** Redirect URL leading users to the login frontend.
- **Example:** `MEMBRANE_FRONTEND=http://localhost:3000`

#### MEMBRANE_SECRET_KEY

- **Description:** The secret key used for creating encrypted tokens.
- **Example:** `MEMBRANE_SECRET_KEY=your_secret_key`
- **Reference:** https://flask.palletsprojects.com/en/latest/config/#builtin-configuration-values

#### MEMBRANE_CLIENT_PUBLIC_KEYS_DIRECTORY

- **Description:** Path to the directory where client public keys are stored for JWT validation.
- **Example:** `MEMBRANE_CLIENT_PUBLIC_KEYS_DIRECTORY=keys/`

#### MEMBRANE_SERVER_PRIVATE_KEY

- **Description:** Path to the server's private key file used for creating and signing tokens.
- **Example:** `MEMBRANE_SERVER_PRIVATE_KEY=keys/server_private_key.pem`

#### MEMBRANE_SERVER_PUBLIC_KEY

- **Description:** Path to the server's public key file used for verifying tokens.
- **Example:** `MEMBRANE_SERVER_PUBLIC_KEY=keys/server_public_key.pem`

#### MEMBRANE_COMM_CONNECTION_STRING

- **Description:** Connection string for the Azure communication service.
- **Example:** `MEMBRANE_COMM_CONNECTION_STRING=your_azure_communication_service_connection_string`
- **Reference:** https://learn.microsoft.com/en-us/python/api/azure-communication-email/azure.communication.email.emailclient?view=azure-python#azure-communication-email-emailclient-from-connection-string

#### MEMBRANE_SENDER_EMAIL

- **Description:** Email address that will send emails.
- **Example:** `MEMBRANE_SENDER_EMAIL=DoNotReply@your_domain.com`
- **Reference:** https://learn.microsoft.com/en-us/python/api/overview/azure/communication-email-readme?view=azure-python#send-an-email-message

#### MEMBRANE_SESSION_TYPE

- **Description:** Specifies the storage for session data. Options: 'filesystem', 'redis', 'memcached', etc.
- **Example:** `MEMBRANE_SESSION_TYPE=filesystem`
- **Reference** https://flask-session.readthedocs.io/en/latest/config.html

### Optional Variables

#### MEMBRANE_JWT_ACCESS_TOKEN_EXPIRE_SECONDS

- **Description:** Expiration time (in seconds) for the JWT access token.
- **Example:** `MEMBRANE_JWT_ACCESS_TOKEN_EXPIRE_SECONDS=300`

#### MEMBRANE_JWT_EXPIRE_SECONDS

- **Description:** General JWT expiration time in seconds.
- **Example:** `MEMBRANE_JWT_EXPIRE_SECONDS=300`

#### MEMBRANE_SESSION_LIFETIME_SECONDS

- **Description:** Duration (in seconds) after which the session will expire.
- **Example:** `MEMBRANE_SESSION_LIFETIME_SECONDS=300`
- **Reference** https://flask-session.readthedocs.io/en/latest/config.html

#### MEMBRANE_SESSION_COOKIE_SECURE

- **Description:** Indicates if the session cookie should be secure.
- **Example:** `MEMBRANE_SESSION_COOKIE_SECURE=true`
- **Reference** https://flask-session.readthedocs.io/en/latest/config.html

#### MEMBRANE_TOKEN_BLACKLIST

- **Description:** List of revoked tokens or sessions for security.
- **Format:** Comma-separated list of tokens.
- **Example:** `MEMBRANE_TOKEN_BLACKLIST=`

#### MEMBRANE_APP_ID_FIELD

- **Description:** Field name for the application ID in JWT.
- **Example:** `MEMBRANE_APP_ID_FIELD=app_id`

#### MEMBRANE_DATA_FIELD

- **Description:** Field name for data in JWT.
- **Example:** `MEMBRANE_DATA_FIELD=data`

#### MEMBRANE_REDIRECT_URL_FIELD

- **Description:** Field name for redirect URL in JWT.
- **Example:** `MEMBRANE_REDIRECT_URL_FIELD=redirect_url`

#### MEMBRANE_ENCODE_ALGORITHM

- **Description:** Algorithm used for encoding JWT.
- **Example:** `MEMBRANE_ENCODE_ALGORITHM=RS256`
- **Reference:** https://pyjwt.readthedocs.io/en/latest/algorithms.html#digital-signature-algorithms

#### MEMBRANE_ALLOWED_EMAIL_DOMAINS_PATTERN

- **Description:** Regex for the list of email domains accepted by the application.
- **Example:** `MEMBRANE_ALLOWED_EMAIL_DOMAINS_PATTERN=^[a-zA-Z0-9._+]+@(?:gc\.ca|canada\.ca|inspection\.gc\.ca)$`

#### MEMBRANE_EMAIL_SUBJECT

- **Description:** Subject line for outgoing emails.
- **Example:** `MEMBRANE_EMAIL_SUBJECT=Please Verify Your Email Address`
- **Reference:** https://learn.microsoft.com/en-us/python/api/overview/azure/communication-email-readme?view=azure-python#send-an-email-message

#### MEMBRANE_EMAIL_SEND_HTML_TEMPLATE

- **Description:** HTML template for outgoing emails.
- **Example:** `MEMBRANE_EMAIL_SEND_HTML_TEMPLATE=<html><h1>{}</h1></html>`
- **Reference:** https://learn.microsoft.com/en-us/python/api/overview/azure/communication-email-readme?view=azure-python#send-an-email-message

#### MEMBRANE_EMAIL_SEND_POLLER_WAIT_TIME

- **Description:** Time in seconds to wait for email sending.
- **Example:** `MEMBRANE_EMAIL_SEND_POLLER_WAIT_TIME=2`
- **Reference:** https://learn.microsoft.com/en-us/python/api/azure-core/azure.core.polling.lropoller?view=azure-python#azure-core-polling-lropoller-wait

#### MEMBRANE_EMAIL_SEND_TIMEOUT_SECONDS

- **Description:** Time in seconds before email sending times out.
- **Example:** `MEMBRANE_EMAIL_SEND_TIMEOUT_SECONDS=30`

#### MEMBRANE_EMAIL_SEND_SUCCESS

- **Description:** Message when an email is successfully sent.
- **Example:** `MEMBRANE_EMAIL_SEND_SUCCESS=Valid email address, Email sent with JWT link`

#### MEMBRANE_GENERIC_500_ERROR_FIELD

- **Description:** Field name for generic 500 errors.
- **Example:** `MEMBRANE_GENERIC_500_ERROR_FIELD=error`

#### MEMBRANE_GENERIC_500_ERROR

- **Description:** Generic error message for 500 status code.
- **Example:** `MEMBRANE_GENERIC_500_ERROR=An unexpected error occurred. Please try again later.`

#### MEMBRANE_LOGGING_LEVEL

- **Description:** Specifies the logging level for the application.
- **Example:** `MEMBRANE_LOGGING_LEVEL=DEBUG`
- **Reference:** https://docs.python.org/3/library/logging.html#logging-levels

#### MEMBRANE_LOGGING_FORMAT

- **Description:** Format for the log messages.
- **Example:** `MEMBRANE_LOGGING_FORMAT=[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d:%(funcName)s] - %(message)s`
- **Reference:** https://docs.python.org/3/library/logging.html#logrecord-attributes


#### MEMBRANE_HEALTH_MESSAGE

- **Description:** Health check message for the server.
- **Example:** `MEMBRANE_HEALTH_MESSAGE=ok`

#### MEMBRANE_WORKERS

- **Description:** Number of hypercorn worker processes for the application.
- **Example:** `MEMBRANE_WORKERS=4`
- **Reference:** https://hypercorn.readthedocs.io/en/latest/how_to_guides/configuring.html

#### MEMBRANE_KEEP_ALIVE

- **Description:** Hypercorn keep-alive timeout in seconds for the server.
- **Example:** `MEMBRANE_KEEP_ALIVE=5`
- **Reference:** https://hypercorn.readthedocs.io/en/latest/how_to_guides/configuring.html

Once you have defined all these variables, save and close the `.env` file. The Flask application will now use these environment variable values when it runs.

<<<<<<< HEAD
### Running the App Locally

### 1. Run the Main Quart Application:
=======
### 7. Run the Main Flask Application:
>>>>>>> 405160b (issue #35: revert from quart to flask)

With your virtual environment activated, start the main `app.py`:
=======
### Getting Started

#### Cloning the repository
>>>>>>> c2d29b5 (issue #35: update README)

```bash
git clone https://github.com/ai-cfia/membrane-backend.git
```

<<<<<<< HEAD
### 2. Simulate a Client Application:
=======
#### Configuration
>>>>>>> c2d29b5 (issue #35: update README)

1. Navigate: `cd membrane-backend`
2. Run `./init-server.sh` to create necessary server resources.
3. Run `./add-client-app.sh <your-client-app-name>` to create a client key pair.
4. Edit the `.env` file.

#### Running the server

<<<<<<< HEAD
### 3. Interact with Membrane Frontend:
=======
1. **Using VS Code DevContainer**
>>>>>>> c2d29b5 (issue #35: update README)

   - **Prerequisites**: VS Code, Docker
   - **Open in VS Code**: `code .`
   - **Start DevContainer**: Click "Reopen in Container" in VS Code.
   - **Run**: `flask run --port=<your_port>`

2. **Using Dockerfile**

   - **Prerequisites**: Docker
   - **Build**: `docker build -t membrane-backend .`
   - **Run**: `export PORT=<your_port> && docker run -v $(pwd)/keys:/app/keys -p $PORT:$PORT -e PORT=$PORT --env-file .env <your_app_name>`

3. **Running without Containers**

   - **Prerequisites**: Python 3.11, pip
   - **Setup Virtual Environment**: `python -m venv venv && source venv/bin/activate`
   - **Install Dependencies**: `pip install -r requirements.txt`
   - **Run**: `export PORT=<your_port> && gunicorn -b :$PORT app:app`

---

## Client Packages

<<<<<<< HEAD
### Setting Up the App

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

3. Populate the following variables in the `.env` file. Example for tests and dev:

   ```env
   # Mandatory
   MEMBRANE_CORS_ALLOWED_ORIGINS=http://localhost:3000
   MEMBRANE_FRONTEND=http://localhost:3000
   MEMBRANE_SECRET_KEY=your_secret_key
   MEMBRANE_CLIENT_PUBLIC_KEYS_DIRECTORY=keys/
   MEMBRANE_SERVER_PRIVATE_KEY=keys/server_private_key.pem
   MEMBRANE_SERVER_PUBLIC_KEY=keys/server_public_key.pem
   MEMBRANE_COMM_CONNECTION_STRING=your_azure_communication_service_connection_string
   MEMBRANE_SENDER_EMAIL=DoNotReply@your_domain.com

   # Optional
   # MEMBRANE_JWT_ACCESS_TOKEN_EXPIRE_SECONDS=
   # MEMBRANE_JWT_EXPIRE_SECONDS=
   # MEMBRANE_SESSION_LIFETIME_SECONDS=
   # MEMBRANE_SESSION_COOKIE_SECURE=
   # MEMBRANE_SESSION_TYPE=
   # MEMBRANE_TOKEN_BLACKLIST=
   # MEMBRANE_APP_ID_FIELD=
   # MEMBRANE_DATA_FIELD=
   # MEMBRANE_REDIRECT_URL_FIELD=
   # MEMBRANE_ENCODE_ALGORITHM=
   # MEMBRANE_ALLOWED_EMAIL_DOMAINS_PATTERN=
   # MEMBRANE_EMAIL_SUBJECT=
   # MEMBRANE_EMAIL_SEND_SUCCESS=
   # MEMBRANE_EMAIL_SEND_POLLER_WAIT_TIME=
   # MEMBRANE_EMAIL_SEND_TIMEOUT_SECONDS=
   # MEMBRANE_EMAIL_SEND_HTML_TEMPLATE=
   # MEMBRANE_GENERIC_500_ERROR_FIELD=
   # MEMBRANE_GENERIC_500_ERROR=
   # MEMBRANE_LOGGING_LEVEL=
   # MEMBRANE_LOGGING_FORMAT=
   # MEMBRANE_HEALTH_MESSAGE=
   # MEMBRANE_WORKERS=
   # MEMBRANE_KEEP_ALIVE=
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
=======
See [Package](./PACKAGE.md)
>>>>>>> c2d29b5 (issue #35: update README)
