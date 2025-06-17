from django.db import IntegrityError
from .models import Place
from restaurateur.geo import fetch_coordinates


def get_or_create_coordinates(api_key, address):
    try:
        place = Place.objects.get(address=address)
        return place.latitude, place.longitude
    except Place.DoesNotExist:
        coords = fetch_coordinates(api_key, address)
        if coords is None:
            return None

        lat, lon = coords
        try:
            Place.objects.create(address=address, latitude=lat, longitude=lon)
        except IntegrityError:
            place = Place.objects.get(address=address)
            return place.latitude, place.longitude

        return lat, lon
