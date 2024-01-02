from django.db import models

from config import settings

NULLABLE = {'blank': True, 'null': True}


class Client(models.Model):
    """
    Модель клиента
    """
    email = models.EmailField(verbose_name='email')
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    surname = models.CharField(max_length=50, verbose_name='Фамилия')
    patronymic_name = models.CharField(max_length=50, **NULLABLE, verbose_name='Отчество')
    comment = models.TextField(**NULLABLE, default=None, verbose_name='Комментарий')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, **NULLABLE, verbose_name='Владелец')

    def __str__(self):
        if self.patronymic_name is None:
            return f'Client: {self.surname} {self.first_name}, email: {self.email}'
        else:
            return f'Client: {self.surname} {self.first_name} {self.patronymic_name}, email: {self.email}'

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ('surname', 'first_name',)
