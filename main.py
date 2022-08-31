import time
import json
import cv2
import urllib.request
import numpy as np
from deepface import DeepFace
import requests
import os
from contextlib import suppress


def get_image_from_url(url):
    req = urllib.request.urlopen(url)
    arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)
    return img


faceCascade = cv2.CascadeClassifier("x.xml")
ACCOUNT = json.loads(open('account.json', 'r').read())


class PassException:
    def __enter__(self):
        pass

    def __exit__(self, *args):
        return True


class TinderProfile:
    def __init__(self, json_child: dict, x_auth_token=None):
        self.json_child = json_child
        self.id = ''
        self.verified = False
        self.bio = ''
        self.birth_date = ''
        self.name = ''
        self.photos = []
        self.gender = 0
        self.city = ''
        self.show_gender_on_profile = False
        self.recently_active = False
        self.online_now = False
        self.distance_mi = 0
        self.distance_km = 0
        self.teaser = ''
        self.s_number = 0
        self.constructor()
        self.match = False
        self.x_auth_token = x_auth_token

    def constructor(self):
        root_user = self.json_child['user']
        with suppress(Exception):
            self.id = root_user['_id']
        with suppress(Exception):
            self.verified = True if len(root_user['badges']) > 0 else False
        with suppress(Exception):
            self.bio = root_user['bio'].replace("'", "")
        with suppress(Exception):
            self.birth_date = root_user['birth_date']
        with suppress(Exception):
            self.name = root_user['name']
        with suppress(Exception):
            self.photos = [i['url'] for i in root_user['photos']]
        with suppress(Exception):
            self.gender = root_user['gender']
        with suppress(Exception):
            self.city = root_user['city']['name'].replace("'", '')
        with suppress(Exception):
            self.show_gender_on_profile = root_user['show_gender_on_profile']
        with suppress(Exception):
            self.recently_active = root_user['recently_active']
        with suppress(Exception):
            self.online_now = root_user['online_now']
        with suppress(Exception):
            self.distance_mi = self.json_child['distance_mi']
        with suppress(Exception):
            self.distance_km = int(self.distance_mi / 1.60934)
        with suppress(Exception):
            self.teaser = self.json_child['teaser']['string'].replace("'", '')
        with suppress(Exception):
            self.s_number = self.json_child['s_number']

    def action(self, option=None):
        if option and self.x_auth_token:
            try:
                url = f"https://api.gotinder.com/{option}/{self.id}"
                querystring = {"locale": "en"}
                payload = {"s_number": self.s_number}
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0',
                    'Accept': 'application/json',
                    'Accept-Language': 'en,en-US',
                    'app-session-id': 'c9587229-8478-4eb0-8097-c3fd4954729c',
                    'app-session-time-elapsed': '15781',
                    'app-version': '1034202',
                    'persistent-device-id': '4355d2a2-30fb-4cac-959f-14b5710e6fed',
                    'tinder-version': '3.42.2',
                    'x-auth-token': self.x_auth_token,
                    'user-session-time-elapsed': '15708',
                    'x-supported-image-formats': 'webp,jpeg',
                    'platform': 'web',
                    'Origin': 'https://tinder.com',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'cross-site',
                    'Referer': 'https://tinder.com/',
                    'Connection': 'keep-alive',
                }

                response = requests.request(
                    "POST", url, json=payload, headers=headers, params=querystring, timeout=30)
                if response.status_code == 200:
                    if response.json()['match']:
                        self.match = True

                    return 1
                else:
                    print('error: change X-AUTH_TOKEN')
            except Exception as e:
                print(f'error {e}')

        else:
            print('Please add x_auth_token=xxxxxx')

    def like(self, colorful=None):
        print('Liking...')
        self.action('like')

    def dislike(self):
        print('Disliking...')
        self.action('pass')


class Tinder:
    def __init__(self, x_auth_token):
        self.x_auth_token = x_auth_token

    def get_potential_matches(self, verbose=False):
        url = "https://api.gotinder.com/v2/recs/core"

        querystring = {"locale": "en"}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0',
            'Accept': 'application/json',
            'Accept-Language': 'en,en-US',
            'app-session-id': 'c9587229-8478-4eb0-8097-c3fd4954729c',
            'app-session-time-elapsed': '15781',
            'app-version': '1034202',
            'persistent-device-id': '4355d2a2-30fb-4cac-959f-14b5710e6fed',
            'tinder-version': '3.42.2',
            'x-auth-token': self.x_auth_token,
            'user-session-time-elapsed': '15708',
            'x-supported-image-formats': 'webp,jpeg',
            'platform': 'web',
            'Origin': 'https://tinder.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Referer': 'https://tinder.com/',
        }

        response = requests.request(
            "GET", url, headers=headers, params=querystring, timeout=30)
        if verbose:
            print(response.text)
        if response.status_code == 200 and response.json()['meta'] and response.json()['meta']['status'] == 200:
            try:
                return response.json()['data']['results']
            except Exception as e:
                if verbose:
                    print(f'error: {e}')

            if "1800000}}" in response.text:
                return 2
        print(f'response: {response.text}')
        return -1


def loopmain():
    while True:
        TinderAcc = Tinder(ACCOUNT["tinder_auth"])
        matches = TinderAcc.get_potential_matches(verbose=False)
        if matches == 2:
            time.sleep(60 * 1)
        else:
            for potential_match in matches:
                try:
                    profile = TinderProfile(
                        potential_match, ACCOUNT["tinder_auth"])
                    image = get_image_from_url(profile.photos[0])
                    cv2.imwrite("keko.jpg", image)
                    obj = DeepFace.analyze(img_path="keko.jpg", actions=[
                                           'age', 'gender', 'race'], enforce_detection=False)
                    if (obj['gender'] == ACCOUNT['gender'] and obj["dominant_race"] in ACCOUNT["race"]):
                        profile.like()
                        print(f'liked : {profile.name} - {profile.birth_date} - {profile.distance_km} KM\n\nAI info : \n- Age : '+ str(obj['age']) + "\n- Gender : "+ obj['gender'] + "\n- Race : "+ obj['dominant_race'])
                        requests.get("https://api.telegram.org/bot"+ACCOUNT["telegram_token"]+"/sendPhoto", params={
                            "photo": profile.photos[0],
                            "chat_id": ACCOUNT["chat_id"],
                            "caption": f'liked : {profile.name} - {profile.birth_date} - {profile.distance_km} KM\n\nAI info : \n- Age : '+ str(obj['age']) + "\n- Gender : "+ obj['gender'] + "\n- Race : "+ obj['dominant_race'] 
                        }, timeout=30)
                    else:
                        profile.dislike()
                        print(f'Dislike : {profile.name} - {profile.birth_date} - {profile.distance_km} KM\n\nAI info : \n- Age : '+ str(obj['age']) + "\n- Gender : "+ obj['gender'] + "\n- Race : "+ obj['dominant_race'])
                        requests.get("https://api.telegram.org/bot"+ACCOUNT["telegram_token"]+"/sendPhoto", params={
                            "photo": profile.photos[0],
                            "chat_id": ACCOUNT["chat_id"],
                            "caption": f'Dislike : {profile.name} - {profile.birth_date} - {profile.distance_km} KM\n\nAI info : \n- Age : '+ str(obj['age']) + "\n- Gender : "+ obj['gender'] + "\n- Race : "+ obj['dominant_race']                         }, timeout=30)
                except BaseException as e:
                    profile.dislike()
                    print(r"no face " + str(e))
        print('Searching New Matches...')


if __name__ == '__main__':
    loopmain()
