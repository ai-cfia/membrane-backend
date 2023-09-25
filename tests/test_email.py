from logging import getLogger

import pytest

from emails import InvalidConnectionStringError, UnexpectedEmailSendError, send_email


@pytest.mark.asyncio
async def test_send_real_email(
    azure_conn_string, sender_email, receiver_email, email_subject, email_body
):
    logger = getLogger("testLogger")

    send_email(
        azure_conn_string,
        sender_email,
        receiver_email,
        email_subject,
        email_body,
        logger,
    )


@pytest.mark.asyncio
async def test_invalid_conn_string(
    sender_email, receiver_email, email_subject, email_body
):
    bad_conn_string = "InvalidConnectionString"
    logger = getLogger("testLogger")

    with pytest.raises(InvalidConnectionStringError):
        send_email(
            bad_conn_string,
            sender_email,
            receiver_email,
            email_subject,
            email_body,
            logger,
        )


@pytest.mark.asyncio
async def test_non_existent_recipient(azure_conn_string, sender_email):
    logger = getLogger("testLogger")
    bad_recipient = "nonexistent@example.com"

    with pytest.raises(UnexpectedEmailSendError):
        send_email(
            azure_conn_string, sender_email, bad_recipient, "Subject", "Body", logger
        )
