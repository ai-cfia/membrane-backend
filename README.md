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

### REDIRECT_URL_TO_MEMBRANE_FRONTEND

- **Description:** The URL to which the Membrane backend will redirect users, leading them to the Membrane Frontend where they can provide an email address.
- **Example:** `REDIRECT_URL_TO_MEMBRANE_FRONTEND=https://membranefrontend.com/`

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

### 9. Interact with Membrane Frontend:

Ensure that the Membrane Frontend React application is running, ideally on `localhost`. This application will serve as the frontend interface for users to provide their email addresses to Membrane Backend.

---

You can now interact with both the main Flask application and the client simulator to validate the entire authentication flow.

## Running the app from dockerfile

### Generate Server and Client Keys

#### Prerequisites

- OpenSSL installed on your machine (in WSL).

#### Steps

1. Navigate to the project's root directory.
2. Run the following script:

   ```bash
   ./generate_keys.sh
   ```

   This will generate four `.pem` files in a folder called `keys`:

   - `server_private_key.pem`
   - `server_public_key.pem`
   - `client_private_key.pem`
   - `client_public_key.pem`

#### Note

- If the keys already exist, the script will overwrite them.

### Configure environment variables

1. Create a .env file in the project's root directory.
2. Generate a secret key:

```bash
openssl rand -hex 32
```

3. Add the following variables:

```
ALLOWED_EMAIL_DOMAINS=
SECRET_KEY=
JWT_ACCESS_TOKEN_EXPIRES_MINUTES=
SESSION_TYPE=
CLIENT_PUBLIC_KEYS_DIRECTORY=
SERVER_PRIVATE_KEY=
SERVER_PUBLIC_KEY=
SESSION_LIFETIME_MINUTES=
REDIRECT_URL_TO_MEMBRANE_FRONTEND=
```

4. Replace `<your_secret_key_here>` with the generated key from step 2.

### Running the App

1. Build the Docker image:

   ```bash
   docker build -t flask-app .
   ```

2. Set your desired port number:

   ```bash
   export PORT=<your_port_here>
   ```

3. Run the Docker container:

   ```bash
   docker run -p $PORT:$PORT -e PORT=$PORT --env-file .env flask-app
   ```

#### Note

- Replace `<your_port_here>` with the port number you wish to use for the application.
