# Система аутентификации и авторизации

## Описание

Backend-приложение на Django + DRF, реализующее собственную систему аутентификации и авторизации с JWT-токенами и гибкой системой разграничения прав доступа.

## Технологии

- **Django 4.2** - веб-фреймворк
- **Django REST Framework 3.14** - создание API
- **PostgreSQL / SQLite** - база данных
- **PyJWT** - работа с JWT-токенами
- **bcrypt** - хеширование паролей
- **django-cors-headers** - поддержка CORS

## Архитектура системы управления доступом

### Схема базы данных

Система основана на ролевой модели доступа (RBAC - Role-Based Access Control) со следующими таблицами:

#### 1. Таблица `users` (Пользователи)
Хранит информацию о пользователях системы.

| Поле | Тип | Описание |
|------|-----|----------|
| id | int | Уникальный идентификатор |
| email | varchar | Email (уникальный, используется для входа) |
| first_name | varchar | Имя |
| last_name | varchar | Фамилия |
| middle_name | varchar | Отчество |
| password | varchar | Хеш пароля (bcrypt) |
| is_active | bool | Статус активности (мягкое удаление) |
| is_staff | bool | Является ли сотрудником |
| is_superuser | bool | Является ли суперпользователем |
| created_at | datetime | Дата создания |
| updated_at | datetime | Дата обновления |
| deleted_at | datetime | Дата удаления (для мягкого удаления) |

#### 2. Таблица `sessions` (Сессии)
Хранит активные сессии пользователей.

| Поле | Тип | Описание |
|------|-----|----------|
| id | int | Уникальный идентификатор |
| user_id | int | Ссылка на пользователя |
| token | text | JWT-токен |
| expires_at | datetime | Время истечения сессии |
| is_active | bool | Статус сессии |
| created_at | datetime | Дата создания |

#### 3. Таблица `roles` (Роли)
Описывает пользовательские роли в системе.

| Поле | Тип | Описание |
|------|-----|----------|
| id | int | Уникальный идентификатор |
| name | varchar | Название роли (уникальное) |
| description | text | Описание роли |
| created_at | datetime | Дата создания |

**Примеры ролей:**
- `admin` - администратор (полный доступ ко всем ресурсам)
- `manager` - менеджер (управление продуктами и заказами)
- `user` - обычный пользователь (базовый доступ)
- `guest` - гость (минимальный доступ, только чтение)

#### 4. Таблица `business_elements` (Бизнес-элементы)
Описывает объекты приложения, к которым осуществляется доступ.

| Поле | Тип | Описание |
|------|-----|----------|
| id | int | Уникальный идентификатор |
| name | varchar | Название элемента (уникальное) |
| description | text | Описание элемента |
| created_at | datetime | Дата создания |

**Примеры бизнес-элементов:**
- `users` - пользователи
- `products` - продукты/товары
- `orders` - заказы
- `access_rules` - правила доступа

#### 5. Таблица `access_role_rules` (Правила доступа ролей)
Хранит правила доступа определённой роли к определённому бизнес-элементу.

| Поле | Тип | Описание |
|------|-----|----------|
| id | int | Уникальный идентификатор |
| role_id | int | Ссылка на роль |
| element_id | int | Ссылка на бизнес-элемент |
| read_permission | bool | Может ли роль читать элементы |
| read_all_permission | bool | Может ли роль читать ВСЕ элементы (включая чужие) |
| create_permission | bool | Может ли роль создавать элементы |
| update_permission | bool | Может ли роль обновлять СВОИ элементы |
| update_all_permission | bool | Может ли роль обновлять ВСЕ элементы |
| delete_permission | bool | Может ли роль удалять СВОИ элементы |
| delete_all_permission | bool | Может ли роль удалять ВСЕ элементы |
| created_at | datetime | Дата создания |
| updated_at | datetime | Дата обновления |

#### 6. Таблица `user_roles` (Роли пользователей)
Связывает пользователей с ролями (многие-ко-многим).

| Поле | Тип | Описание |
|------|-----|----------|
| id | int | Уникальный идентификатор |
| user_id | int | Ссылка на пользователя |
| role_id | int | Ссылка на роль |
| assigned_at | datetime | Дата назначения роли |

