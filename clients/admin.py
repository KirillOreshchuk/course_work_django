from django.contrib import admin

from clients.models import Client


@admin.register(Client)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'surname', 'patronymic_name')
    list_filter = ('surname', 'first_name',)
    search_fields = ('email', 'first_name', 'surname',)
