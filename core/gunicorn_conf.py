from multiprocessing import cpu_count

# Socket Path

bind = 'unix:/tmp/gunicorn.sock'

# Worker Options

workers = cpu_count() + 1

worker_class = 'uvicorn.workers.UvicornWorker'

# Logging Options

loglevel = 'ERROR'

errorlog = '/home/ubuntu/Feedback_bot/error_log'
