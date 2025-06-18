from django.db import IntegrityError
from .models import Place
from restaurateur.geo import fetch_coordinates


def get_or_create_coordinates(api_key, address, address_cache=None):
    if address_cache is not None and address in address_cache:
        return address_cache[address]

    place, created = Place.objects.get_or_create(address=address)
    if created or not place.latitude or not place.longitude:
        coords = fetch_coordinates(api_key, address)
        if coords:
            place.latitude, place.longitude = coords
            place.save()
        else:
            return None

    if address_cache is not None:
        address_cache[address] = (place.latitude, place.longitude)

    return place.latitude, place.longitude
