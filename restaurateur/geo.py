import logging
import requests


logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s:%(asctime)s:%(message)s'
)


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    try:
        response = requests.get(base_url, params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        })
        response.raise_for_status()
        found_places = response.json()['response']['GeoObjectCollection']['featureMember']

        if not found_places:
            return None

        most_relevant = found_places[0]
        lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")

        return lat, lon
    except (requests.RequestException, KeyError, IndexError, ValueError) as e:
        logging.warning(f"Ошибка при геокодировании адреса '{address}': {e}")
        return None
