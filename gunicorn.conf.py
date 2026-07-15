import os

bind = "0.0.0.0:5000"
workers = 1
worker_class = "eventlet"
worker_connections = 1000
timeout = 30
keepalive = 2
accesslog = "-"
errorlog = "-"
loglevel = "info"
reload = os.getenv('FLASK_ENV') == 'development'
