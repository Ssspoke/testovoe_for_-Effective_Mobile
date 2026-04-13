import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import authenticate
from .models import CustomUser, Session


def generate_jwt_token(user):
    """Генерирует JWT-токен для пользователя"""
    payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES),
        'iat': datetime.utcnow(),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def decode_jwt_token(token):
    """Декодирует JWT-токен и возвращает payload"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user_from_token(token):
    """Получает пользователя из JWT-токена"""
    payload = decode_jwt_token(token)
    if not payload:
        return None
    
    try:
        user = CustomUser.objects.get(id=payload['user_id'], is_active=True)
        return user
    except CustomUser.DoesNotExist:
        return None


def create_session(user, token):
    """Создаёт сессию для пользователя"""
    expires_at = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    session = Session.objects.create(
        user=user,
        token=token,
        expires_at=expires_at,
        is_active=True,
    )
    return session


def deactivate_session(token):
    """Деактивирует сессию (logout)"""
    try:
        session = Session.objects.get(token=token, is_active=True)
        session.is_active = False
        session.save()
        return True
    except Session.DoesNotExist:
        return False


def validate_token_and_session(token):
    """Проверяет токен и сессию"""
    payload = decode_jwt_token(token)
    if not payload:
        return None, 'invalid_token'
    
    try:
        session = Session.objects.get(token=token, is_active=True)
        if session.is_expired():
            session.is_active = False
            session.save()
            return None, 'expired'
        
        user = session.user
        if not user.is_active:
            return None, 'user_inactive'
        
        return user, 'valid'
    except Session.DoesNotExist:
        return None, 'no_session'
