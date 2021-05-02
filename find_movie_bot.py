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
        self.DICT_WITH_MOVIES = {
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
        }

    def find_movies(self, url):
        self.url = url
        self.players_url = self.find_players_url()
        self.script = self.get_players_script()
        return self.parse_script()

    def find_players_url(self) -> list:
        players_url = []
        response = requests.get(self.url, headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        player_web_urls = soup.find_all('iframe')
        for player_url in player_web_urls:
            if player_url['src'].find('voidboost') != -1 or player_url['src'].find(
                    'delivembed') != -1:
                players_url.append(player_url['src'])
        return players_url

    def get_players_script(self) -> str:
        response = requests.get(self.find_players_url()[0], headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")
        script = soup.find('body').find('script').string
        return script

    def parse_script(self) -> dict:
        regex = re.compile('\n^(.*?):(.*?)$|,', re.MULTILINE)
        js_text = re.findall(regex, self.script)  # find first item
        for val in js_text:
            if val[0].find('file') != -1:
                for quality in val[1].replace('"', '').split(','):
                    good_string = quality.replace(' ', '')
                    if good_string.startswith('[240p]'):
                        extens = good_string.replace('[240p]', '').split('or')
                        self.DICT_WITH_MOVIES['240p']['m3u8'].insert(0, extens[0])
                        self.DICT_WITH_MOVIES['240p']['mp4'].insert(0, extens[1])
                    elif good_string.startswith('[360p]'):
                        extens = good_string.replace('[360p]', '').split('or')
                        self.DICT_WITH_MOVIES['360p']['m3u8'].insert(0, extens[0])
                        self.DICT_WITH_MOVIES['360p']['mp4'].insert(0, extens[1])
                    elif good_string.startswith('[480p]'):
                        extens = good_string.replace('[480p]', '').split('or')
                        self.DICT_WITH_MOVIES['480p']['m3u8'].insert(0, extens[0])
                        self.DICT_WITH_MOVIES['480p']['mp4'].insert(0, extens[1])
                    elif good_string.startswith('[720p]'):
                        extens = good_string.replace('[720p]', '').split('or')
                        self.DICT_WITH_MOVIES['720p']['m3u8'].insert(0, extens[0])
                        self.DICT_WITH_MOVIES['720p']['mp4'].insert(0, extens[1])
                    elif good_string.startswith('[1080p]'):
                        extens = good_string.replace('[1080p]', '').split('or')
                        self.DICT_WITH_MOVIES['1080p']['m3u8'].insert(0, extens[0])
                        self.DICT_WITH_MOVIES['1080p']['mp4'].insert(0, extens[1])
        return self.DICT_WITH_MOVIES
