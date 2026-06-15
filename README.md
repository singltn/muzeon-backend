# Muzeon Backend

B2B SaaS-платформа для управления мероприятиями музеев: онбординг тенантов, управление событиями, сотрудниками и подписками.

API обслуживает веб-админку (и в перспективе — публичный сайт и мобильное приложение).

## Роли

| Роль | Описание |
|------|----------|
| `super_admin` | Администратор платформы — музеи, типы событий, назначение `museum_admin` |
| `museum_admin` | Администратор музея — профиль музея, сотрудники, события, площадки |
| `museum_stuff` | Сотрудник музея — работа с событиями и площадками (без управления пользователями) |

## Реализовано

- **Аутентификация** — email + пароль → OTP на почту → session cookie (Redis)
- **Мультитенантность** — row-level isolation через `museum_id`; доступ к чужому музею запрещён
- **Музеи** — CRUD для `super_admin`; просмотр/редактирование своего музея для `museum_admin`
- **Пользователи музея** — CRUD; пароль генерируется и отправляется на email
- **Типы событий** — глобальный справочник; CRUD для `super_admin`
- **Площадки и события** — tenant-scoped CRUD; жизненный цикл статусов события
- **Дашборд** — агрегированные данные в зависимости от роли
- **Сессии** — список активных сессий, завершение сторонней сессии

## В планах

- Продажа билетов, фискализация, аналитика, push/email-уведомления, публичное API

## Стек

| Компонент | Технология |
|-----------|------------|
| Runtime | Python 3.13+ |
| API | FastAPI |
| ORM | SQLAlchemy 2.x (async) + Alembic |
| БД | PostgreSQL 17 |
| Сессии / OTP | Redis 8 |
| Почта | aiosmtplib |
| Пароли | bcrypt |

## Быстрый старт

```bash
# Зависимости
pip install -e ".[dev]"

# Окружение
cp .env.example .env

# Инфраструктура
docker compose up -d db redis

# Миграции
alembic upgrade head

# Супер-админ (интерактивно)
python -m app.scripts.create_super_user

# Запуск (порт 8080)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

Или полный стек через Docker:

```bash
docker compose up -d
```

- **Swagger UI:** http://localhost:8080/api/v1/docs
- **Health check:** http://localhost:8080/health

## Переменные окружения

| Переменная | Описание |
|------------|----------|
| `APP_ENV` | `local` / `dev` — профиль настроек |
| `DATABASE_URL` | PostgreSQL (`postgresql+asyncpg://...`) |
| `REDIS_URL` | Redis |
| `REDIS_PASSWORD` | Пароль Redis |
| `SMTP_*` | Настройки почты (OTP, пароли новых пользователей) |
| `SESSION_TTL` | Время жизни сессии (сек), по умолчанию 86400 |
| `OTP_TTL` | Время жизни OTP (сек), по умолчанию 300 |
| `CORS_ORIGINS` | Разрешённые origins для фронтенда |

Полный список — в [.env.example](.env.example).

## Аутентификация

Session-based 2FA через HttpOnly cookie `session_id`:

1. `POST /api/v1/admin/auth/login` — проверка пароля, OTP на email
2. `POST /api/v1/admin/auth/verify` — проверка OTP, установка cookie
3. `GET /api/v1/admin/users/me` — текущий пользователь
4. `POST /api/v1/admin/auth/logout` — выход

Все защищённые запросы отправлять с `credentials: 'include'`.

## Структура проекта

