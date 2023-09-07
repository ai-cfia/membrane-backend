# Configuration

1. Navigate to the root directory of the project and create a new file named .env.
2. Open this .env file using your preferred text editor.
3. Define the ALLOWED_EMAIL_DOMAINS= variable by setting it to your accepted email domains. These should be comma-separated.

Here's an example configuration: 

   For example: `ALLOWED_EMAIL_DOMAINS=gc.ca,canada.ca,inspection.gc.ca`

## Installing Dependencies

If you have previously saved your dependencies in a `requirements.txt` file and wish to install them again at a later time, you can do so with the following command:

```bash
pip install -r requirements.txt
