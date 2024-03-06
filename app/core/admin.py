from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from core.models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'registration_method')

admin.site.register(User, CustomUserAdmin)