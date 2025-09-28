#!/usr/bin/env python3
"""
WebSocket-enabled startup script with proper monkey patching
"""

# CRITICAL: Monkey patch must be the VERY FIRST thing
import eventlet
eventlet.monkey_patch()

# Now import everything else
from app import create_app

# Create the app with WebSocket support
app = create_app()

if __name__ == "__main__":
    from flask_socketio import SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*")
    socketio.run(app, host="0.0.0.0", port=8000, debug=True)
