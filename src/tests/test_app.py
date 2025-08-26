import pytest
import json
import sys
import os

# Add the parent directory ('src') to the Python path to resolve the module not found error.
# This allows the test to import the 'app' module from the 'src' directory.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app  # noqa: E402


@pytest.fixture
def client():
    """Create and configure a new app instance for each test."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home_page(client):
    """Test that the home page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Hello from Flask!" in response.data


def test_get_books_api(client):
    """Test the /api/books endpoint."""
    response = client.get('/api/books')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0
    titles = [d['title'] for d in data]
    assert "The Hitchhiker's Guide to the Galaxy" in titles


def test_show_books_page(client):
    """Test that the /books page loads and displays book data."""
    response = client.get('/books')
    assert response.status_code == 200
    assert b"Available Books" in response.data
    assert b"Dune" in response.data  # Check for a specific book title
