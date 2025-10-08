from celery import shared_task
from django.core.files.base import ContentFile
from PIL import Image
import io
from .models import User
import os
import requests
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from social_django.models import UserSocialAuth


User = get_user_model()


@shared_task
def process_user_image(user_id, image_name):
    try:
        user = User.objects.get(id=user_id)
        if user.image:
            # Открываем изображение
            image_path = user.image.path
            with Image.open(image_path) as img:
                # Пример обработки: сжимаем изображение до ширины 300px
                img.thumbnail((300, 300))

                # Сохраняем обработанное изображение
                buffer = io.BytesIO()
                img.save(buffer, format=img.format or 'JPEG', quality=85)
                file_name = os.path.basename(image_name)
                user.image.save(f"processed_{file_name}", ContentFile(buffer.getvalue()), save=True)

        return f"Image processed for user {user_id}"
    except Exception as e:
        return f"Error processing image for user {user_id}: {str(e)}"


@shared_task
def verify_external_auth(user_id, access_token):
    """
    Проверяет аутентификацию через Google OAuth и отправляет email при успехе.
    """
    try:
        # Находим пользователя по user_id или создаем нового
        user = User.objects.get(id=user_id) if user_id else None
        if not user:
            return {'status': 'error', 'message': 'Пользователь не найден'}

        # Проверяем токен через social-auth
        social_auth = UserSocialAuth.objects.filter(user=user, provider='google-oauth2').first()
        if social_auth and social_auth.extra_data.get('access_token') == access_token:
            user.is_external_authenticated = True
            user.external_token = access_token
            user.save()

            # Отправляем email
            send_verification_email.delay(user.id, user.email)

            return {
                'status': 'success',
                'user_id': user.id,
                'message': 'Аутентификация через Google подтверждена, письмо отправлено',
                'created': False
            }
        else:
            return {
                'status': 'error',
                'message': 'Неверный токен или пользователь не связан с Google OAuth'
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Неожиданная ошибка: {str(e)}'
        }


@shared_task
def send_verification_email(user_id, email):
    """
    Отправляет email-уведомление о успешной аутентификации.
    """
    try:
        user = User.objects.get(id=user_id)
        subject = 'Добро пожаловать в Ksysha One Love!'
        message = (
            f'Здравствуйте, {user.username}!\n\n'
            'Ваша аутентификация через Google успешно подтверждена.\n'
            'Теперь вы можете пользоваться всеми функциями нашего сайта.\n\n'
            'С уважением,\nКоманда Ksysha One Love'
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return {'status': 'success', 'message': f'Письмо отправлено на {email}'}
    except User.DoesNotExist:
        return {'status': 'error', 'message': f'Пользователь {user_id} не найден'}
    except Exception as e:
        return {'status': 'error', 'message': f'Ошибка отправки письма: {str(e)}'}