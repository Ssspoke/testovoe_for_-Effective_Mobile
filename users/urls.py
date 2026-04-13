from django.urls import path
from .views import register, login, logout, get_profile, update_profile, delete_account

urlpatterns = [
    path('auth/register/', register, name='register'),
    path('auth/login/', login, name='login'),
    path('auth/logout/', logout, name='logout'),
    path('auth/me/', get_profile, name='get_profile'),
    path('auth/me/update/', update_profile, name='update_profile'),
    path('auth/me/delete/', delete_account, name='delete_account'),
]
