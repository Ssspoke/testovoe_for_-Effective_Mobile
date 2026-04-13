from rest_framework import serializers
from .models import Role, BusinessElement, AccessRoleRule, UserRole


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class BusinessElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessElement
        fields = '__all__'


class AccessRoleRuleSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    element_name = serializers.CharField(source='element.name', read_only=True)
    
    class Meta:
        model = AccessRoleRule
        fields = '__all__'


class UserRoleSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    
    class Meta:
        model = UserRole
        fields = '__all__'


class CreateAccessRuleSerializer(serializers.Serializer):
    role_id = serializers.IntegerField()
    element_id = serializers.IntegerField()
    read_permission = serializers.BooleanField(default=False)
    read_all_permission = serializers.BooleanField(default=False)
    create_permission = serializers.BooleanField(default=False)
    update_permission = serializers.BooleanField(default=False)
    update_all_permission = serializers.BooleanField(default=False)
    delete_permission = serializers.BooleanField(default=False)
    delete_all_permission = serializers.BooleanField(default=False)
    
    def validate(self, data):
        # Проверяем существование роли и элемента
        from .models import Role, BusinessElement
        try:
            Role.objects.get(id=data['role_id'])
        except Role.DoesNotExist:
            raise serializers.ValidationError("Роль не найдена")
        
        try:
            BusinessElement.objects.get(id=data['element_id'])
        except BusinessElement.DoesNotExist:
            raise serializers.ValidationError("Бизнес-элемент не найден")
        
        # Проверяем уникальность комбинации role + element
        if AccessRoleRule.objects.filter(
            role_id=data['role_id'],
            element_id=data['element_id']
        ).exists():
            raise serializers.ValidationError("Такое правило уже существует")
        
        return data


class UpdateAccessRuleSerializer(serializers.Serializer):
    read_permission = serializers.BooleanField(required=False)
    read_all_permission = serializers.BooleanField(required=False)
    create_permission = serializers.BooleanField(required=False)
    update_permission = serializers.BooleanField(required=False)
    update_all_permission = serializers.BooleanField(required=False)
    delete_permission = serializers.BooleanField(required=False)
    delete_all_permission = serializers.BooleanField(required=False)
