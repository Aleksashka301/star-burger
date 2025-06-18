from geopy.distance import distance

from places.services import get_or_create_coordinates


def get_distance(api_key, address1, address2, address_cache=None):
    coords1 = get_or_create_coordinates(api_key, address1, address_cache)
    coords2 = get_or_create_coordinates(api_key, address2, address_cache)

    if not coords1 or not coords2:
        return None

    return round(distance(coords1, coords2).km, 1)


def get_common_restaurants(order, product_to_restaurants):
    product_ids = [item.products.id for item in order.items.all()]
    restaurant_sets = [
        product_to_restaurants[product_id]
        for product_id in product_ids
        if product_id in product_to_restaurants
    ]
    if restaurant_sets:
        return set.intersection(*restaurant_sets)
    return set()


def get_restaurants_with_distances(common_restaurants, customer_address, yandex_key, address_cache):
    restaurants_with_distances = []
    for name, address in common_restaurants:
        distance_km = get_distance(yandex_key, address, customer_address, address_cache)
        restaurants_with_distances.append({
            'name': name.replace('Star Burger', 'BRB'),
            'distance': f'{distance_km} км' if distance_km else 'Расстояние не определено',
        })

    restaurants_with_distances.sort(key=lambda r: r['distance'])
    return restaurants_with_distances

