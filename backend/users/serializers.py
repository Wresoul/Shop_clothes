from rest_framework import serializers
from .models import User
from orders.serializers import OrderSerializer
from carts.serializers import CartSerializer

class UserSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(source='order_set', many=True, read_only=True)
    cart_items = CartSerializer(source='cart_set', many=True, read_only=True)
    total_cart_price = serializers.SerializerMethodField()
    total_cart_quantity = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'phone_number', 'image', 'is_active', 'orders',
            'cart_items', 'total_cart_price', 'total_cart_quantity'
        ]
        read_only_fields = ['id', 'is_active', 'orders', 'cart_items',
                           'total_cart_price', 'total_cart_quantity']

    def get_total_cart_price(self, obj):
        return obj.cart_set.total_price()

    def get_total_cart_quantity(self, obj):
        return obj.cart_set.total_quantity()