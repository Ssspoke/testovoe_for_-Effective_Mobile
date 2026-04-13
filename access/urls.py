from django.urls import path
from .views import (
    list_roles,
    create_role,
    list_elements,
    list_rules,
    create_rule,
    update_rule,
    delete_rule,
    assign_role_to_user,
)

urlpatterns = [
    path('access/roles/', list_roles, name='list_roles'),
    path('access/roles/create/', create_role, name='create_role'),
    path('access/elements/', list_elements, name='list_elements'),
    path('access/rules/', list_rules, name='list_rules'),
    path('access/rules/create/', create_rule, name='create_rule'),
    path('access/rules/<int:rule_id>/update/', update_rule, name='update_rule'),
    path('access/rules/<int:rule_id>/delete/', delete_rule, name='delete_rule'),
    path('access/users/assign-role/', assign_role_to_user, name='assign_role'),
]
