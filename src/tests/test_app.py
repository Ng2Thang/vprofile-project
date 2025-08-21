import pytest
import json
from app import app

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
    assert "The Hitchhiker's Guide to the Galaxy" in [d['title'] for d in data]

def test_show_books_page(client):
    """Test that the /books page loads and displays book data."""
    response = client.get('/books')
    assert response.status_code == 200
    assert b"Available Books" in response.data
    assert b"Dune" in response.data # Check for a specific book title

