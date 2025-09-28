# WebSocket-enabled configuration with eventlet worker
web: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT wsgi_to_asgi_converter:asgi_app
