import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the create_app factory from your main app module (app.py)
from app import create_app

# Create the application instance
application = create_app()