from django.shortcuts import render
from shop.models import Categories
from shop.models import Goods


def index(request):
    categories = Categories.objects.all()
    news = Goods.objects.all()
    return render (request, 'main/index.html',
                   {'news': news})
