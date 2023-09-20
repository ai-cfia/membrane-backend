#!/bin/bash

set -e  # Exit on error
set -x  # Debug mode

# Get prefix from command line argument, default to empty string if not provided
PREFIX=$1

# Create keys directory if it doesn't exist
mkdir -p keys >> keygen.log 2>&1

# Generate server keys
openssl genpkey -algorithm RSA -out keys/server_private_key.pem >> keygen.log 2>&1
openssl rsa -pubout -in keys/server_private_key.pem -out keys/server_public_key.pem >> keygen.log 2>&1

# Generate client keys with prefix
openssl genpkey -algorithm RSA -out "keys/${PREFIX}_private_key.pem" >> keygen.log 2>&1
openssl rsa -pubout -in "keys/${PREFIX}_private_key.pem" -out "keys/${PREFIX}_public_key.pem" >> keygen.log 2>&1

echo "Keys generated in 'keys' folder."