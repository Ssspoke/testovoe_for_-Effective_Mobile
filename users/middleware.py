from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from .utils import validate_token_and_session


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """Кастомный middleware для аутентификации через JWT"""

    def process_request(self, request):
        # Пропускаем пути без аутентификации
        if request.path.startswith('/api/auth/register/') or \
           request.path.startswith('/api/auth/login/'):
            return None

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
        
        if status == 'valid':
            request.user = user
            request.auth_token = token
        else:
            # Токен недействителен, но не блокируем запрос - это сделают permission классы
            request.user = None
        
        return None
