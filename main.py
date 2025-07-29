import requests
from json import loads, dumps
import sys
sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
import os

load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
CANTEEN_NUM = os.getenv("CANTEEN_NUM")
LOGIN_URL = "https://app.strava.cz/api/login"
DATA_URL = 'https://app.strava.cz/api/objednavky'

login_headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,cs;q=0.8,cs-CZ;q=0.7",
    "content-type": "text/plain;charset=UTF-8",
    "origin": "https://app.strava.cz",
    "priority": "u=1, i",
    "referer": "https://app.strava.cz/en/prihlasit-se?jidelna",
    "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
}
login_data = {
    "cislo": CANTEEN_NUM,
    "jmeno": USERNAME,
    "heslo": PASSWORD,
    "zustatPrihlasen": False,
    "environment": "W",
    "lang": "EN"
}

def parser(src):
    new = [src[i] for i in src if src[i][1]["alergeny"]]

    clean_src = []

    for day in new:
        for course in day:
            if "Oběd" in course["druh_popis"] and course["pocet"] != 0:
                clean_src.append({
                    "date": course["datum"],
                    "meal_num": course["druh_popis"],
                    "dish_name": course["nazev"],
                    "num_and_name": f"{course['druh_popis']}: {course['nazev']}"
                })
    return clean_src

def getDataStrava(login_data = login_data, login_headers = login_headers):
    response = requests.post(LOGIN_URL, headers = login_headers, json = login_data)
    login_data = response.json()

    sid = login_data['sid']
    s5url = login_data["s5url"]

    data = f'{"{"}"cislo":"{CANTEEN_NUM}","sid":"{sid}","s5url":"{s5url}","lang":"EN","konto":0,"podminka":"","ignoreCert":"false"{"}"}'
    response = requests.post(DATA_URL, data = data)

    raw_src = loads(response.text)

    return raw_src

def getDate():
    response = requests.get("https://api.timezonedb.com/v2.1/get-time-zone?key=21NHSAQ7TSX4&format=json&by=zone&zone=Europe/Prague") # requests data from the API
    date = response.json()["formatted"] # selects the correct format
    date_string = date[0:10] # selects the needed part

    date_list = date_string.split("-") # splits the string into a list

    return f"{date_list[2]}.{date_list[1]}.{date_list[0]}" # returns the formatted date

def main():
    date = getDate()

    raw_src = getDataStrava()
    clean_src = parser(raw_src)

    today = next((meal for meal in clean_src if meal["date"] == date), None)

    return today







main()