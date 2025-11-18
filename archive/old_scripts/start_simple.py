#!/usr/bin/env python3
"""
Simple startup script for WebSocket support without monkey patching conflicts
"""

# Import Flask app without any monkey patching
from app import create_app
from flask_socketio import SocketIO

# Create the app
app = create_app()

# Initialize SocketIO for WebSocket support
socketio = SocketIO(app, cors_allowed_origins="*")

# Register SocketIO events from Convonet routes
try:
    from convonet.routes import register_socketio_events
    register_socketio_events(socketio)
    print("✅ Convonet SocketIO events registered successfully")
except Exception as e:
    print(f"⚠️  Warning: Could not register Convonet SocketIO events: {e}")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8000, debug=True)
