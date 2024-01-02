# Generated by Django 5.0 on 2023-12-31 04:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Заголовок cообщения')),
                ('text', models.TextField(verbose_name='Тело сообщения')),
            ],
            options={
                'verbose_name': 'Сообщение',
                'verbose_name_plural': 'Сообщения',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='MailingSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(verbose_name='Дата начала рассылки')),
                ('end_time', models.DateTimeField(verbose_name='Дата окончания рассылки')),
                ('next_newsletter', models.DateTimeField(blank=True, null=True, verbose_name='Дата следующей рассылки')),
                ('periodicity', models.CharField(choices=[('Раз в день', 'Раз в день'), ('Раз в неделю', 'Раз в неделю'), ('Раз в месяц', 'Раз в месяц')], max_length=50, verbose_name='Периодичность')),
                ('status', models.CharField(choices=[('Завершена', 'Завершена'), ('Создана', 'Создана'), ('Запущена', 'Запущена')], default='Создана', max_length=50, verbose_name='Статус рассылки')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('is_active', models.BooleanField(choices=[(True, 'Активна'), (False, 'На модерации')], default=True, verbose_name='Активна')),
                ('clients', models.ManyToManyField(to='clients.client', verbose_name='Клиенты рассылки')),
                ('message', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='newsletter.message', verbose_name='Сообщение')),
            ],
            options={
                'verbose_name': 'Настройки рассылки',
                'verbose_name_plural': 'Настройки рассылки',
                'ordering': ('created_at',),
            },
        ),
        migrations.CreateModel(
            name='MailingLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания лога')),
                ('status', models.BooleanField(verbose_name='Статус попытки')),
                ('server_response', models.CharField(blank=True, null=True, verbose_name='Ответ от сервера')),
                ('mailing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newsletter.mailingsettings', verbose_name='Рассылка')),
            ],
            options={
                'verbose_name': 'Лог рассылки',
                'verbose_name_plural': 'Логи рассылки',
                'ordering': ('time',),
            },
        ),
    ]