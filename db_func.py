import sqlite3
import psycopg2
import psycopg2.extras

from config import DATABASE, USER, HOST, PASSWORD
from typing import Union


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
        return True

    def insert_movies(self, data):
        if data:
            for val in data:
                films_id = val['id_film']
                name = val['name']
                url = val['url']
                poster_url = val['poster']
                sql = f"select * from check_films({films_id}, '{name}', '{url}', '{poster_url}')"
                self.db_connect(sql=sql)

    def search_film_id(self, id_film):
        info = self.db_connect(f'select url from films where films_id = {id_film}', all_value=False)
        if info:
            return dict(info)
        else:
            raise Exception('Nothing found')

    def count_users(self):
        sql = "select count(*) from users where (users.last_uses - users.create_date) > interval '30 days'" \
              " and last_uses::text not like '2021-08-13%';"
        info = self.db_connect(sql, all_value=False)
        return dict(info)

