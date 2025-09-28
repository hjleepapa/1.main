#!/usr/bin/env python3
"""
WebSocket-enabled startup script with proper monkey patching
"""

# CRITICAL: Monkey patch must be the VERY FIRST thing
import eventlet
eventlet.monkey_patch()

# Now import everything else
from app import create_app
from flask_socketio import SocketIO

# Create the app with WebSocket support
app = create_app()

# Initialize SocketIO for WebSocket support
socketio = SocketIO(app, cors_allowed_origins="*")

# Register SocketIO events from Sambanova routes
try:
    from sambanova.routes import register_socketio_events
    register_socketio_events(socketio)
    print("✅ Sambanova SocketIO events registered successfully")
except Exception as e:
    print(f"⚠️  Warning: Could not register Sambanova SocketIO events: {e}")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8000, debug=True)
