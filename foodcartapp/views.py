from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response

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
    if not order_details.get('products'):
        return Response('Поле products: Обязательное поле с типом list и оно не должно быть пустым!')
    elif isinstance(order_details['products'], str):
        return Response(
            f'Поле products: Ожидался list со значениями, но был получен "{type(order_details['products'])}".'
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
