from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Role, BusinessElement, AccessRoleRule, UserRole
from .serializers import (
    RoleSerializer, 
    BusinessElementSerializer, 
    AccessRoleRuleSerializer,
    UserRoleSerializer,
    CreateAccessRuleSerializer,
    UpdateAccessRuleSerializer,
)
from .permissions import IsAdminUser


@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_roles(request):
    """Получение списка всех ролей (только для админа)"""
    roles = Role.objects.all()
    serializer = RoleSerializer(roles, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_role(request):
    """Создание новой роли (только для админа)"""
    serializer = RoleSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_elements(request):
    """Получение списка всех бизнес-элементов (только для админа)"""
    elements = BusinessElement.objects.all()
    serializer = BusinessElementSerializer(elements, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_rules(request):
    """Получение списка всех правил доступа (только для админа)"""
    rules = AccessRoleRule.objects.select_related('role', 'element').all()
    serializer = AccessRoleRuleSerializer(rules, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_rule(request):
    """Создание правила доступа (только для админа)"""
    serializer = CreateAccessRuleSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    rule = AccessRoleRule.objects.create(
        role_id=serializer.validated_data['role_id'],
        element_id=serializer.validated_data['element_id'],
        read_permission=serializer.validated_data.get('read_permission', False),
        read_all_permission=serializer.validated_data.get('read_all_permission', False),
        create_permission=serializer.validated_data.get('create_permission', False),
        update_permission=serializer.validated_data.get('update_permission', False),
        update_all_permission=serializer.validated_data.get('update_all_permission', False),
        delete_permission=serializer.validated_data.get('delete_permission', False),
        delete_all_permission=serializer.validated_data.get('delete_all_permission', False),
    )
    
    rule_serializer = AccessRoleRuleSerializer(rule)
    return Response(rule_serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdminUser])
def update_rule(request, rule_id):
    """Обновление правила доступа (только для админа)"""
    try:
        rule = AccessRoleRule.objects.get(id=rule_id)
    except AccessRoleRule.DoesNotExist:
        return Response({
            'error': 'Правило не найдено'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UpdateAccessRuleSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Обновляем поля
    for field, value in serializer.validated_data.items():
        setattr(rule, field, value)
    
    rule.save()
    
    rule_serializer = AccessRoleRuleSerializer(rule)
    return Response(rule_serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_rule(request, rule_id):
    """Удаление правила доступа (только для админа)"""
    try:
        rule = AccessRoleRule.objects.get(id=rule_id)
        rule.delete()
        return Response({
            'message': 'Правило успешно удалено'
        }, status=status.HTTP_200_OK)
    except AccessRoleRule.DoesNotExist:
        return Response({
            'error': 'Правило не найдено'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def assign_role_to_user(request):
    """Назначение роли пользователю (только для админа)"""
    user_id = request.data.get('user_id')
    role_id = request.data.get('role_id')
    
    if not user_id or not role_id:
        return Response({
            'error': 'Необходимо указать user_id и role_id'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    from users.models import CustomUser
    
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({
            'error': 'Пользователь не найден'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        role = Role.objects.get(id=role_id)
    except Role.DoesNotExist:
        return Response({
            'error': 'Роль не найдена'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Проверяем, не назначена ли уже эта роль
    if UserRole.objects.filter(user=user, role=role).exists():
        return Response({
            'error': 'Эта роль уже назначена пользователю'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    UserRole.objects.create(user=user, role=role)
    
    return Response({
        'message': 'Роль успешно назначена',
        'user': user.email,
        'role': role.name
    }, status=status.HTTP_201_CREATED)
