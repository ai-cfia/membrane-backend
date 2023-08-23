"""
Unit tests for the `extract_jwt_token` function.
"""
from werkzeug.wrappers import Request
from jwt_utils import extract_jwt_token
from generate_jwt import generate_jwt

# Loading the private key
TEST_PRIVATE_KEY = open('tests/test_private_keys/test1_private_key.pem', 'rb').read()

def create_request_with_json(data):
    """Create a mock request object with the given JSON data."""
    environ = {
        'REQUEST_METHOD': 'POST',
        'wsgi.input': None,
        'CONTENT_TYPE': 'application/json',
        'CONTENT_LENGTH': len(data),
    }
    request = Request(environ)

    # Update get_data to accept cache argument and return our data
    request.get_data = lambda cache=True: data  

    # Simple mock for is_json property
    request.is_json = True
    return request

def generate_valid_jwt():
    """Generate a valid JWT token with the required app_id"""
    jwt_data = {
        "app_id": "app1",
        "redirect_url": "https://www.google.com/"
    }
    return generate_jwt(jwt_data, TEST_PRIVATE_KEY)

def create_request(query_string):
    """Create a mock request object with the given query_string."""
    environ = {
        'QUERY_STRING': query_string,
        'REQUEST_METHOD': 'GET',
        'wsgi.input': None,
    }
    return Request(environ)

def test_extract_jwt_with_valid_token():
    """Test extracting a valid JWT token."""
    valid_jwt = generate_valid_jwt()
    mock_request = create_request(f"token={valid_jwt}")
    token = extract_jwt_token(mock_request)
    assert token == valid_jwt

def test_extract_jwt_with_empty_token():
    """Test extracting an empty JWT token."""
    mock_request = create_request("token=")
    token = extract_jwt_token(mock_request)
    assert token == ""

def test_extract_jwt_without_token():
    """Test scenario where no JWT token is provided."""
    mock_request = create_request("")
    token = extract_jwt_token(mock_request)
    assert token is None

def test_extract_jwt_with_other_parameters():
    """Test extracting JWT token with other query parameters."""
    mock_request = create_request(f"other_param=value&token={generate_valid_jwt()}")
    token = extract_jwt_token(mock_request)
    assert token == generate_valid_jwt()
