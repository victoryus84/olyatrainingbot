import multiprocessing

# Gunicorn configuration

# The number of worker processes for handling requests
workers = multiprocessing.cpu_count() * 2 + 1

# The type of worker processes to use
worker_class = 'gthread'

# The host and port where Gunicorn will listen for requests
bind = '0.0.0.0:8000'

# The maximum number of pending connections
backlog = 2048

# The maximum number of requests a worker will process before restarting
max_requests = 1000

# The maximum number of simultaneous clients that can be served by each worker process
worker_connections = 1000

# The timeout for gracefully shutting down worker processes
timeout = 30

# Enable or disable Gunicorn's internal error logging
capture_output = True

# Set the log level (debug, info, warning, error, critical)
loglevel = 'info'
