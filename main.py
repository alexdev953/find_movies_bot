from bs4 import BeautifulSoup
import requests
import re
import json

URl = ""
headers = {
    "user-agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    "accept-language":
        "uk,ru-RU;q=0.9,ru;q=0.8,en-US;q=0.7,en;q=0.6"
}


def find_players_url() -> list:
    players_url = []
    response = requests.get(URl, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    player_web_urls = soup.find_all('iframe')
    for player_url in player_web_urls:
        if player_url['src'].find('voidboost') != -1 or player_url['src'].find(
                'delivembed') != -1:
            players_url.append(player_url['src'])
    return players_url


print(find_players_url()[0])

response = requests.get(find_players_url()[0], headers=headers)
soup = BeautifulSoup(response.text, "html.parser")
script = soup.find('body').find('script').string

regex = re.compile('\n^(.*?):(.*?)$|,', re.MULTILINE)
js_text = re.findall(regex, script)  # find first item
dict_with_movies = {
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
for val in js_text:
    if val[0].find('file') != -1:
        for quality in val[1].replace('"', '').split(','):
            good_string = quality.replace(' ', '')
            if good_string.startswith('[240p]'):
                extens = good_string.replace('[240p]', '').split('or')
                dict_with_movies['240p']['m3u8'].append(extens[0])
                dict_with_movies['240p']['mp4'].append(extens[1])
            elif good_string.startswith('[360p]'):
                extens = good_string.replace('[360p]', '').split('or')
                dict_with_movies['360p']['m3u8'].append(extens[0])
                dict_with_movies['360p']['mp4'].append(extens[1])
            elif good_string.startswith('[480p]'):
                extens = good_string.replace('[480p]', '').split('or')
                dict_with_movies['480p']['m3u8'].append(extens[0])
                dict_with_movies['480p']['mp4'].append(extens[1])
            elif good_string.startswith('[720p]'):
                extens = good_string.replace('[720p]', '').split('or')
                dict_with_movies['720p']['m3u8'].append(extens[0])
                dict_with_movies['720p']['mp4'].append(extens[1])
            elif good_string.startswith('[1080p]'):
                extens = good_string.replace('[1080p]', '').split('or')
                dict_with_movies['1080p']['m3u8'].append(extens[0])
                dict_with_movies['1080p']['mp4'].append(extens[1])
print(json.dumps(dict_with_movies, indent=2))
