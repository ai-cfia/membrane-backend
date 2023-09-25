# Deployment Guide for membrane-backend

This guide outlines the steps to deploy membrane-backend to Google Cloud Run.

## Steps
 1. Run the script from DevOps repo available [here](https://github.com/ai-cfia/devops)

2.  You will need to add the "Secret Manager Secret Accessor" role to your service account

3. Enable google Secret Manager 

4. Create a new secret and for each key, give it a name and upload it. Keep this tab open as you will need it for an upcoming step.

> Note : it is recommanded you use these names
> - client_private_key	
> - client1_public_key	
> - server_private_key
> - server_public_key

5. On Cloud Run, click on the name of the application you want to mount your secrets as volume on to and click on "Edit & Deploy New Revision" on the top of the screen.

6. Scroll down all the way down to "Secrets" and add the link to each key. To find the link to your keys, go back to your key manager and click on any key. On top of the "Overview", you should see the link to your key. Copy paste the path to each key to Cloud Run.

7. You will need to do the same for the keys which are in your .env file.