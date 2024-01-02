from django.urls import path
from django.views.decorators.cache import cache_page

from newsletter.apps import NewsletterConfig
from newsletter.views import (MessageListView, MessageCreateView, MessageUpdateView,
                              MessageDeleteView, MessageDetailView, MailingSettingsListView, MailingSettingsDetailView,
                              MailingSettingsCreateView, MailingSettingsUpdateView, MailingSettingsDeleteView,
                              LogListView, LogDetailView, LogDeleteView, toggle_active)
from newsletter.views import MainPage

app_name = NewsletterConfig.name

urlpatterns = [
    path('', MainPage.as_view(), name='main_page'),

    path('message_list/', MessageListView.as_view(), name='message_list'),
    path('message_create/', MessageCreateView.as_view(), name='message_create'),
    path('message_detail/<int:pk>/', cache_page(60)(MessageDetailView.as_view()), name='message_detail'),
    path('message_update/<int:pk>/', MessageUpdateView.as_view(), name='message_update'),
    path('message_delete/<int:pk>/', MessageDeleteView.as_view(), name='message_delete'),

    path('mailing_settings_list/', MailingSettingsListView.as_view(), name='mailing_settings_list'),
    path('toggle-active/<int:pk>/', toggle_active, name='toggle_active'),
    path('mailing_settings_detail/<int:pk>/', cache_page(60)(MailingSettingsDetailView.as_view()),
         name='mailing_settings_detail'),
    path('mailing_settings_create/', MailingSettingsCreateView.as_view(), name='mailing_settings_create'),
    path('mailing_settings_update/<int:pk>/', MailingSettingsUpdateView.as_view(), name='mailing_settings_update'),
    path('mailing_settings_delete/<int:pk>/', MailingSettingsDeleteView.as_view(), name='mailing_settings_delete'),

    path('logs/', LogListView.as_view(), name='log_list'),
    path('log/<int:pk>/', LogDetailView.as_view(), name='log_detail'),
    path('log_delete/<int:pk>/', LogDeleteView.as_view(), name='log_delete')
]