```
muzeon-backend/
├── app/
│   ├── main.py                 # FastAPI app, middleware, lifespan
│   ├── api/
│   │   ├── dependencies.py     # DI, auth guards, RBAC
│   │   └── v1/
│   │       ├── router.py
│   │       └── endpoints/admin/
│   │           ├── auth.py
│   │           ├── dashboard.py
│   │           ├── museums.py
│   │           ├── museum_users.py
│   │           ├── events.py
│   │           ├── users.py
│   │           └── session.py
│   ├── core/                   # config, security, redis, logging
│   ├── cruds/                  # Data access layer
│   ├── db/models/              # SQLAlchemy models
│   ├── enums/
│   ├── exceptions/
│   ├── schemas/                # Pydantic DTO
│   ├── services/               # Business logic
│   └── scripts/
│       └── create_super_user.py
├── alembic/
├── tests/
├── docs/
│   └── admin-frontend-prompt.md  # Спека для фронтенда админки
├── architecture.md
├── docker-compose.yaml
└── pyproject.toml
```

Слои: `endpoints → services → cruds → models`.

## API

Базовый prefix: `/api/v1`

### Auth и профиль

| Метод | Путь | Доступ |
|-------|------|--------|
| POST | `/admin/auth/login` | — |
| POST | `/admin/auth/verify` | — |
| POST | `/admin/auth/logout` | session |
| GET | `/admin/users/me` | session |
| GET | `/admin/sessions` | session |
| DELETE | `/admin/sessions/{session_id}` | session |

### Дашборд

| Метод | Путь | Доступ |
|-------|------|--------|
| GET | `/admin/dashboard` | session (ответ зависит от роли) |

### Музеи

| Метод | Путь | Доступ |
|-------|------|--------|
| GET | `/museums` | `super_admin` |
| POST | `/museums` | `super_admin` |
| GET | `/museums/{id}` | `super_admin`, `museum_admin` (свой) |
| PATCH | `/museums/{id}` | `super_admin`, `museum_admin` (свой)* |

\* `museum_admin` не может менять `status`, `subscription_plan`, `subscription_end_date`.

### Пользователи музея

| Метод | Путь | Доступ |
|-------|------|--------|
| GET/POST | `/museums/{id}/users` | `super_admin`, `museum_admin` |
| GET/PATCH/DELETE | `/museums/{id}/users/{user_id}` | `super_admin`, `museum_admin` |

При создании пароль генерируется на сервере и отправляется на email.  
`super_admin` может назначить `museum_admin`; `museum_admin` — только `museum_stuff`.

### Типы событий (глобальные)

| Метод | Путь | Доступ |
|-------|------|--------|
| GET | `/event-types` | session |
| GET | `/event-types/{id}` | session |
| POST/PATCH/DELETE | `/event-types` … | `super_admin` |

### Площадки

| Метод | Путь | Доступ |
|-------|------|--------|
| GET | `/museums/{id}/event-locations` | EventReader** |
| POST/PATCH/DELETE | `/museums/{id}/event-locations` … | EventManager** |

### События

| Метод | Путь | Доступ |
|-------|------|--------|
| GET | `/museums/{id}/events` | EventReader** |
| POST/PATCH/DELETE | `/museums/{id}/events` … | EventManager** |

**EventReader:** `super_admin`, `museum_admin`, `museum_stuff`  
**EventManager:** `super_admin`, `museum_admin`, `museum_stuff`

**Статусы события:** `draft` → `published` / `canceled`; `published` → `archived` / `canceled`.

## Дашборд по ролям

`GET /admin/dashboard` возвращает JSON с полем `role`:

| Роль | Содержимое |
|------|------------|
| `super_admin` | Сводка по музеям (статусы, тарифы), истекающие подписки, проблемные музеи, топ-5 по событиям |
| `museum_admin` | Карточка музея, сотрудники, события по статусам, активные площадки, ближайшие события |
| `museum_stuff` | Карточка музея (read-only), события (total/published/draft), ближайшие события, предупреждение о подписке |

## Тесты

```bash
pytest
```

## Документация

- [architecture.md](architecture.md) — архитектура, модели данных, правила тенантности
- [docs/admin-frontend-prompt.md](docs/admin-frontend-prompt.md) — спецификация для фронтенда админки (меню, маршруты, RBAC)
