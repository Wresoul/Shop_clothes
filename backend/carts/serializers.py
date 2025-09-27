from rest_framework import serializers
from .models import Cart
from shop.models import Goods

class CartSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source='product.name', read_only=True)
    products_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'product', 'quantity', 'created_timestamp', 'products_price']
        read_only_fields = ['id', 'created_timestamp', 'products_price']

    def get_products_price(self, obj):
        return obj.products_price()