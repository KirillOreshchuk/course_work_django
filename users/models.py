from django.contrib.auth.models import AbstractUser
from django.db import models

NULLABLE = {'blank': True, 'null': True}


class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True, verbose_name='Почта')

    phone = models.CharField(max_length=20,  **NULLABLE, verbose_name='Телефон')
    avatar = models.ImageField(upload_to='users/',  **NULLABLE, verbose_name='Аватар')
    country = models.CharField(max_length=50,  **NULLABLE, verbose_name='Страна')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
