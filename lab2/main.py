from functools import partial

import consolemenu
import redis
import atexit


def register(conn, username):
    if conn.hget("users:", username):
        return None

    user_id = conn.incr("user:id:")

    pipeline = conn.pipeline(True)

    pipeline.hset("users:", username, user_id)

    pipeline.hmset("user:%s" % user_id, {
        "login": username,
        "id": user_id,
        "queue": 0,
        "checking": 0,
        "blocked": 0,
        "sent": 0,
        "delivered": 0
    })
    pipeline.execute()
    return user_id


def sign_in(conn, username) -> int:
    user_id = conn.hget("users:", username)

    if not user_id:
        print("User does not exist %s" % username)
        return -1

    conn.sadd("online:", username)
    return int(user_id)


def sign_out(conn, user_id) -> int:
    try:
        return conn.srem("online:", conn.hmget("user:%s" % user_id, ["login"])[0])
    except redis.exceptions.DataError:
        ...


def create_message(conn, message_text, sender_id, consumer) -> int:
    message_id = int(conn.incr("message:id:"))
    consumer_id = int(conn.hget("users:", consumer))

    if not consumer_id:
        print("User does not exist %s, unable to send message" % consumer)
        return

    pipeline = conn.pipeline(True)

    pipeline.hmset("message:%s" % message_id, {
        "text": message_text,
        "id": message_id,
        "sender_id": sender_id,
        "consumer_id": consumer_id,
        "status": "created"
    })
    pipeline.lpush("queue:", message_id)
    pipeline.hmset("message:%s" % message_id, {
        "status": "queue"
    })
    pipeline.zincrby("sent:", 1, "user:%s" %
                     conn.hmget("user:%s" % sender_id, ["login"])[0])
    pipeline.hincrby("user:%s" % sender_id, "queue", 1)
    pipeline.execute()

    return message_id


def print_messages(connection, user_id):
    messages = connection.smembers("sentto:%s" % user_id)
    for message_id in messages:
        message = connection.hmget("message:%s" % message_id, [
                                   "sender_id", "text", "status"])
        sender_id = message[0]
        print("From: %s - %s" % (connection.hmget("user:%s" %
                                                  sender_id, ["login"])[0], message[1]))
        if message[2] != "delivered":
            pipeline = connection.pipeline(True)
            pipeline.hset("message:%s" % message_id, "status", "delivered")
            pipeline.hincrby("user:%s" % sender_id, "sent", -1)
            pipeline.hincrby("user:%s" % sender_id, "delivered", 1)
            pipeline.execute()


def main_menu(msg="") -> int:
    menu = consolemenu.SelectionMenu(["Register", "Log in"], title=f"Menu({msg})")
    menu.show()
    if menu.is_selected_item_exit():
        exit()
    return menu.selected_option + 1


def user_menu(login) -> int:
    menu = consolemenu.SelectionMenu(["Sign out", "Send message", "Messages inbox", "Message statistic"],
                                     title=f"User menu for `{login}`")
    menu.show()
    if menu.is_selected_item_exit():
        exit()
    return menu.selected_option + 1


def main():
    def exit_handler():
        sign_out(connection, current_user_id)

    atexit.register(exit_handler)
    loop = True
    signed_in = False
    current_user_id = -1
    connection = redis.Redis(charset="utf-8", decode_responses=True, port=6379)
    menu = main_menu

    while loop:
        choice = menu()

        if choice == 1:
            if not signed_in:
                login = input("Please enter your username: ")
                register(connection, login)
            else:
                sign_out(connection, current_user_id)
                connection.publish("users", "User %s signed out"
                                   % connection.hmget("user:%s" % current_user_id, ["login"])[0])
                signed_in = False
                current_user_id = -1
                menu = main_menu

        elif choice == 2:
            if signed_in:
                message = input("Please enter message text: ")
                recipient = input("Please enter recipient username: ")

                if create_message(connection, message, current_user_id, recipient):
                    print("Sending message...")
            else:
                login = input("Please enter your login: ")
                current_user_id = sign_in(connection, login)
                signed_in = current_user_id != -1
                if signed_in:
                    connection.publish("users", "User %s signed in"
                                       % connection.hmget("user:%s" % current_user_id, ["login"])[0])
                    menu = partial(user_menu, login)
                else:
                    menu = partial(main_menu, f"user `{login}` is not registered")

        elif choice == 3:
            if signed_in:
                print_messages(connection, current_user_id)
                input(" Please press enter tp continue...")
            else:
                loop = False

        elif choice == 4:
            current_user = connection.hmget("user:%s" % current_user_id,
                                            ["queue", "checking", "blocked", "sent", "delivered"])
            print("In queue: %s\nChecking: %s\nBlocked: %s\nSent: %s\nDelivered: %s" %
                  tuple(current_user))
            input("Please press enter to continue...")


if __name__ == "__main__":
    main()
