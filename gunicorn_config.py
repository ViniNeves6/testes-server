import multiprocessing

# Bind to port 8000 on all available network interfaces
bind = "0.0.0.0:8000"

# Use the number of CPU cores available in the system
workers = 2

# Log level
loglevel = "info"

# Access log - records incoming HTTP requests
accesslog = "-"

# Error log - records Gunicorn server errors
errorlog = "-"


# Timeout
timeout = 60

# Keep alive
keepalive = 5
