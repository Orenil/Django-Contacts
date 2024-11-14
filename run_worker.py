import sys
import logging
from redis import Redis
from rq import Worker, Queue, Connection
from rq.scheduler import RQScheduler
import django_rq

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the connection to Redis
redis_conn = Redis()

def start_worker():
    # Create a Queue for the worker
    queue = Queue('default', connection=redis_conn)

    # Ensure the worker runs without forking on Windows
    worker = Worker([queue], connection=redis_conn)
    
    logger.info("Worker started without forking.")
    worker.work(with_scheduler=True)

def start_scheduler():
    # Initialize the scheduler with 'queues' argument
    scheduler = RQScheduler(queues=['default'], connection=redis_conn)  # Pass the 'queues' argument as a list
    scheduler.acquire_locks()  # Acquire locks to start the scheduler

def main():
    if sys.platform == 'win32':
        logger.info("Running on Windows.")
        start_worker()
    else:
        logger.info("Running on non-Windows OS.")
        start_worker()

if __name__ == '__main__':
    main()
