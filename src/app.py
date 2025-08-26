import os
import json
from flask import Flask, render_template, jsonify

app = Flask(__name__)


def load_books_from_json():
    """Helper function to load book data from the JSON file."""
    # Construct the path to the JSON file relative to the app's root path
    json_url = os.path.join(app.root_path, 'data', 'books.json')
    with open(json_url) as f:
        return json.load(f)


@app.route('/')
def home():
    """Renders the home page."""
    return render_template('index.html', message="Hello from Flask!")


@app.route('/books')
def show_books():
    """Renders a page displaying a list of books."""
    books = load_books_from_json()
    return render_template('books.html', books=books)


@app.route('/api/books', methods=['GET'])
def get_books():
    """API endpoint to get all books."""
    books = load_books_from_json()
    return jsonify(books)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
