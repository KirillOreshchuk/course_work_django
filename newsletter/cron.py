import calendar
from datetime import timedelta, datetime
from smtplib import SMTPException

from django.core.mail import send_mail
from django.db.models import QuerySet
from django.utils import timezone

from config import settings
from newsletter.models import MailingSettings, MailingLog


def my_scheduled_job():
    # Получаем все активные настройки рассылки
    active_mailings: QuerySet = MailingSettings.objects.filter(is_active=True)
    current_time = timezone.localtime(timezone.now())
    now: str = current_time.strftime('%Y-%m-%d %H:%M')
    for mailing in active_mailings:
        # Проверяем, находится ли время рассылки в заданном интервале
        if mailing.start_time >= current_time:
            mailing.status = "Создана"
            mailing.save()
        elif mailing.end_time <= current_time:
            mailing.status = "Завершена"
            mailing.save()
        elif mailing.start_time.strftime('%Y-%m-%d %H:%M') <= now <= mailing.end_time.strftime('%Y-%m-%d %H:%M'):
            mailing.status = "Запущена"
            mailing.save()
            # Определяем периодичность рассылки
            next_send_str: str = mailing.next_send.strftime('%Y-%m-%d %H:%M')
            if next_send_str <= now:
                if mailing.periodicity == "Раз в день":
                    mailing.next_send = current_time + timedelta(days=1)
                    mailing.save()
                elif mailing.periodicity == "Раз в неделю":
                    mailing.next_send = current_time + timedelta(days=7)
                    mailing.save()
                elif mailing.periodicity == "Раз в месяц":
                    today = datetime.today()
                    days = calendar.monthrange(today.year, today.month)[1]
                    mailing.next_send = current_time + timedelta(days=days)
                    mailing.save()
                if mailing.next_send > mailing.end_time:
                    mailing.status = "Завершена"
                    mailing.save()

                status = True
                error_message = ''
                try:
                    send_mail(
                        subject=mailing.message.title,
                        message=mailing.message.text,
                        from_email=settings.EMAIL_HOST_USER,
                        recipient_list=[client.email for client in mailing.clients.all()],
                        fail_silently=False
                    )
                    status = True
                    error_message = 'OK'
                except SMTPException as error:
                    status = False
                    if 'authentication failed' in str(error):
                        error_message = 'Ошибка аутентификации в почтовом сервисе'
                    elif 'suspicion of SPAM' in str(error):
                        error_message = 'Слишком много рассылок, сервис отклонил письмо'
                    else:
                        error_message = error
                finally:
                    log = MailingLog.objects.create(
                        status=status,
                        server_response=error_message,
                        mailing=mailing,
                        owner=mailing.owner
                    )
                    log.save()
            elif mailing.next_send >= mailing.end_time:
                mailing.status = "Завершена"
                mailing.save()
