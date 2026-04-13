from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from access.models import AccessRoleRule, UserRole


def check_permission(user, element_name, permission_field):
    """
    Проверяет право доступа пользователя к бизнес-элементу.
    
    Args:
        user: Пользователь
        element_name: Название бизнес-элемента
        permission_field: Поле права доступа (например, 'read_permission')
    
    Returns:
        bool: Имеет ли пользователь право
    """
    if not user or not user.is_active:
        return False
    
    # Получаем роли пользователя
    user_roles = UserRole.objects.filter(user=user).values_list('role_id', flat=True)
    
    if not user_roles:
        return False
    
    # Проверяем правила для каждой роли
    rules = AccessRoleRule.objects.filter(
        role_id__in=user_roles,
        element__name=element_name
    )
    
    for rule in rules:
        if getattr(rule, permission_field, False):
            return True
    
    return False


def get_permission_level(user, element_name, base_permission, all_permission):
    """
    Определяет уровень доступа пользователя.
    
    Returns:
        str: 'all' - доступ ко всем, 'own' - доступ только к своим, 'none' - нет доступа
    """
    if check_permission(user, element_name, all_permission):
        return 'all'
    elif check_permission(user, element_name, base_permission):
        return 'own'
    return 'none'


class HasReadPermission(permissions.BasePermission):
    """Проверка права на чтение"""
    element_name = None
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_active:
            return False
        
        if request.user.is_superuser:
            return True
        
        element = self.element_name or getattr(view, 'element_name', None)
        if not element:
            return False
        
        permission_level = get_permission_level(
            request.user, element, 'read_permission', 'read_all_permission'
        )
        
        if permission_level == 'none':
            raise PermissionDenied('Нет прав на чтение этого ресурса')
        
        return True


class HasCreatePermission(permissions.BasePermission):
    """Проверка права на создание"""
    element_name = None
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_active:
            return False
        
        if request.user.is_superuser:
            return True
        
        element = self.element_name or getattr(view, 'element_name', None)
        if not element:
            return False
        
        if not check_permission(request.user, element, 'create_permission'):
            raise PermissionDenied('Нет прав на создание этого ресурса')
        
        return True


class HasUpdatePermission(permissions.BasePermission):
    """Проверка права на обновление"""
    element_name = None
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_active:
            return False
        
        if request.user.is_superuser:
            return True
        
        element = self.element_name or getattr(view, 'element_name', None)
        if not element:
            return False
        
        permission_level = get_permission_level(
            request.user, element, 'update_permission', 'update_all_permission'
        )
        
        if permission_level == 'none':
            raise PermissionDenied('Нет прав на обновление этого ресурса')
        
        return True
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        element = self.element_name or getattr(view, 'element_name', None)
        permission_level = get_permission_level(
            request.user, element, 'update_permission', 'update_all_permission'
        )
        
        if permission_level == 'all':
            return True
        
        # Проверяем, является ли пользователь владельцем объекта
        if hasattr(obj, 'owner') and obj.owner == request.user:
            return permission_level == 'own'
        
        return False


class HasDeletePermission(permissions.BasePermission):
    """Проверка права на удаление"""
    element_name = None
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_active:
            return False
        
        if request.user.is_superuser:
            return True
        
        element = self.element_name or getattr(view, 'element_name', None)
        if not element:
            return False
        
        permission_level = get_permission_level(
            request.user, element, 'delete_permission', 'delete_all_permission'
        )
        
        if permission_level == 'none':
            raise PermissionDenied('Нет прав на удаление этого ресурса')
        
        return True
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        
        element = self.element_name or getattr(view, 'element_name', None)
        permission_level = get_permission_level(
            request.user, element, 'delete_permission', 'delete_all_permission'
        )
        
        if permission_level == 'all':
            return True
        
        # Проверяем, является ли пользователь владельцем объекта
        if hasattr(obj, 'owner') and obj.owner == request.user:
            return permission_level == 'own'
        
        return False


class IsAdminUser(permissions.BasePermission):
    """Проверка, что пользователь является администратором"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_active:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Проверяем наличие роли admin
        user_roles = UserRole.objects.filter(
            user=request.user,
            role__name='admin'
        ).exists()
        
        if not user_roles:
            raise PermissionDenied('Требуются права администратора')
        
        return True
