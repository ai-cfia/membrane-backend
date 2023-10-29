Membrane-Backend is a Single Sign-On (SSO) solution specifically designed for AI-Lab products. This repository contains two key components:

1. **SSO Server**: A centralized authentication and authorization service built with Flask, designed to provide a single point of entry for multiple services within the AI-Lab ecosystem.

2. **Client Packages**: These are the required packages that need to be installed on client backends to enable Membrane functionality. These packages facilitate secure and seamless interaction with the SSO server.

---

## Server

### Getting Started

#### Cloning the repository

```bash
git clone https://github.com/ai-cfia/membrane-backend.git
```

#### Configuration

1. Navigate: `cd membrane-backend`
2. Run `./init-server.sh` to create necessary server resources.
3. Run `./add-client-app.sh <your-client-app-name>` to create a client key pair.
4. Edit the `.env` file.

#### Running the server

1. **Using VS Code DevContainer**

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

See [Package](./PACKAGE.md)