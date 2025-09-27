#!/usr/bin/env python3
"""
Start Sambanova with ASGI support for WebSocket
"""

import uvicorn
import asyncio
import subprocess
import sys
import os
from pathlib import Path

def start_asgi_server():
    """Start the ASGI server with WebSocket support."""
    print("🚀 Starting Sambanova ASGI Server with WebSocket support...")
    
    # Convert Flask app to ASGI
    from asgiref.wsgi import WsgiToAsgi
    from app import app
    
    asgi_app = WsgiToAsgi(app)
    
    # Start uvicorn server
    uvicorn.run(
        asgi_app,
        host="0.0.0.0",
        port=8000,
        ws="websockets",
        log_level="info"
    )

def create_production_script():
    """Create production deployment script."""
    script_content = '''#!/bin/bash
# Production deployment script for hjlees.com with WebSocket support

# Install required packages
pip install uvicorn[standard] asgiref websockets

# Start ASGI server
uvicorn wsgi_to_asgi_converter:asgi_app \\
    --host 0.0.0.0 \\
    --port 8000 \\
    --ws websockets \\
    --workers 4 \\
    --log-level info
'''
    
    with open("deploy_sambanova_asgi.sh", "w") as f:
        f.write(script_content)
    
    os.chmod("deploy_sambanova_asgi.sh", 0o755)
    print("✅ Created deploy_sambanova_asgi.sh")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "create-script":
        create_production_script()
    else:
        start_asgi_server()
