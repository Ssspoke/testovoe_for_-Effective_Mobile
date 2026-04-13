from django.contrib import admin
from .models import CustomUser, Session


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'created_at')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'expires_at', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('user__email',)
