import pytest
import json
import sys
import os

# Add the 'src' directory to sys.path to allow importing 'app'.
# This is necessary because the test is run from the project root.
SRC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, SRC_PATH)

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
