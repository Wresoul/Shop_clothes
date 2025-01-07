from django.shortcuts import render
from shop.models import Goods
# Create your views here.
def login(request):
    news = Goods.objects.all()
    return render(request,'users/login.html', {'news': news})