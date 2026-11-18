import json
import os

FICHIER = os.path.join(os.path.dirname(__file__), "..", "data", "meteo.json")


def charger_meteo():
    try:
        with open(FICHIER) as f:
            h = json.load(f)["hourly"]
    except (OSError, ValueError, KeyError):
        return {}
    return {t: (temp, pluie, code) for t, temp, pluie, code
            in zip(h["time"], h["temperature_2m"], h["precipitation_probability"], h["weather_code"])}


def icone(code):
    if code == 0:
        return "☀️"
    if code in (1, 2):
        return "🌤️"
    if code == 3:
        return "☁️"
    if code in (45, 48):
        return "🌫️"
    if code in (51, 53, 55, 56, 57):
        return "🌦️"
    if code in (61, 63, 65, 66, 67, 80, 81, 82):
        return "🌧️"
    if code in (71, 73, 75, 77, 85, 86):
        return "❄️"
    if code in (95, 96, 99):
        return "⛈️"
    return ""


def texte_meteo(meteo, moment):
    cle = moment.floor("h").strftime("%Y-%m-%dT%H:00")
    if cle not in meteo:
        return ""
    temp, pluie, code = meteo[cle]
    if temp is None:
        return ""
    texte = f"{icone(code)} {round(temp)}°"
    if pluie is not None:
        texte += f" · pluie {pluie}%"
    return texte
