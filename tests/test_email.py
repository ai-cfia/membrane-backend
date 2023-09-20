from logging import getLogger

import pytest

from emails import send_email  # Replace with the actual import


@pytest.mark.asyncio
async def test_send_real_email(azure_conn_string, sender_email, receiver_email):
    logger = getLogger("testLogger")

    send_email(
        azure_conn_string,
        sender_email,
        receiver_email,
        "Subject",
        "Body",
        logger,
    )


@pytest.mark.asyncio
async def test_invalid_conn_string(sender_email):
    bad_conn_string = "InvalidConnectionString"
    logger = getLogger("testLogger")

    with pytest.raises(Exception):
        send_email(
            bad_conn_string,
            sender_email,
            "recipient@example.com",
            "Subject",
            "Body",
            logger,
        )


@pytest.mark.asyncio
async def test_non_existent_recipient(azure_conn_string, sender_email):
    logger = getLogger("testLogger")
    bad_recipient = "nonexistent@example.com"

    with pytest.raises(Exception):
        send_email(
            azure_conn_string, sender_email, bad_recipient, "Subject", "Body", logger
        )
