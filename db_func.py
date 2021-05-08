import sqlite3


class DbFunc:

    def __init__(self):
        self.conn = None
        self.cur = self.db_connect()

    def db_connect(self):
        self.conn = sqlite3.connect('bot.db')
        cur = self.conn.cursor()
        return cur

    def check_user(self, message):
        user_cred = message.from_user
        # logger.debug(f'Check USER {user_id}, {first_name}, {user_name}')
        self.cur.execute(f"select userid from users where userid = {user_cred.id}")
        info = self.cur.fetchall()
        if not info:
            self.cur.execute(f"insert into users (userid, username, firstname, lastname) values "
                             f"('{user_cred.id}', '{user_cred.username}', '{user_cred.first_name}', '{user_cred.last_name}')")
            self.conn.commit()
            self.conn.close()
        else:
            self.cur.execute(f"update users set last_uses = datetime('now', 'localtime') where userid = {user_cred.id};")
            self.conn.commit()
            self.conn.close()

    def insert_movies(self, data):
        for val in data:
            films_id = val['id_film']
            name = val['name']
            url = val['url']
            poster_url = val['poster']
            self.cur.execute(f"insert into films (films_id, name, url, poster_url) values ({films_id}, '{name}', '{url}', '{poster_url}')")
            self.conn.commit()
        self.conn.close()

    def search_film_id(self, id_film):
        self.cur.execute(f'select url from films where films_id = {id_film}')
        info = self.cur.fetchone()
        if info:
            self.conn.close()
            return info[0]
        else:
            raise Exception('Nothing found')
