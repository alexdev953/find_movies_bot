import sqlite3


class DbFunc:

    def __init__(self):
        self.conn = None
        self.cur = self.db_connect()

    def db_connect(self):
        self.conn = sqlite3.connect('bot.db')
        cur = self.conn.cursor()
        return cur

    def check_user(self, user_id, username, firstname, lastname):
        # logger.debug(f'Check USER {user_id}, {first_name}, {user_name}')
        self.cur.execute(f"select userid from users where userid = {user_id}")
        info = self.cur.fetchall()
        if not info:
            self.cur.execute(f"insert into users (userid, username, firstname, lastname) values ('{user_id}', '{username}', '{firstname}', '{lastname}')")
            self.conn.commit()
            self.conn.close()
        else:
            self.last_uses(user_id)

    def last_uses(self, user_id):
        self.cur.execute(f"update users set last_uses = datetime('now', 'localtime') where userid = {user_id};")
        self.conn.commit()
        self.conn.close()
