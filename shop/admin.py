from django.contrib import admin
from shop.models import Goods
from shop.models import Categories

@admin.register(Goods)
class GoodsAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

