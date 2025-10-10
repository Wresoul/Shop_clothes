from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from users.models import User
from core.validators import validate_email_unique, validate_phone_number
from django.core.exceptions import ValidationError
import magic


class UserLoginForm(AuthenticationForm):
    external_token = forms.CharField(max_length=500, required=False, label='Токен внешнего сервиса')
    username = forms.CharField()
    password = forms.CharField()

    class Meta:
        model = User
        fields = ['username', 'password', 'external_token']


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
            "external_token",
        )

    first_name = forms.CharField()
    last_name = forms.CharField()
    username = forms.CharField()
    email = forms.CharField()
    password1 = forms.CharField()
    password2 = forms.CharField()
    external_token = forms.CharField(max_length=500, required=False, label='Токен внешнего сервиса')


class ProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            "image",
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",  # Добавляем phone_number
        )

    image = forms.ImageField(required=False, label='Аватар')
    first_name = forms.CharField(label='Имя')
    last_name = forms.CharField(label='Фамилия')
    username = forms.CharField(label='Имя пользователя')
    email = forms.EmailField(label='Email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and self.instance.email != email:  # Проверяем, если email изменился
            validate_email_unique(email)
        return email


    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name.strip():
            raise ValidationError("Имя не может быть пустым.")
        if len(first_name) < 2:
            raise ValidationError("Имя должно содержать минимум 2 символа.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name.strip():
            raise ValidationError("Фамилия не может быть пустой.")
        if len(last_name) < 2:
            raise ValidationError("Фамилия должна содержать минимум 2 символа.")
        return last_name

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Проверка размера файла (например, не больше 5MB)
            max_size = 5 * 1024 * 1024  # 5MB
            if image.size > max_size:
                raise ValidationError("Размер изображения не должен превышать 5MB.")

            # Проверка типа файла
            mime = magic.Magic(mime=True)
            file_type = mime.from_buffer(image.read(1024))
            valid_types = ['image/jpeg', 'image/png', 'image/gif']
            if file_type not in valid_types:
                raise ValidationError("Поддерживаются только изображения в формате JPEG, PNG или GIF.")
            image.seek(0)  # Возвращаем указатель в начало файла
        return image
