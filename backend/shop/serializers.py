from rest_framework import serializers
from .models import Categories, Goods

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ['id', 'name', 'slug']

class GoodsSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    sell_price = serializers.SerializerMethodField()

    class Meta:
        model = Goods
        fields = ['id', 'name', 'slug', 'photo', 'rating', 'discount', 'price', 'quantity', 'category', 'sell_price']

    def get_sell_price(self, obj):
        return obj.sell_price()