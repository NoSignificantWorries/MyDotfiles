#!/usr/bin/python3

import json
import requests
from pathlib import Path
from datetime import datetime

with open(Path("~/.config/eww/widgets/bar/scripts/api.key").expanduser()) as file:
    KEY = file.read().strip()

CITY = "Novosibirsk"
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={KEY}&units=metric&lang=ru"

TEMP = ""
ICONS = {
    "day": {
        "clear": "",
        "fog": "",
        "snow": "",
        "snow-wind": "",
        "hail": "",
        "windy": "",
        "cloudy": "",
        "cloudy-windy": "",
        "cloudy-gusts": "",
        "sleet": "",
        "sleet-storm": "",
        "showers": "",
        "storm-showers": "",
        "sprinkle": "",
        "rain": "",
        "rain-mix": "",
        "rain-wind": "",
        "lightning": "",
        "thunderstorm": "",
        "thunderstorm-snowy": "",
    },
    "night": {
        "clear": "",
        "fog": "",
        "snow": "",
        "snow-wind": "",
        "hail": "",
        "windy": "",
        "cloudy": "",
        "cloudy-windy": "",
        "cloudy-gusts": "",
        "sleet": "",
        "sleet-storm": "",
        "showers": "",
        "storm-showers": "",
        "sprinkle": "",
        "rain": "",
        "rain-mix": "",
        "rain-wind": "",
        "lightning": "",
        "thunderstorm": "",
        "thunderstorm-snowy": "",
    }
}

def match_icon(temp):
    if temp <= 0:
        idx = 0
    elif temp <= 10:
        idx = 1
    elif temp <= 23:
        idx = 2
    elif temp <= 30:
        idx = 3
    else:
        idx = 4
    return TEMP[idx]


def get_weather_icon(weather_id, icon_code):
    is_night = icon_code.endswith('n')
    time_of_day = "night" if is_night else "day"

    weather_map = {
        # Гроза (200-232)
        range(200, 233): "thunderstorm",

        # Морось (300-321)
        range(300, 322): "sprinkle",

        # Дождь (500-531)
        range(500, 532): "rain",

        # Снег (600-622)
        range(600, 623): "snow",

        # Атмосферные явления (700-781)
        701: "fog", 711: "fog", 721: "fog", 731: "fog",
        741: "fog", 751: "fog", 761: "fog", 762: "fog",
        771: "windy", 781: "windy",

        # Облачность (800-804)
        800: "clear",
        range(801, 805): "cloudy",
    }

    for code_range, icon_key in weather_map.items():
        if isinstance(code_range, range):
            if weather_id in code_range:
                return ICONS[time_of_day].get(icon_key, ICONS[time_of_day]["cloudy"])
        elif weather_id == code_range:
            return ICONS[time_of_day].get(icon_key, ICONS[time_of_day]["cloudy"])

    return ICONS[time_of_day].get("cloudy", "")


response = requests.get(URL)

if response.status_code == 200:
    data = response.json()

    icon_code = data["weather"][0]["icon"]
    weather_id = data["weather"][0]["id"]

    weather_icon = get_weather_icon(weather_id, icon_code)

    temp_real = round(data["main"]["temp"], 1)
    tr_icon = match_icon(temp_real)
    temp_feels = round(data["main"]["feels_like"], 1)
    tf_icon = match_icon(temp_feels)

    weather = {
        "data": True,
        "label": data["weather"][0]["main"],
        "id": data["weather"][0]["id"],
        "icon": weather_icon,
        "temp": {
            "real": {
                "t": temp_real,
                "i": tr_icon
            },
            "feels": {
                "t": temp_feels,
                "i": tf_icon
            }
        },
        "pressure": data["main"]["pressure"],
        "humidity": data["main"]["humidity"],
        "wind": {
            "speed": data["wind"]["speed"] if "wind" in data else 0,
            "orient": data["wind"]["deg"] if "wind" in data and "deg" in data["wind"] else 0
        },
        "visibility": data.get("visibility", 10000) / 1000,
        "sun": {
            "rise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M"),
            "set": datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M")
        }
    }

    print(json.dumps(weather))
else:
    print(json.dumps({"data": False}))

