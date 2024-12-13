import redis
from rq import Worker, Queue
from redis import Connection

listen = ['default']
redis_url = 'ur path to redis'


conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()