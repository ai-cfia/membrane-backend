# Deployment Guide for membrane-backend

This guide outlines the steps to deploy manually membrane-backend to Google Cloud Run (GCP). It uses secrets as volume which allows you to mount your secret keys directly into the service's filesystem, which gives a secure and effective way to manage the application's sensitive information.

This backend application needs to manage keys for communcation with different clients here is a breakdown
- Server Key Pair:

    * Private Key: Used by the server to decrypt information encrypted with its public key. Must be stored securely and never exposed.

    * Public Key: Shared with clients or other entities that need to encrypt data intended only for the server.
Client Key Pairs:

- Private Key: Remains with the client. Used to decrypt data or sign transactions.
- Public Key: Shared with the server and possibly other clients. The server uses this to encrypt data specifically for that client or verify its signature.

## Steps
 1. Setup your GCP environment. You can use the instructions [GCP Project Setup Guide](https://github.com/ai-cfia/devops/blob/main/gcp-setup-script/gcp-project-setup-guide.md)

2.  You will need to add the "Secret Manager Secret Accessor" role to your service account

3. Enable ["Secret Manager"](https://cloud.google.com/secret-manager) service on your GCP project.

4. After running the script from the [ReadMe](README.md) file, you should have 4 keys on your project. If you have the public key(s) from your client(s), you can go ahead and delete the one you generated and replace it with the one(s) you have. In the "Secret Manager", create a new secret and for each key, give it the right name and upload it.

5. On Cloud Run, click on the name of the application you want to mount your secrets as volume on to and click on "Edit & Deploy New Revision" on the top of the screen.

![GCP Deploy & Edit](docs/gcp-edit-&-deploy.pngg)

6. Scroll down all the way down to "Secrets" and add the link to each key. To find the link to your keys, go back to your key manager and click on any key. On top of the "Overview", you should see the link to your key. Copy paste the path to each key to Cloud Run.