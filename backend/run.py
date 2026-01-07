#!/usr/bin/env python3
"""
KnowBook Backend Server
Entry point for the Flask application.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)