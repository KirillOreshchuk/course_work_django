# course_work_django

1. Создать файл '.env', добавить в него:

- DB_HOST=localhost  #  Хост базы данных
- DB_USER=postgres  # Пользователь базы данных
- DB_PASSWORD=12345  # Пароль пользователя от базы данных
- DB_NAME='distribution'  # Название базы данных
- DB_ENGINE='django.db.backends.postgresql_psycopg2'  # Подключение  к базе данных
- EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
- EMAIL_HOST='smtp.yandex.ru'  # Хост яндекс почты
- EMAIL_PORT=465  # Порт для яндекс почты
- EMAIL_HOST_USER='your_email@yandex.ru' # email яндекс почты
- EMAIL_HOST_PASSWORD='your_yandex_smtp_password' # пароль яндекс почты
- CACHE_LOCATION=redis://127.0.0.1:6379
- CACHE_BACKEND=django.core.cache.backends.redis.RedisCache

2. Запустить файл `users/management/commands/csu.py` командой: `python manage.py csu` создать суперпользователя с паролем '12345'.

3. Запустить крон в ручную командой `python manage.py crontab add`.

4. Запустить Рассылку командой `python manage.py cron_newsletter`.
