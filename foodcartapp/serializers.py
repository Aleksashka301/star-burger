from rest_framework import serializers

from foodcartapp.models import Order, OrderDetail, Product


class OrderDetailSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        source='products',
        queryset=Product.objects.all()
    )

    class Meta:
        model = OrderDetail
        fields = ['product', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    products = OrderDetailSerializer(
        many=True,
        source='items',
        allow_empty=False
    )

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address', 'products']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        order_details = []
        for item_data in items_data:
            product = item_data['products']
            quantity = item_data['quantity']
            order_details.append(OrderDetail(
                order=order,
                products=product,
                quantity=quantity,
                price=product.price
            ))

        OrderDetail.objects.bulk_create(order_details)
        return order

