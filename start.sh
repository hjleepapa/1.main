#!/bin/bash
# WebSocket-enabled start script for Render.com
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app
