# Flask-SocketIO with eventlet worker (WebSocket support)
# NOTE: -w 1 is REQUIRED for Socket.IO (single worker only)
web: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT passenger_wsgi:application
