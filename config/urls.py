"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def home(request):
    """Welcome page с описанием доступных API endpoints"""
    return JsonResponse({
        'message': 'Система аутентификации и авторизации',
        'documentation': 'См. README.md',
        'endpoints': {
            'auth': {
                'POST /api/auth/register/': 'Регистрация',
                'POST /api/auth/login/': 'Вход (получение токена)',
                'POST /api/auth/logout/': 'Выход',
                'GET /api/auth/me/': 'Профиль',
                'PUT /api/auth/me/update/': 'Обновить профиль',
                'DELETE /api/auth/me/delete/': 'Удалить аккаунт',
            },
            'access (admin only)': {
                'GET /api/access/roles/': 'Список ролей',
                'POST /api/access/roles/create/': 'Создать роль',
                'GET /api/access/elements/': 'Список бизнес-элементов',
                'GET /api/access/rules/': 'Список правил доступа',
                'POST /api/access/rules/create/': 'Создать правило',
                'PUT /api/access/rules/<id>/update/': 'Обновить правило',
                'DELETE /api/access/rules/<id>/delete/': 'Удалить правило',
            },
            'business': {
                'GET /api/products/': 'Список продуктов',
                'POST /api/products/create/': 'Создать продукт',
                'GET /api/orders/': 'Список заказов',
                'POST /api/orders/create/': 'Создать заказ',
            },
            'admin_panel': '/admin/',
        },
        'test_users': {
            'admin': 'admin@test.com / admin123',
            'manager': 'manager@test.com / manager123',
            'user': 'user@test.com / user123',
            'guest': 'guest@test.com / guest123',
        }
    }, json_dumps_params={'ensure_ascii': False, 'indent': 2})


urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('access.urls')),
    path('api/', include('business.urls')),
]
