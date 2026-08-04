from django.shortcuts import render
from django.utils.translation import gettext_lazy as _

def custom_404(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_500(request):
    try:
        return render(request, 'errors/500.html', status=500)
    except Exception:
        return render(request, 'errors/500_minimal.html', status=500)

def custom_403(request, exception):
    return render(request, 'errors/403.html', status=403)

def custom_400(request, exception):
    return render(request, 'errors/400.html', status=400)
