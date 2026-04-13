from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .utils import validate_token_and_session


class JWTAuthentication(BaseAuthentication):
    """Кастомный класс аутентификации для DRF"""
    
    def authenticate(self, request):
        # Получаем токен из заголовка Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            return None
        
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split('Bearer ')[-1].strip()
        
        if not token:
            return None
        
        # Проверяем токен и сессию
        user, status = validate_token_and_session(token)
        
        if status == 'invalid_token':
            raise AuthenticationFailed('Неверный токен')
        elif status == 'expired':
            raise AuthenticationFailed('Токен истек')
        elif status == 'user_inactive':
            raise AuthenticationFailed('Пользователь неактивен')
        elif status == 'no_session':
            raise AuthenticationFailed('Сессия не найдена')
        
        # Возвращаем (user, auth) кортеж
        return (user, token)
    
    def authenticate_header(self, request):
        return 'Bearer'
