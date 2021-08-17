import sqlite3
import psycopg2
import psycopg2.extras

from config import DATABASE, USER, HOST, PASSWORD
from typing import Union


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
        return True

    def insert_movies(self, data):
        if data:
            for val in data:
                films_id = val['id_film']
                name = val['name']
                url = val['url']
                poster_url = val['poster']
                sql_check_exist = f"select not exists(select * from films where films_id = {films_id}) as e;"
                if self.cur.execute(sql_check_exist).fetchone()[0]:
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


class DBFunc:

    def db_connect(self, sql, values=None, dict_val=True, all_value=True) -> Union[bool, tuple, list, dict]:
        con = None
        try:
            con = psycopg2.connect(database=DATABASE, user=USER, host=HOST,
                                   password=PASSWORD, port='5432')
            con.autocommit = True
            if dict_val:
                cur = con.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            elif not dict_val:
                cur = con.cursor()
            if values:
                cur.execute(sql, values)
            else:
                cur.execute(sql)
            output = cur.fetchall() if all_value else cur.fetchone()
            cur.close()
            return output
        except psycopg2.Error as error:
            # logger.error(f"Помилка в базі: {error}")
            print(f"Помилка в базі: {error}")
            return False
        finally:
            if con is not None:
                con.close()

    def check_user(self, message):
        user_cred = message.from_user
        self.db_connect(f"select * from check_users({user_cred.id}, '{user_cred.username}',"
                        f" '{user_cred.first_name}', '{user_cred.last_name}')")

    def insert_movies(self, data):
        if data:
            for val in data:
                films_id = val['id_film']
                name = val['name']
                url = val['url']
                poster_url = val['poster']
                sql_check_exist = f"select not exists(select * from films where films_id = {films_id}) as e;"
                if self.cur.execute(sql_check_exist).fetchone()[0]:
                    self.cur.execute(f"insert into films (films_id, name, url, poster_url) values ({films_id}, '{name}', '{url}', '{poster_url}')")
                    self.conn.commit()
            self.conn.close()
