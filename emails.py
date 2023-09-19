from azure.communication.email import EmailClient


def send_email(
    connection_string,
    sender_email,
    recipient_email,
    subject,
    body,
    html_content=None,
):
    """
    Send an email using Azure Communication Services.

    Parameters:
    - connection_string (str): The connection string for Azure Communication Services.
    - sender_email (str): The sender's email address.
    - recipient_email (str): The recipient's email address.
    - subject (str): The subject of the email.
    - body (str): The plain text body content of the email.
    - html_content (str): The HTML content of the email. Optional.

    Raises:
    - RuntimeError: If the email sending process fails or times out.

    Source: https://learn.microsoft.com/en-ca/azure/communication-services/quickstarts/email/send-email?tabs=windows%2Cconnection-string&pivots=programming-language-python
    """
    # Initialize the EmailClient
    email_client = EmailClient.from_connection_string(connection_string)

    # Construct the message
    message = {
        "content": {
            "subject": subject,
            "plainText": body,
            "html": html_content if html_content else f"<html><h1>{body}</h1></html>",
        },
        "recipients": {
            "to": [{"address": recipient_email, "displayName": "Customer Name"}]
        },
        "senderAddress": sender_email,
    }

    # Send the email and poll for its status
    POLLER_WAIT_TIME = 10
    time_elapsed = 0

    try:
        poller = email_client.begin_send(message)

        while not poller.done():
            print("Email send poller status: " + poller.status())

            poller.wait(POLLER_WAIT_TIME)
            time_elapsed += POLLER_WAIT_TIME

            if time_elapsed > 18 * POLLER_WAIT_TIME:
                raise RuntimeError("Polling timed out.")

        if poller.result()["status"] == "Succeeded":
            print(
                f"Successfully sent the email (operation id: {poller.result()['id']})"
            )
        else:
            raise RuntimeError(str(poller.result()["error"]))
    except Exception as ex:
        print(ex)
