from random import randint
from threading import Thread
import main as user
from faker import Faker
import redis
import atexit
import time


class User(Thread):
    def __init__(self, connection, user_name, users_list, users_count):
        Thread.__init__(self)
        self.connection = connection
        self.users_list = users_list
        self.users_count = users_count
        user.register(connection, user_name)
        self.user_id = user.sign_in(connection, user_name)
        self.user_name = user_name

    def run(self):
        while True:
            message_text = fake.sentence(nb_words=10, variable_nb_words=True, ext_word_list=None)
            receiver = users[randint(0, users_count - 1)]
            user.create_message(self.connection, message_text, self.user_id, receiver)

            print(f"`{self.user_name}` sent message to `{receiver}`: `{message_text}`")
            time.sleep(1)


def exit_handler():
    redis_connection = redis.Redis(charset="utf-8", decode_responses=True)
    online = redis_connection.smembers("online:")
    redis_connection.srem("online:", list(online))
    print("Exit")


if __name__ == "__main__":
    atexit.register(exit_handler)
    fake = Faker()
    users_count = int(input("Users count = "))
    users = [fake.profile(fields=["username"], sex=None)["username"] for u in range(users_count)]
    threads = []
    for x in range(users_count):
        connection = redis.Redis(charset="utf-8", decode_responses=True)

        print("User: " + users[x])
        threads.append(User(
            redis.Redis(charset="utf-8", decode_responses=True),
            users[x], users, users_count))
    input("Press ENTER to start emulation...")
    for t in threads:
        t.start()
