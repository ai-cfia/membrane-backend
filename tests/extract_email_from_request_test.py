"""
Unit tests for the `extract_email_from_request` function.
"""
import io
from werkzeug.wrappers import Request
from request_helpers import extract_email_from_request, EmailError

def create_request_with_json(data):
    """Create a mock request object with the given JSON data."""
    environ = {
        'REQUEST_METHOD': 'POST',
        'wsgi.input': io.BytesIO(data),
        'CONTENT_TYPE': 'application/json',
        'CONTENT_LENGTH': str(len(data)),
    }
    request = Request(environ)

    # Update get_data to accept cache argument and return our data
    request.get_data = lambda cache=True: data
    return request

def test_extract_valid_email():
    """Test extracting a valid email."""
    data = b'{"email": "test@inspection.gc.ca"}'
    mock_request = create_request_with_json(data)
    email = extract_email_from_request(mock_request)
    assert email == "test@inspection.gc.ca"

def test_extract_no_email():
    """Test extracting when no email is provided."""
    data = b'{}'
    mock_request = create_request_with_json(data)
    try:
        extract_email_from_request(mock_request)
        assert False, "Expected EmailError but got none."
    except EmailError as error:
        assert str(error) == "Missing email."

def test_extract_with_other_keys():
    """Test extracting email with other JSON keys."""
    data = b'{"name": "John", "email": "test@inspection.gc.ca", "age": 30}'
    mock_request = create_request_with_json(data)
    email = extract_email_from_request(mock_request)
    assert email == "test@inspection.gc.ca"
