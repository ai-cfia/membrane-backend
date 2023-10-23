#!/bin/bash

set -e  # Exit on error
set -x  # Debug mode

# Create keys directory if it doesn't exist
mkdir -p keys

# Generate server keys
openssl genpkey -algorithm RSA -out keys/server-private-key.pem >> init.log 2>&1
openssl rsa -pubout -in keys/server-private-key.pem -out keys/server-public-key.pem >> init.log 2>&1

echo "Server keys generated in 'keys' folder."

# Copy .env.template to .env
cp .env.template .env >> init.log 2>&1

# Copy .env.tests.template to .env.tests
cp .env.tests.template .env.tests >> init.log 2>&1

echo "Environment files generated."
