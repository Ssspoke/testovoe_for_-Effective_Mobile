from django.contrib import admin
from .models import Role, BusinessElement, AccessRoleRule, UserRole


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(BusinessElement)
class BusinessElementAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(AccessRoleRule)
class AccessRoleRuleAdmin(admin.ModelAdmin):
    list_display = ('role', 'element', 'read_permission', 'create_permission', 'update_permission', 'delete_permission')
    list_filter = ('role', 'element')
    search_fields = ('role__name', 'element__name')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'assigned_at')
    list_filter = ('role',)
    search_fields = ('user__email', 'role__name')
