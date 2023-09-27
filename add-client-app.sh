#!/bin/bash

set -e  # Exit on error
set -x  # Debug mode

# Get APPID from command line argument. Exit if not provided.
if [ -z "$1" ]; then
  echo "usage: $0 APP_ID"
  echo "APP_ID is the application identifier from the client application"
  exit 1
fi

APPID=$1

# Create keys directory if it doesn't exist
mkdir -p keys

# Generate client keys with APPID
openssl genpkey -algorithm RSA -out "keys/${APPID}_private_key.pem" >> add-client.log 2>&1
openssl rsa -pubout -in "keys/${APPID}_private_key.pem" -out "keys/${APPID}_public_key.pem" >> add-client.log 2>&1

echo "Client keys for ${APPID} generated in 'keys' folder."
