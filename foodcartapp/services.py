from django.db import transaction
from .models import Order, OrderDetail, Product


@transaction.atomic
def create_order_with_items(order_data, items_data):
    order = Order.objects.create(**order_data)

    for item in items_data:
        product = Product.objects.get(id=item['product_id'])

        order_item = OrderDetail(
            order=order,
            products=product,
            quantity=item['quantity'],
            price=product.price
        )

        order_item.full_clean()
        order_item.save()

    return order
