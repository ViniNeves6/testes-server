import multiprocessing

# Bind to port 8000 on all available network interfaces
bind = "0.0.0.0:8000"

# Use the number of CPU cores available in the system
workers = 2

# Log level
loglevel = "info"

# Access log - records incoming HTTP requests
accesslog = "/var/log/gunicorn/access.log"

# Error log - records Gunicorn server errors
errorlog = "/var/log/gunicorn/error.log"


# Timeout
timeout = 60

# Keep alive
keepalive = 5
