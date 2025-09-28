#!/usr/bin/env python3
"""
Convert Flask WSGI app to ASGI for WebSocket support with eventlet monkey patching
"""

import eventlet
# CRITICAL: Monkey patch must be done before importing any other modules
eventlet.monkey_patch()

from asgiref.wsgi import WsgiToAsgi
from app import app

# Convert Flask WSGI app to ASGI
asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(asgi_app, host="0.0.0.0", port=8000)
