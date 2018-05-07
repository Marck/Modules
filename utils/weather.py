import json
import urllib

from utils import http


class JsonDict:
    def __init__(self, my_dict: dict):
        self._dict = my_dict

    def __getattr__(self, key):
        return self._dict.get(key, None)


async def getcords(address, key):
    try:
        r = await http.get(
            f"https://maps.googleapis.com/maps/api/geocode/json?address={urllib.parse.quote(address)}&key={key}",
            res_method="json"
        )
    except json.JSONDecodeError:
        raise json.JSONDecodeError("The API didn't give any response")

    results = r["results"][0]

    geometry = results["geometry"]["viewport"]["northeast"]
    address = results["formatted_address"]
    country_code = results["address_components"][2]["short_name"]

    return JsonDict({
        "country_code": country_code,
        "address": address,
        "geometry": geometry,
        "latitude": geometry["lat"],
        "longitude": geometry["lng"]
    })


async def getweather(address, key, gmapskey, unit="ca"):
    cords = await getcords(address, gmapskey)
    lat = cords.latitude
    lng = cords.longitude

    try:
        r = await http.get(
            f"https://api.darksky.net/forecast/{key}/{lat},{lng}?units={unit}",
            res_method="json"
        )
    except json.JSONDecodeError:
        raise json.JSONDecodeError("The API didn't give any response")

    return JsonDict({
        "country_code": cords.country_code,
        "address": cords.address,
        "currently": JsonDict(r["currently"]),
        "one": JsonDict(r["daily"]["data"][0]),
        "two": JsonDict(r["daily"]["data"][1]),
        "three": JsonDict(r["daily"]["data"][2]),
        "four": JsonDict(r["daily"]["data"][3]),
        "five": JsonDict(r["daily"]["data"][4]),
    })
