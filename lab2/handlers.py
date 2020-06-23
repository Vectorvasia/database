import random
import time
from threading import Thread

import redis


class QueueMessageWorker(Thread):

    def __init__(self, conn, delay):
        Thread.__init__(self)
        self.conn = conn
        self.delay = delay

    def run(self):
        while True:
            message = self.conn.brpop("queue:")
            if message:
                message_id = int(message[1])

                self.conn.hmset("message:%s" % message_id, {
                    "status": "checking"
                })
                message = self.conn.hmget("message:%s" % message_id, ["sender_id", "consumer_id"])
                sender_id = int(message[0])
                consumer_id = int(message[1])
                self.conn.hincrby("user:%s" % sender_id, "queue", -1)
                self.conn.hincrby("user:%s" % sender_id, "checking", 1)
                time.sleep(self.delay)
                is_spam = random.random() > 0.5
                pipeline = self.conn.pipeline(True)
                pipeline.hincrby("user:%s" % sender_id, "checking", -1)
                if is_spam:
                    sender_username = self.conn.hmget("user:%s" % sender_id, ["login"])[0]
                    pipeline.zincrby("spam:", 1, "user:%s"
                                     % sender_username)
                    pipeline.hmset("message:%s" % message_id, {
                        "status": "blocked"
                    })
                    pipeline.hincrby("user:%s" % sender_id, "blocked", 1)
                    pipeline.publish("spam", "User %s sent spam message: \"%s\""
                                     % (sender_username,
                                        self.conn.hmget("message:%s" % message_id, ["text"])[0]))
                else:
                    pipeline.hmset("message:%s" % message_id, {
                        "status": "sent"
                    })
                    pipeline.hincrby("user:%s" % sender_id, "sent", 1)
                    pipeline.sadd("sentto:%s" % consumer_id, message_id)
                pipeline.execute()


def main():
    handlers_count = 5
    handlers_delay = 3
    for x in range(handlers_count):
        connection = redis.Redis(charset="utf-8", decode_responses=True)
        worker = QueueMessageWorker(connection, random.randint(0, 3))
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()
    while True:
        pass


if __name__ == "__main__":
    main()
