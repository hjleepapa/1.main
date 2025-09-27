#!/usr/bin/env python3
"""
Flask-SocketIO setup for WebSocket support
"""

from flask import Flask
from flask_socketio import SocketIO, emit
import os

# Create Flask app with SocketIO support
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY', 'your-secret-key')

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection."""
    print('Client connected')
    emit('status', {'data': 'Connected to Sambanova WebSocket'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection."""
    print('Client disconnected')

@socketio.on('twilio_media')
def handle_twilio_media(data):
    """Handle Twilio media stream data."""
    print(f'Received media data: {data}')
    # Process media data here
    emit('response', {'data': 'Media processed'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)
