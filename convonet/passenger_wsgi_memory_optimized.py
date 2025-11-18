#!/usr/bin/env python3
"""
Memory-optimized WSGI entry point for Flask-SocketIO with eventlet support
"""

# CRITICAL: Monkey patch MUST be the very first thing
import eventlet
eventlet.monkey_patch()

print("✅ Eventlet monkey patch applied!")

import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import the create_app factory and socketio from the memory-optimized app
from app_memory_optimized import create_app, socketio

print("✅ Imported create_app and socketio from memory-optimized app")

# Create the application instance
app = create_app()

print(f"✅ Flask app created: {app}")
print(f"✅ SocketIO instance: {socketio}")

# For Flask-SocketIO with eventlet, we need to expose the Flask app directly
application = app

print(f"✅ WSGI application exported: {application}")