from bs4 import BeautifulSoup
import requests
import re
import logging
from config import HEADERS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Find_movie_bot')


class FindMovies:

    def __init__(self):
        self.url = ''
        self.player = None
        self.players_url = None
        self.script = None

        self.DICT_WITH_MOVIES = {
            "poster": "",
            "about": "",
            "watch": []
        }

    def find_movies(self, url):
        self.url = url
        self.players_url = self.find_players_url()
        self.DICT_WITH_MOVIES['watch'] = self.take_translate()
        return self.DICT_WITH_MOVIES

    def find_players_url(self) -> list:
        players_url = []
        response = requests.get(self.url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        player_web_urls = soup.find_all('iframe')
        for player_url in player_web_urls:
            if player_url['src'].find('voidboost') != -1 or player_url['src'].find(
                    'delivembed') != -1:
                players_url.append(player_url['src'])
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
        soup = BeautifulSoup(response.text, "html.parser")
        find_newest = soup.find('div', class_='carousel-box').find_all('a')
        for val in find_newest:
            if not val['href'].startswith('#'):
                newest_list.append({'id_film': self.make_films_id(val['href']),
                                    'name': val.find('img')['title'],
                                    'url': f"{url}{val['href']}",
                                    'poster': val.find('img')['src']})
        # print(newest_list)
        return newest_list

    def make_films_id(self, href):
        id_film = href.split('/')[3].split('-')[0]
        # print(id_film)
        return id_film
