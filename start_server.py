#!/usr/bin/env python3
"""
Start the Universal Time Tracker Server with Database Browser
"""

import os
import sys

# Add the server directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'server', 'src'))

# Set the database path
os.environ['DATABASE_PATH'] = os.path.join(os.path.dirname(__file__), 'data', 'timetracker.db')

# Import and run the Flask app
from app import app

if __name__ == '__main__':
    print("Starting Universal Time Tracker Server...")
    print("Database Browser available at: http://localhost:5000/db")
    print("API available at: http://localhost:5000/api/v1/")
    print("Press Ctrl+C to stop the server")
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True) 