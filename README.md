## Work Flow

Louis Login Backend offers a comprehensive workflow that ensures a seamless Single Sign-On (SSO) experience. The system operates through a series of steps starting from the client application check to email verification and eventual redirection after verification. 

For a detailed step-by-step breakdown and to understand how the API endpoints function within this process, please refer to the [WORKFLOW documentation](./WORKFLOW.md).

---

## Setting Up a Flask Application

Follow the instructions below to set up a Flask application in your environment:

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

Now, you can proceed with running your Flask application or any other tasks. Always ensure that your virtual environment is activated when working on the project to maintain dependencies separately from your global Python environment.


## 6. Environment Variable Configuration:

To run the Flask application correctly, it requires some environment variables to be set. Follow the steps below to set them up:

1. Navigate to the root directory of the project and create a new file named `.env`.
2. Open this `.env` file using your preferred text editor.

Now, define each of the following variables:

### ALLOWED_EMAIL_DOMAINS
- **Description:** List of email domains that are accepted by the application.
- **Format:** Comma-separated list of domains.
- **Example:** `ALLOWED_EMAIL_DOMAINS=gc.ca,canada.ca,inspection.gc.ca`

### SECRET_KEY
- **Description:** The secret key used for creating encrypted tokens and for the Flask session.
- **Recommendation:** Generate a strong random value for this.

### JWT_ACCESS_TOKEN_EXPIRES_MINUTES
- **Description:** The expiration time (in minutes) for the JWT access token.
- **Example:** `JWT_ACCESS_TOKEN_EXPIRES_MINUTES=30`

### SESSION_TYPE
- **Description:** Specifies where to store the session data. Options can include 'filesystem', 'redis', 'memcached', etc. 
- **Example:** `SESSION_TYPE=filesystem`

### CLIENT_PUBLIC_KEYS_DIRECTORY
- **Description:** Path to the directory where client public keys are stored. These keys are used for JWT validation.
- **Example:** `CLIENT_PUBLIC_KEYS_DIRECTORY=keys/public_keys`

### SERVER_PRIVATE_KEY
- **Description:** Path to the server's private key file. This key is used for creating and signing tokens.
- **Example:** `SERVER_PRIVATE_KEY=keys/server_private.pem`

### SERVER_PUBLIC_KEY
- **Description:** Path to the server's public key file. This key is used for verifying tokens.
- **Example:** `SERVER_PUBLIC_KEY=keys/server_public.pem`

### SESSION_LIFETIME_MINUTES
- **Description:** Duration (in minutes) after which the session will expire.
- **Example:** `SESSION_LIFETIME_MINUTES=30`

### REDIRECT_URL_TO_LOUIS_FRONTEND
- **Description:** The URL to which the Louis login backend will redirect users, leading them to the Louis login frontend where they can provide an email address.
- **Example:** `REDIRECT_URL_TO_LOUIS_FRONTEND=https://login.louisfrontend.com/`

Once you have defined all these variables, save and close the `.env` file. The Flask application will now use these environment variable values when it runs.

### 7. Run the Main Flask Application:
With your virtual environment activated, start the main `app.py`:
```bash
flask run
```

### 8. Simulate a Client Application:
Open a separate terminal or command prompt. Make sure the virtual environment is activated and then run the `test1app.py` to simulate a client application:
```bash
flask --app .\test1app.py run --port=4000
```

### 9. Interact with Louis Login Frontend:
Ensure that the Louis Login Frontend React application is running, ideally on `localhost`. This application will serve as the frontend interface for users to provide their email addresses to Louis Login Backend.

---

You can now interact with both the main Flask application and the client simulator to validate the entire authentication flow.
