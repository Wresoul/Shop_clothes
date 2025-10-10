from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from users.models import User
import re

def validate_positive_number(value):
    if value <= 0:
        raise ValidationError(_("Число должно быть положительным."))

def validate_email_unique(email):
    if User.objects.filter(email=email).exists():
        raise ValidationError(_("Этот email уже занят."))

def validate_phone_number(phone):
    pattern = r'^\+7\d{10}$'
    if not re.match(pattern, phone):
        raise ValidationError(_("Номер телефона должен быть в формате +7XXXXXXXXXX."))