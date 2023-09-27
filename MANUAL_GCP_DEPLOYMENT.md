# Deployment Guide for membrane-backend

This guide outlines the steps to deploy manually membrane-backend to Google Cloud Run.

## Steps
 1. Setup your GCP environment. You can use the instructions [GCP Project Setup Guide](https://github.com/ai-cfia/devops/blob/main/gcp-setup-script/gcp-project-setup-guide.md)

2.  You will need to add the "Secret Manager Secret Accessor" role to your service account

3. Enable "Secret Manager" service on your GCP project.

4. After running the script from the ReadMe file, you should have 4 keys on your project. If you have the public key(s) from your client(s), you can go ahead and delete the one you generated and replace it with the one(s) you have. In the "Secret Manager", create a new secret and for each key, give it the right name and upload it.

5. On Cloud Run, click on the name of the application you want to mount your secrets as volume on to and click on "Edit & Deploy New Revision" on the top of the screen.

6. Scroll down all the way down to "Secrets" and add the link to each key. To find the link to your keys, go back to your key manager and click on any key. On top of the "Overview", you should see the link to your key. Copy paste the path to each key to Cloud Run.

7. You will need to point out to the link for SERVER_PRIVATE_KEY and SERVER_PUBLIC_KEY in your .env file as well.