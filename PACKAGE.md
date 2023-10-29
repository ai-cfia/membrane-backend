# Membrane Package

## Overview

Membrane is a Python-based authentication package that leverages JWT for secure, token-based authentication. It is specifically designed to integrate with Flask applications, providing a streamlined approach for authentication management.

## Installation

```bash
pip install --no-cache-dir git+https://github.com/ai-cfia/membrane-backend.git
```

**Note:** The package is still in development. Install from the development branch on `git+https://github.com/ai-cfia/membrane-backend.git@k-allagbe/issue35-packaging-membrane`

## Features

- Simple Flask blueprint integration for login and logout routes
- JWT Token-based authentication

## Usage

### Basic Setup

Import the `configure_membrane` function and call it to set up the package.

```python
from membrane.client.flask import configure_membrane

# Configuration
configure_membrane(
    app=flask_app_instance,
    certificate=certificate_dict,
    token_expiration=3600,
    custom_claims=None,
    landing_page_path='/',
    logout_page_path='/'
)
```

### Login Required Decorator

Use the `membrane_login_required` decorator to protect your routes.

```python
from membrane.client.flask import membrane_login_required

@app.route('/protected')
@membrane_login_required
def protected_route():
    return 'This is a protected route.'
```

### Adding Login and Logout Routes

If you wish to add login and logout routes to your Flask application, you can simply register the Membrane blueprint:

```python
from flask import Flask
from membrane.client.flask import blueprint as membrane_blueprint

app = Flask(__name__)
app.register_blueprint(membrane_blueprint)
```
