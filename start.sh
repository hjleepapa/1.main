#!/bin/bash
# WebSocket-enabled start script for Render.com
gunicorn --worker-class gevent -w 1 --bind 0.0.0.0:$PORT start_simple:app
