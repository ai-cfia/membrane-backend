#!/bin/bash

set -e  # Exit on error
set -x  # Debug mode

# Get APPID from command line argument. Exit if not provided.
if [ -z "$1" ]; then
  echo "APPID must be provided."
  exit 1
fi

APPID=$1

# Create keys directory if it doesn't exist
mkdir -p keys >> init.log 2>&1

# Generate server keys
openssl genpkey -algorithm RSA -out keys/server_private_key.pem >> init.log 2>&1
openssl rsa -pubout -in keys/server_private_key.pem -out keys/server_public_key.pem >> init.log 2>&1

# Generate client keys with APPID
openssl genpkey -algorithm RSA -out "keys/${APPID}_private_key.pem" >> init.log 2>&1
openssl rsa -pubout -in "keys/${APPID}_private_key.pem" -out "keys/${APPID}_public_key.pem" >> init.log 2>&1

echo "Keys generated in 'keys' folder."

# Copy .env.template to .env
cp .env.template .env >> init.log 2>&1

# Copy .env.tests.template to .env.tests
cp .env.tests.template .env.tests >> init.log 2>&1

echo "Environment files generated."
