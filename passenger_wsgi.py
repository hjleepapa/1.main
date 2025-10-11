import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the create_app factory and socketio from your main app module (app.py)
from app import create_app, socketio

# Create the application instance
app = create_app()

# For WSGI servers, we expose the socketio.wsgi_app instead of app
# This allows Socket.IO to handle WebSocket upgrades properly
application = socketio.wsgi_app if socketio else app