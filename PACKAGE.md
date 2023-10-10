# Membrane Package

## Overview

Membrane is a Python-based authentication package that leverages JWT for secure, token-based authentication. It is specifically designed to integrate with Flask applications, providing a streamlined approach for authentication management.

## Installation

```bash
pip install --no-cache-dir git+https://github.com/ai-cfia/membrane-backend.git
```

**Note:** The package is still in development. Install from the development branch on `git+https://github.com/ai-cfia/membrane-backend.git@k-allagbe/issue35-packaging-membrane`

## Features

- Simple Flask blueprint integration
- JWT Token-based authentication
- Flexible and customizable
- Error handling for JWT decoding

## Usage

### Basic Setup

Import the `configure` function and call it to set up the package.

```python
from membrane import configure

# Configuration
configure(
    active=True
    app=flask_app_instance,
    certificate=path_to_certificate,
    token_expiration=3600,
    redirect_path='/',
)
```

### Adding Login and Logout Routes

If you wish to add login and logout routes to your Flask application, you can simply register the Membrane blueprint:

```python
from flask import Flask
from membrane.client.flask import blueprint as membrane_blueprint

app = Flask(__name__)
app.register_blueprint(membrane_blueprint)
```

### Login Required Decorator

You can use `membrane_login_required` decorator to protect your routes.

```python
from membrane.client.flask import membrane_login_required

@app.route('/protected')
@membrane_login_required
def protected_route():
    return 'This is a protected route.'
```