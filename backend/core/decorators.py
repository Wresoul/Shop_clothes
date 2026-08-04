from functools import wraps
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages
from .exceptions import APIValidationError, ResourceNotFoundError
import logging
from django.urls import reverse


logger = logging.getLogger(__name__)

def handle_exceptions(redirect_url='main:index'):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                return view_func(request, *args, **kwargs)
            except APIValidationError as e:
                logger.error(f"APIValidationError: {str(e)}")
                if request.path.startswith('/api/'):
                    return JsonResponse({'error': str(e.message)}, status=e.status_code)
                messages.error(request, str(e.message))
                return HttpResponseRedirect(reverse(redirect_url))
            except ResourceNotFoundError as e:
                logger.error(f"ResourceNotFoundError: {str(e)}")
                if request.path.startswith('/api/'):
                    return JsonResponse({'error': str(e.message)}, status=e.status_code)
                messages.error(request, str(e.message))
                return HttpResponseRedirect(reverse(redirect_url))
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                if request.path.startswith('/api/'):
                    return JsonResponse({'error': 'Внутренняя ошибка сервера'}, status=500)
                messages.error(request, "Произошла ошибка. Пожалуйста, попробуйте позже.")
                return HttpResponseRedirect(reverse(redirect_url))
        return wrapper
    return decorator