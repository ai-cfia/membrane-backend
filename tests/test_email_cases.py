# test_email_cases.py

import os
from utils import is_valid_email

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
    assert is_valid_email(email) is True, f"Expected {email} to be valid but was not."

def test_invalid_email_from_disallowed_domain():
    """
    Test the is_valid_email function with a valid email format but from a disallowed domain.
    """
    email = "test.user@notallowed.com"
    assert is_valid_email(email) is False, f"Expected {email} to be invalid but was not."

def test_concatenated_emails():
    """
    Test the is_valid_email function with two valid emails concatenated.
    This should not be considered a valid email.
    """
    email = "test.user1@inspection.gc.ca" + "test.user2@inspection.gc.ca"
    assert is_valid_email(email) is False, f"Expected {email} to be invalid, but it was considered valid."

def test_email_with_unsupported_symbols():
    """
    Test the is_valid_email function with an email containing unsupported symbols.
    Such an email should not be considered valid.
    """
    email = "test.user!#%^&*()+=[]{}|;<>?@inspection.gc.ca"
    assert is_valid_email(email) is False, f"Expected {email} to be invalid due to unsupported symbols, but it was considered valid."

def test_email_with_lookalike_utf8_characters():
    """
    Test the is_valid_email function with an email containing look-alike UTF-8 characters.
    Such an email should not be considered valid as it's potentially misleading.
    """
    # Using Cyrillic 'а' which looks like Latin 'a'
    email = "test.userа@inspection.gc.ca"
    assert is_valid_email(email) is False, f"Expected {email} to be invalid due to look-alike UTF-8 characters, but it was considered valid."

def test_misspelled_inspection_subdomain():
    """
    Test the is_valid_email function with a misspelled "inspection" subdomain.
    """
    email = "user@inspektion.gc.ca"
    assert is_valid_email(email) is False, f"Expected {email} to be invalid but was not."

def test_extra_characters_in_canada_domain():
    """
    Test the is_valid_email function with an extra character in the "canada" domain.
    """
    email = "user@canadaa.ca"
    assert is_valid_email(email) is False, f"Expected {email} to be invalid but was not."

def test_missing_domain_extension():
    """
    Test the is_valid_email function with a missing domain extension.
    """
    email = "user@canada."
    assert is_valid_email(email) is False, f"Expected {email} to be invalid but was not."

def test_missing_subdomain():
    """
    Test the is_valid_email function with a missing subdomain.
    """
    email = "user@.gc.ca"
    assert is_valid_email(email) is False, f"Expected {email} to be invalid but was not."

def test_extra_characters_in_tld():
    """
    Test the is_valid_email function with extra characters in the TLD.
    """
    email = "user@inspection.gc.caa"
    assert is_valid_email(email) is False, f"Expected {email} to be invalid but was not."

