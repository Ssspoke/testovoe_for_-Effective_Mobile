"""
Management command для заполнения БД тестовыми данными.
Запуск: python manage.py seed_db
"""

import bcrypt
from django.core.management.base import BaseCommand
from users.models import CustomUser
from access.models import Role, BusinessElement, AccessRoleRule, UserRole
from business.models import MockProduct


class Command(BaseCommand):
    help = 'Заполняет БД тестовыми данными'

    def handle(self, *args, **kwargs):
        self.stdout.write('Начало заполнения БД тестовыми данными...')
        
        # Создаём роли
        self.stdout.write('Создание ролей...')
        roles_data = [
            {'name': 'admin', 'description': 'Администратор с полным доступом'},
            {'name': 'manager', 'description': 'Менеджер с управлением продуктами и заказами'},
            {'name': 'user', 'description': 'Обычный пользователь'},
            {'name': 'guest', 'description': 'Гость с минимальным доступом'},
        ]
        
        roles = {}
        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )
            roles[role_data['name']] = role
            status = 'создана' if created else 'уже существует'
            self.stdout.write(f'  Роль "{role.name}" {status}')
        
        # Создаём бизнес-элементы
        self.stdout.write('\nСоздание бизнес-элементов...')
        elements_data = [
            {'name': 'users', 'description': 'Пользователи системы'},
            {'name': 'products', 'description': 'Продукты/товары'},
            {'name': 'orders', 'description': 'Заказы'},
            {'name': 'access_rules', 'description': 'Правила доступа'},
        ]
        
        elements = {}
        for elem_data in elements_data:
            elem, created = BusinessElement.objects.get_or_create(
                name=elem_data['name'],
                defaults={'description': elem_data['description']}
            )
            elements[elem_data['name']] = elem
            status = 'создан' if created else 'уже существует'
            self.stdout.write(f'  Элемент "{elem.name}" {status}')
        
        # Создаём правила доступа
        self.stdout.write('\nСоздание правил доступа...')
        
        rules_data = [
            # admin - полный доступ ко всему
            {'role': 'admin', 'element': 'users', 'all_perms': True},
            {'role': 'admin', 'element': 'products', 'all_perms': True},
            {'role': 'admin', 'element': 'orders', 'all_perms': True},
            {'role': 'admin', 'element': 'access_rules', 'all_perms': True},
            
            # manager - управление продуктами и заказами
            {'role': 'manager', 'element': 'products', 
             'read': True, 'read_all': True, 'create': True, 
             'update': True, 'update_all': True, 'delete': True, 'delete_all': False},
            {'role': 'manager', 'element': 'orders', 
             'read': True, 'read_all': True, 'create': True, 
             'update': True, 'update_all': True, 'delete': False, 'delete_all': False},
            {'role': 'manager', 'element': 'users', 'read': True, 'read_all': False},
            
            # user - базовый доступ
            {'role': 'user', 'element': 'products', 'read': True, 'read_all': True},
            {'role': 'user', 'element': 'orders', 
             'read': True, 'read_all': False, 'create': True, 
             'update': True, 'update_all': False, 'delete': True, 'delete_all': False},
            
            # guest - только чтение продуктов
            {'role': 'guest', 'element': 'products', 'read': True, 'read_all': False},
        ]
        
        for rule_data in rules_data:
            role = roles[rule_data['role']]
            element = elements[rule_data['element']]
            
            rule, created = AccessRoleRule.objects.get_or_create(
                role=role,
                element=element,
                defaults={
                    'read_permission': rule_data.get('read', rule_data.get('all_perms', False)),
                    'read_all_permission': rule_data.get('read_all', rule_data.get('all_perms', False)),
                    'create_permission': rule_data.get('create', rule_data.get('all_perms', False)),
                    'update_permission': rule_data.get('update', rule_data.get('all_perms', False)),
                    'update_all_permission': rule_data.get('update_all', rule_data.get('all_perms', False)),
                    'delete_permission': rule_data.get('delete', rule_data.get('all_perms', False)),
                    'delete_all_permission': rule_data.get('delete_all', rule_data.get('all_perms', False)),
                }
            )
            status = 'создано' if created else 'уже существует'
            self.stdout.write(f'  Правило "{role.name} -> {element.name}" {status}')
        
        # Создаём тестовых пользователей
        self.stdout.write('\nСоздание тестовых пользователей...')
        
        users_data = [
            {
                'email': 'admin@test.com',
                'first_name': 'Admin',
                'last_name': 'Adminov',
                'middle_name': 'Adminovich',
                'password': 'admin123',
                'role': 'admin',
                'is_superuser': True,
                'is_staff': True,
            },
            {
                'email': 'manager@test.com',
                'first_name': 'Manager',
                'last_name': 'Managerov',
                'middle_name': 'Managerovich',
                'password': 'manager123',
                'role': 'manager',
            },
            {
                'email': 'user@test.com',
                'first_name': 'User',
                'last_name': 'Userov',
                'middle_name': 'Userovich',
                'password': 'user123',
                'role': 'user',
            },
            {
                'email': 'guest@test.com',
                'first_name': 'Guest',
                'last_name': 'Guestov',
                'middle_name': '',
                'password': 'guest123',
                'role': 'guest',
            },
        ]
        
        test_users = {}
        for user_data in users_data:
            user, created = CustomUser.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'middle_name': user_data.get('middle_name', ''),
                    'is_superuser': user_data.get('is_superuser', False),
                    'is_staff': user_data.get('is_staff', False),
                }
            )
            
            if created:
                # Устанавливаем пароль через bcrypt
                password_hash = bcrypt.hashpw(
                    user_data['password'].encode('utf-8'),
                    bcrypt.gensalt()
                ).decode('utf-8')
                user.password = password_hash
                user.save()
                status = 'создан'
            else:
                status = 'уже существует'
            
            self.stdout.write(f'  Пользователь "{user.email}" {status}')
            
            test_users[user_data['role']] = user
            
            # Назначаем роль
            role = roles[user_data['role']]
            UserRole.objects.get_or_create(user=user, role=role)
        
        # Создаём тестовые продукты
        self.stdout.write('\nСоздание тестовых продуктов...')
        
        products_data = [
            {'name': 'Laptop', 'description': 'Gaming laptop', 'price': '89999.99', 'owner': 'manager'},
            {'name': 'Smartphone', 'description': 'Flagship smartphone', 'price': '59999.99', 'owner': 'manager'},
            {'name': 'Headphones', 'description': 'Wireless headphones', 'price': '12999.99', 'owner': 'manager'},
            {'name': 'Monitor', 'description': '4K monitor', 'price': '35999.99', 'owner': 'user'},
            {'name': 'Keyboard', 'description': 'Mechanical keyboard', 'price': '8999.99', 'owner': 'user'},
        ]
        
        for prod_data in products_data:
            owner = test_users[prod_data['owner']]
            product, created = MockProduct.objects.get_or_create(
                name=prod_data['name'],
                defaults={
                    'description': prod_data['description'],
                    'price': prod_data['price'],
                    'owner': owner,
                }
            )
            status = 'создан' if created else 'уже существует'
            self.stdout.write(f'  Продукт "{product.name}" {status}')
        
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write('Заполнение БД завершено!')
        self.stdout.write('=' * 50)
        self.stdout.write('\nТестовые учетные данные:')
        self.stdout.write('  Admin:   admin@test.com / admin123')
        self.stdout.write('  Manager: manager@test.com / manager123')
        self.stdout.write('  User:    user@test.com / user123')
        self.stdout.write('  Guest:   guest@test.com / guest123')
