from django.contrib import admin

from newsletter.models import MailingSettings, Message, MailingLog


@admin.register(Message)
class MessageListSettingsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title',)
    list_filter = ('title',)
    search_fields = ('title', 'text',)


@admin.register(MailingSettings)
class MailingListSettingsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'start_time', 'end_time', 'next_newsletter', 'periodicity', 'status', 'is_active',)
    list_filter = ('next_newsletter', 'periodicity', 'status',)
    search_fields = ('start_time', 'periodicity', 'end_time',)


@admin.register(MailingLog)
class LogAdmin(admin.ModelAdmin):
    list_display = ('pk', 'mailing', 'time', 'status', 'server_response',)
    list_filter = ('time', 'status',)
    search_fields = ('mailing', 'time', 'status',)
