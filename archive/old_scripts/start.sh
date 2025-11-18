#!/bin/bash
# WebSocket-enabled start script for Render.com
gunicorn --worker-class gthread -w 1 --threads 4 --bind 0.0.0.0:$PORT start_simple:app
