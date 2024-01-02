from django.contrib import admin
from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('last_login', 'first_name', 'last_name', 'country', 'is_active')
