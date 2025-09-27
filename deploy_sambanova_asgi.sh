#!/bin/bash
# Production deployment script for hjlees.com with WebSocket support

# Install required packages
pip install uvicorn[standard] asgiref websockets

# Start ASGI server
uvicorn wsgi_to_asgi_converter:asgi_app \
    --host 0.0.0.0 \
    --port 8000 \
    --ws websockets \
    --workers 4 \
    --log-level info
