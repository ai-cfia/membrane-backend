"""
Login API Test
"""
# pylint: disable=redefined-outer-name
import pytest
import requests

@pytest.fixture(scope='module')
def base_url():
    """Fixture to set base url"""
    return 'http://localhost:5000'

@pytest.fixture(scope='module')
def login_url(base_url):
    """Fixture to set login url"""
    return f'{base_url}/login'

def test_valid_login(request):
    """
    Test case for valid login credentials.
    Asserts that the status code of the response is 200
    """
    login_url = request.getfixturevalue('login_url')
    response = requests.post(
        login_url,
        json={
            "email": "valid.email@inspection.gc.ca",
            "redirect_url": "http://localhost:3000/"
        },
        timeout=5
    )
    assert response.status_code == 200

def test_invalid_email_format(request):
    """
    Test case for invalid email format.
    Asserts that the status code of the response is 400
    """
    login_url = request.getfixturevalue('login_url')
    response = requests.post(
        login_url,
        json={
            "email": "invalid.email",
            "redirect_url": "http://localhost:3000/"
        },
        timeout=5
    )
    assert response.status_code == 400

def test_email_not_provided(request):
    """
    Test case for not providing an email.
    Asserts that the status code of the response is 400
    """
    login_url = request.getfixturevalue('login_url')
    response = requests.post(
        login_url,
        json={
            "redirect_url": "http://localhost:3000/"
        },
        timeout=5
    )
    assert response.status_code == 400

def test_redirect_url_not_provided(request):
    """
    Test case for not providing a redirect url.
    Asserts that the status code of the response is 400
    """
    login_url = request.getfixturevalue('login_url')
    response = requests.post(
        login_url,
        json={
            "email": "valid.email@example.com",
        },
        timeout=5
    )
    assert response.status_code == 400

def test_empty_json(request):
    """
    Test case for empty json.
    Asserts that the status code of the response is 400
    """
    login_url = request.getfixturevalue('login_url')
    response = requests.post(
        login_url,
        json={},
        timeout=5
    )
    assert response.status_code == 400 
