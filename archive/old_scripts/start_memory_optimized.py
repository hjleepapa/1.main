#!/usr/bin/env python3
"""
Memory-optimized startup script for Render deployment
"""

import os
import sys
import subprocess

def start_memory_optimized():
    """Start the application with memory optimizations"""
    
    # Set memory optimization environment variables
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    
    # Get port from environment
    port = os.getenv('PORT', '10000')
    
    # Memory-optimized gunicorn command
    cmd = [
        'gunicorn',
        '--worker-class', 'eventlet',
        '-w', '1',  # Single worker to reduce memory
        '--worker-connections', '1000',  # Reduce connections
        '--max-requests', '1000',  # Restart worker after 1000 requests
        '--max-requests-jitter', '100',  # Add jitter to prevent thundering herd
        '--timeout', '30',  # Reduce timeout
        '--keep-alive', '2',  # Reduce keep-alive
        '--bind', f'0.0.0.0:{port}',
        '--log-level', 'info',
        '--access-logfile', '-',
        '--error-logfile', '-',
        'passenger_wsgi:application'
    ]
    
    print(f"🚀 Starting memory-optimized server on port {port}")
    print(f"📊 Memory optimizations:")
    print(f"   - Single worker process")
    print(f"   - Reduced worker connections")
    print(f"   - Request recycling enabled")
    print(f"   - Reduced timeouts")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    start_memory_optimized()
