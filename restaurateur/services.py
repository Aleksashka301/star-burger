from geopy import distance

from places.services import get_or_create_coordinates


def get_distance(api_key, restaurant_address, client_address):
    restaurant_coordinates = get_or_create_coordinates(api_key, restaurant_address)
    client_coordinates = get_or_create_coordinates(api_key, client_address)

    return round(distance.distance(restaurant_coordinates, client_coordinates).km, 1)

