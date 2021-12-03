from bs4 import BeautifulSoup
import requests
import re
import logging
from random import randint
from config import HEADERS
from db_func import DBFunc
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Find_movie_bot')


class FindMovies:

    def __init__(self):
        self.url = ''
        self.player = None
        self.players_url = None
        self.script = None
        self.base_url = 'http://baskino.me/'

        self.DICT_WITH_MOVIES = {
            "poster": "",
            "about": "",
            "watch": []
        }

    def find_movies(self, url):
        self.url = url
        self.players_url = self.find_players_url()
        if self.players_url:
            self.DICT_WITH_MOVIES['watch'] = self.take_translate()
            return self.DICT_WITH_MOVIES
        else:
            return False

    def find_players_url(self) -> list:
        players_url = []
        response = requests.get(self.url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        player_web_urls = soup.find_all('iframe')
        for player_url in player_web_urls:
            if 'voidboost' in player_url.get('src') or 'delivembed' in player_url.get('src'):
                players_url.append(player_url.get('src'))
        self.find_poster_url(soup)
        return players_url

    def find_poster_url(self, soup):
        poster_url = soup.find("div", {"class": "mobile_cover"}).find('img')
        self.DICT_WITH_MOVIES['poster'] = poster_url['src']

    def get_players_script(self, url):
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        script = soup.find('body').find('script').string
        return self.parse_script(script=script)

    def take_translate(self) -> list:
        translate_list = []
        response = requests.get(self.find_players_url()[0], headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        find_translate = soup.find("select", {"id": "translator-name"}).find_all('option')
        for val in find_translate:
            if val['data-token']:
                quality = self.get_players_script(
                    f'https://voidboost.net/movie/{val["data-token"]}/iframe?h=baskino.me')
                translate_list.append({'name': val.text, 'quality': quality['quality']})
        return translate_list

    def parse_script(self, script) -> dict:
        quality_dict = {"quality": {
            "240p": {
                "m3u8": [],
                "mp4": []
            },
            "360p": {
                "m3u8": [],
                "mp4": []
            },
            "480p": {
                "m3u8": [],
                "mp4": []
            },
            "720p": {
                "m3u8": [],
                "mp4": []
            },
            "1080p": {
                "m3u8": [],
                "mp4": []
            }
        }}
        regex = re.compile('\n^(.*?):(.*?)$|,', re.MULTILINE)
        js_text = re.findall(regex, script)  # find first item
        for val in js_text:
            if val[0].find('file') != -1:
                for quality in val[1].replace('"', '').split(','):
                    good_string = quality.replace(' ', '')
                    if good_string.startswith('[240p]'):
                        extens = good_string.replace('[240p]', '').split('or')
                        quality_dict['quality']['240p']['m3u8'] = extens[0]
                        quality_dict['quality']['240p']['mp4'] = extens[1]
                    elif good_string.startswith('[360p]'):
                        extens = good_string.replace('[360p]', '').split('or')
                        quality_dict['quality']['360p']['m3u8'] = extens[0]
                        quality_dict['quality']['360p']['mp4'] = extens[1]
                    elif good_string.startswith('[480p]'):
                        extens = good_string.replace('[480p]', '').split('or')
                        quality_dict['quality']['480p']['m3u8'] = extens[0]
                        quality_dict['quality']['480p']['mp4'] = extens[1]
                    elif good_string.startswith('[720p]'):
                        extens = good_string.replace('[720p]', '').split('or')
                        quality_dict['quality']['720p']['m3u8'] = extens[0]
                        quality_dict['quality']['720p']['mp4'] = extens[1]
                    elif good_string.startswith('[1080p]'):
                        extens = good_string.replace('[1080p]', '').split('or')
                        quality_dict['quality']['1080p']['m3u8'] = extens[0]
                        quality_dict['quality']['1080p']['mp4'] = extens[1]
        return quality_dict

    def find_newest(self):
        newest_list = []
        url = 'http://baskino.me'
        response = requests.get(url, headers=HEADERS)
        if response:
            soup = BeautifulSoup(response.text, "html.parser")
            find_newest = soup.find('div', class_='carousel-box').find_all('a')
            for val in find_newest:
                if not val['href'].startswith('#'):
                    newest_list.append({'id_film': self.make_films_id(val['href']),
                                        'name': val.find('img')['title'],
                                        'url': f"{url}{val['href']}",
                                        'poster': val.find('img')['src']})
            DBFunc().insert_movies(newest_list)
            return {'error': False, 'movies': newest_list}
        else:
            return {'error': 'Сталася помилка при з\'єднанні з фільмовим сервером, спробуйте пізніше',
                    'movies': newest_list}

    def make_films_id(self, href, search=False):
        if search:
            id_film = href.split('/')[5].split('-')[0]
        else:
            id_film = href.split('/')[3].split('-')[0]
        return id_film

    def search_films(self, name):
        films_list = []
        data = {'story': name, 'do': 'search', 'subaction': 'search', 'search_start': 1}
        response = requests.post(self.base_url, headers=HEADERS,
                                 data=data)
        soup = BeautifulSoup(response.text, "html.parser")
        films = soup.find_all('div', class_='postcover')
        navigation = soup.find('div', class_='navigation')
        if films:
            films_list.extend(films)
            # print('first page', films_list)
            if navigation:
                last_page = navigation.find_all('a')[-2].text
                self.search_film_another_page(data, last_page, films_list)
        parsed_films = self.search_film_in_page(films_list)
        # print(parsed_films)
        return parsed_films

    def search_film_another_page(self, data, last_page, films_list):
        url = 'http://baskino.me/'
        for page in range(2, int(last_page)):
            data['search_start'] = page
            response = requests.post(url, headers=HEADERS,
                                     data=data)
            soup = BeautifulSoup(response.text, "html.parser")
            films = soup.find_all('div', class_='postcover')
            films_list.extend(films)
            # print(f'page number: {page}\nfilms list: {films_list}')

    def search_film_in_page(self, data):
        parsed_films = []
        for val in data:
            if val.find('a')['href'].startswith(f'{self.base_url}films/'):
                parsed_films.append({'id_film': self.make_films_id(val.find('a')['href'], search=True),
                                   'name': val.find('img')['title'],
                                   'url': val.find('a')['href'],
                                   'poster': val.find('img')['src']})
        DBFunc().insert_movies(parsed_films)
        return parsed_films

    def get_random_bs(self):
        film_list = []
        response = requests.get('http://baskino.me/top/', headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        tbody = soup.find('ul', class_='content_list_top')
        tbody_top_raw = tbody.find_all('a')
        for val in tbody_top_raw:
            if '/films/' in val.get('href'):
                film_list.append(val.get('href'))
        movie_ans = self.format_top_movies(film_list, random=randint(0, len(tbody_top_raw)))
        return movie_ans

    @staticmethod
    def format_top_movies(data, random):
        return data[random]