#### 7. Таблицы бизнес-объектов (Mock)
- `mock_products` - продукты (name, description, price, owner_id, created_at, updated_at)
- `mock_orders` - заказы (product_id, user_id, status, quantity, created_at, updated_at)

### Логика работы системы прав доступа

#### Аутентификация
1. **Регистрация**: Пользователь вводит email, имя, пароль. Пароль хешируется через bcrypt.
2. **Login**: Пользователь входит по email и паролю. Система генерирует JWT-токен с `user_id` и возвращает его.
3. **Идентификация**: При последующих запросах пользователь передаёт токен в заголовке `Authorization: Bearer {token}`. Кастомный Middleware извлекает токен, проверяет его и устанавливает `request.user`.
4. **Logout**: Токен деактивируется в таблице `sessions` (is_active=False).
5. **Обновление профиля**: Авторизованный пользователь может редактировать свои данные.
6. **Удаление аккаунта**: Мягкое удаление - `is_active=False`, пользователь не может войти, но данные остаются в БД.

#### Авторизация
1. Пользователь отправляет запрос к ресурсу с JWT-токеном.
2. Middleware идентифицирует пользователя из токена.
3. Система проверяет роли пользователя через таблицу `user_roles`.
4. Для каждой роли проверяются права доступа в `access_role_rules` к запрашиваемому бизнес-элементу.
5. **Если пользователь не идентифицирован** → ошибка **401 Unauthorized**.
6. **Если пользователь идентифицирован, но нет прав** → ошибка **403 Forbidden**.
7. **Если права есть** → запрос выполняется.

#### Правила _all_
- Поля с суффиксом `_all_permission` определяют, может ли пользователь работать со **всеми** объектами или только со **своими** (где он является `owner`).
- Например, `read_permission=True` и `read_all_permission=False` означает, что пользователь видит только свои объекты.
- `read_permission=True` и `read_all_permission=True` означает доступ ко всем объектам.

### Пример прав доступа для ролей

| Роль | Элемент | Read | Read All | Create | Update | Update All | Delete | Delete All |
|------|---------|------|----------|--------|--------|------------|--------|------------|
| admin | users | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| admin | products | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| admin | orders | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| manager | products | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| manager | orders | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ |
| user | products | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| user | orders | ✓ | ✗ | ✓ | ✓ | ✗ | ✓ | ✗ |
| guest | products | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| guest | orders | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

## API Endpoints

### Аутентификация
- `POST /api/auth/register/` - Регистрация
- `POST /api/auth/login/` - Вход (получение токена)
- `POST /api/auth/logout/` - Выход
- `GET /api/auth/me/` - Получить текущий профиль
- `PUT /api/auth/me/` - Обновить профиль
- `DELETE /api/auth/me/` - Удалить аккаунт (мягкое)

### Управление правилами (только для администраторов)
- `GET /api/access/roles/` - Список ролей
- `POST /api/access/roles/` - Создать роль
- `GET /api/access/elements/` - Список бизнес-элементов
- `GET /api/access/rules/` - Список правил доступа
- `POST /api/access/rules/` - Создать правило
- `PUT /api/access/rules/{id}/` - Обновить правило
- `DELETE /api/access/rules/{id}/` - Удалить правило

### Бизнес-объекты (Mock)
- `GET /api/products/` - Список продуктов
- `POST /api/products/` - Создать продукт
- `GET /api/orders/` - Список заказов
- `POST /api/orders/` - Создать заказ

## Установка и запуск

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Примените миграции:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

4. Заполните тестовыми данными (опционально):
```bash
python manage.py loaddata fixtures/initial_data.json
```

5. Запустите сервер:
```bash
python manage.py runserver
```

## Структура проекта

```
testovoe/
├── config/              # Настройки Django
│   └── settings.py
├── users/               # Приложение пользователей
│   ├── models.py        # CustomUser, Session
│   ├── views.py         # Auth views
│   ├── middleware.py    # JWT middleware
│   └── serializers.py
├── access/              # Приложение управления доступом
│   ├── models.py        # Role, BusinessElement, AccessRoleRule
│   ├── views.py         # Access management views
│   └── serializers.py
├── business/            # Приложение бизнес-объектов
│   ├── models.py        # MockProduct, MockOrder
│   └── views.py         # Mock views
├── requirements.txt
├── manage.py
└── README.md
```
