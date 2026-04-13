from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .models import CustomUser
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer, UpdateUserSerializer
from .utils import generate_jwt_token, create_session, deactivate_session, validate_token_and_session
import bcrypt


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Регистрация нового пользователя"""
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Хешируем пароль через bcrypt
    password_hash = bcrypt.hashpw(
        serializer.validated_data['password'].encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')
    
    # Создаём пользователя
    user = CustomUser.objects.create_user(
        email=serializer.validated_data['email'],
        password=serializer.validated_data['password'],
        first_name=serializer.validated_data.get('first_name', ''),
        last_name=serializer.validated_data.get('last_name', ''),
        middle_name=serializer.validated_data.get('middle_name', ''),
    )
    
    # Назначаем роль по умолчанию (user)
    from access.models import Role, UserRole
    try:
        default_role = Role.objects.get(name='user')
        UserRole.objects.create(user=user, role=default_role)
    except Role.DoesNotExist:
        pass
    
    return Response({
        'message': 'Пользователь успешно зарегистрирован',
        'user_id': user.id,
        'email': user.email,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Вход пользователя (генерация JWT-токена)"""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # Находим пользователя по email
    try:
        user = CustomUser.objects.get(email=serializer.validated_data['email'])
    except CustomUser.DoesNotExist:
        return Response({
            'error': 'Неверный email или пароль'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Проверяем активность
    if not user.is_active:
        return Response({
            'error': 'Аккаунт неактивен или удален'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Проверяем пароль (bcrypt)
    try:
        password_valid = bcrypt.checkpw(
            serializer.validated_data['password'].encode('utf-8'),
            user.password.encode('utf-8')
        )
    except:
        return Response({
            'error': 'Неверный email или пароль'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    if not password_valid:
        return Response({
            'error': 'Неверный email или пароль'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Генерируем JWT-токен
    token = generate_jwt_token(user)
    
    # Создаём сессию
    create_session(user, token)
    
    return Response({
        'message': 'Успешный вход',
        'token': token,
        'user': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """Выход пользователя (деактивация сессии)"""
    token = request.auth
    if token:
        deactivate_session(token)
    
    return Response({
        'message': 'Успешный выход'
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    """Получение профиля текущего пользователя"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Обновление профиля текущего пользователя"""
    serializer = UpdateUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user = request.user
    user.first_name = serializer.validated_data.get('first_name', user.first_name)
    user.last_name = serializer.validated_data.get('last_name', user.last_name)
    user.middle_name = serializer.validated_data.get('middle_name', user.middle_name)
    user.save()
    
    return Response({
        'message': 'Профиль успешно обновлен',
        'user': UserSerializer(user).data
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    """Мягкое удаление аккаунта"""
    user = request.user
    user.soft_delete()
    
    # Деактивируем сессию
    token = request.auth
    if token:
        deactivate_session(token)
    
    return Response({
        'message': 'Аккаунт успешно удален'
    }, status=status.HTTP_200_OK)
