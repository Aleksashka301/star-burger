import phonenumbers

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.templatetags.rest_framework import items

from .models import Product, Order, OrderDetail


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    order_details = request.data
    product_ids = list(Product.objects.values_list('id', flat=True))

    for key in ['products', 'firstname', 'lastname', 'phonenumber', 'address']:
        if not key in order_details:
            return Response(f'Поле {key}: Обязательное поле, не должно быть пустым!')

    for key, detail in items(order_details):
        if not detail:
            return Response(f'Поле {key}: Обязательное поле, не должно быть пустым!')

    if not isinstance(order_details['products'], list):
        return Response(
            f'Поле products: Ожидался list со значениями, но был получен "{type(order_details['products'])}".'
        )

    phone = phonenumbers.parse(order_details['phonenumber'], 'RU')
    if not phonenumbers.is_valid_number(phone):
        return Response(f'Поле phonenumber: Введён не правильный номер телефона {order_details['phonenumber']}')
    
    if not order_details['products'][0]['product'] in product_ids:
        return Response(f'Поле product: Введён не верный ключ продукта {order_details['products'][0]['product']}')

    for field in ['firstname', 'lastname', 'phonenumber', 'address']:
        if not isinstance(order_details[field], str):
            return Response(
                f'Поле {field}: Ожидалась строка со значением, но был получен "{type(order_details[field])}".'
            )

    order = Order.objects.create(
        address=order_details['address'],
        first_name=order_details['firstname'],
        last_name=order_details['lastname'],
        phone=order_details['phonenumber'],
    )

    for product in order_details['products']:
        OrderDetail.objects.create(
            order=order,
            product_id=product['product'],
            quantity=product['quantity'],
        )

    return Response(order_details)
