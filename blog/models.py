from django.db import models

from config import settings

NULLABLE = {'blank': True, 'null': True}


class Post(models.Model):
    ACTIVE_CHOICES = ((True, 'Активна'), (False, 'На модерации'))

    title = models.CharField(max_length=100, verbose_name='Заголовок публикации')
    slug = models.CharField(max_length=100, **NULLABLE, verbose_name='Slug')
    description = models.TextField(**NULLABLE, verbose_name='Тело публикации')
    image = models.ImageField(upload_to='blog/', **NULLABLE, verbose_name='Превью')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания публикации')
    is_published = models.BooleanField(default=True, choices=ACTIVE_CHOICES, verbose_name='Статус публикации')
    views_count = models.IntegerField(default=0, verbose_name='Количество просмотров')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE, verbose_name='Владелец')
    is_active = models.BooleanField(default=True, choices=ACTIVE_CHOICES, verbose_name='Статус активности публикации')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'
