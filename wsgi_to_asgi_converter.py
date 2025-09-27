#!/usr/bin/env python3
"""
Convert Flask WSGI app to ASGI for WebSocket support
"""

from asgiref.wsgi import WsgiToAsgi
from app import app

# Convert Flask WSGI app to ASGI
asgi_app = WsgiToAsgi(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(asgi_app, host="0.0.0.0", port=8000)
