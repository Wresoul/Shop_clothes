from rest_framework import serializers
from .models import Order, OrderItem
from shop.models import Goods

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'name', 'price', 'quantity', 'created_timestamp']
        read_only_fields = ['id', 'created_timestamp']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)
    user = serializers.CharField(source='user.username', read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'created_timestamp', 'phone_number', 'requires_delivery',
            'delivery_address', 'payment_on_get', 'is_paid', 'status',
            'items', 'total_price'
        ]
        read_only_fields = ['id', 'created_timestamp', 'items', 'total_price', 'user']

    def get_total_price(self, obj):
        return obj.orderitem_set.total_price()