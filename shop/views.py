from django.shortcuts import render
from .models import Goods
# Create your views here.
def shop(request):
    news = Goods.objects.all()
    return render(request, 'shop/shop.html', {'news': news})