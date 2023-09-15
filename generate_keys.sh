#!/bin/bash

# Create keys directory if it doesn't exist
mkdir -p keys > /dev/null 2>&1

# Generate server keys
openssl genpkey -algorithm RSA -out keys/server_private_key.pem > /dev/null 2>&1
openssl rsa -pubout -in keys/server_private_key.pem -out keys/server_public_key.pem > /dev/null 2>&1

# Generate client keys
openssl genpkey -algorithm RSA -out keys/client_private_key.pem > /dev/null 2>&1
openssl rsa -pubout -in keys/client_private_key.pem -out keys/client_public_key.pem > /dev/null 2>&1

echo "Keys generated in 'keys' folder."