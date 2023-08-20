"""
Email Test Cases
"""
import os
from request_helpers import is_valid_email, EmailError

# pylint: disable=unused-argument
def setup_module(module):
    """
    Setup for the test module.
    Setting the ALLOWED_EMAIL_DOMAINS environment variable for testing.
    """
    os.environ['ALLOWED_EMAIL_DOMAINS'] = 'gc.ca,canada.ca,inspection.gc.ca'

def test_valid_email_from_allowed_domain():
    """
    Test the is_valid_email function with a valid email from the allowed domain.
    """
    email = "test.user@inspection.gc.ca"
    try:
        assert is_valid_email(email) is True
    except EmailError:
        assert False, f"Expected {email} to be valid but was not."

def test_invalid_email_from_disallowed_domain():
    """
    Test the is_valid_email function with a valid email format but from a disallowed domain.
    """
    email = "test.user@notallowed.com"
    try:
        is_valid_email(email)
        assert False, f"Expected {email} to be invalid but was not."
    except EmailError:
        assert True


def test_concatenated_emails():
    """
    Test the is_valid_email function with two valid emails concatenated.
    This should not be considered a valid email.
    """
    email = "test.user1@inspection.gc.ca" + "test.user2@inspection.gc.ca"
    try:
        is_valid_email(email)
        assert False, f"Expected {email} to be invalid but was not."
    except EmailError:
        assert True

def test_email_with_unsupported_symbols():
    """
    Test the is_valid_email function with an email containing unsupported symbols.
    Such an email should not be considered valid.
    """
    email = "test.user!#%^&*()+=[]{}|;<>?@inspection.gc.ca"
    try:
        is_valid_email(email)
        assert False, f"Expected {email} to be invalid but was not."
    except EmailError:
        assert True
def test_email_with_lookalike_utf8_characters():
    """
    Test the is_valid_email function with an email containing look-alike UTF-8 characters.
    Such an email should not be considered valid as it's potentially misleading.
    """
    # Using Cyrillic 'а' which looks like Latin 'a'
    email = "test.userа@inspection.gc.ca"
    try:
        is_valid_email(email)
        assert False, f"Expected {email} to be invalid but was not."
    except EmailError:
        assert True
def test_misspelled_inspection_subdomain():
    """
    Test the is_valid_email function with a misspelled "inspection" subdomain.
    """
    email = "user@inspektion.gc.ca"
    try:
        is_valid_email(email)
        assert False, f"Expected {email} to be invalid but was not."
    except EmailError:
        assert True
def test_extra_characters_in_canada_domain():
    """
    Test the is_valid_email function with an extra character in the "canada" domain.
    """
    email = "user@canadaa.ca"
    try:
        is_valid_email(email)
        assert False, f"Expected {email} to be invalid but was not."
    except EmailError:
        assert True
def test_missing_domain_extension():
    """
    Test the is_valid_email function with a missing domain extension.
    """
    email = "user@canada."
    try:
        is_valid_email(email)
        assert False, f"Expected {email} to be invalid but was not."
    except EmailError:
        assert True
def test_missing_subdomain():
    """
    Test the is_valid_email function with a missing subdomain.
    """
    email = "user@.gc.ca"
    try:
        is_valid_email(email)
        assert False, f"Expected {email} to be invalid but was not."
    except EmailError:
        assert True
def test_extra_characters_in_tld():
    """
    Test the is_valid_email function with extra characters in the TLD.
    """
    email = "user@inspection.gc.caa"
    try:
        is_valid_email(email)
        assert False, f"Expected {email} to be invalid but was not."
    except EmailError:
        assert True
