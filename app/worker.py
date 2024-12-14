import redis
from rq import Worker, Queue

listen = ['default']
redis_url = 'redis://localhost:6379'


conn = redis.Redis.from_url(redis_url)


def run_worker():

    queues = [Queue(name, connection=conn) for name in listen]

    worker = Worker(queues, connection=conn)
    worker.work()


if __name__ == '__main__':
    run_worker()
