from django.db import models


class Role(models.Model):
    """Модель роли пользователя"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'roles'
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return self.name


class BusinessElement(models.Model):
    """Модель бизнес-элемента, к которому осуществляется доступ"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'business_elements'
        verbose_name = 'Бизнес-элемент'
        verbose_name_plural = 'Бизнес-элементы'

    def __str__(self):
        return self.name


class AccessRoleRule(models.Model):
    """Модель правил доступа ролей к бизнес-элементам"""
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='access_rules')
    element = models.ForeignKey(BusinessElement, on_delete=models.CASCADE, related_name='access_rules')
    
    # Права на чтение
    read_permission = models.BooleanField(default=False, help_text='Может ли роль читать элементы')
    read_all_permission = models.BooleanField(default=False, help_text='Может ли роль читать все элементы (включая чужие)')
    
    # Права на создание
    create_permission = models.BooleanField(default=False, help_text='Может ли роль создавать элементы')
    
    # Права на обновление
    update_permission = models.BooleanField(default=False, help_text='Может ли роль обновлять свои элементы')
    update_all_permission = models.BooleanField(default=False, help_text='Может ли роль обновлять все элементы')
    
    # Права на удаление
    delete_permission = models.BooleanField(default=False, help_text='Может ли роль удалять свои элементы')
    delete_all_permission = models.BooleanField(default=False, help_text='Может ли роль удалять все элементы')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'access_role_rules'
        unique_together = ('role', 'element')
        verbose_name = 'Правило доступа'
        verbose_name_plural = 'Правила доступа'

    def __str__(self):
        return f'{self.role.name} -> {self.element.name}'


class UserRole(models.Model):
    """Связь пользователя с ролями"""
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_roles'
        unique_together = ('user', 'role')
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователей'

    def __str__(self):
        return f'{self.user.email} - {self.role.name}'
