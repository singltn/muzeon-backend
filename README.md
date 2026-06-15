# Muzeon Backend

B2B SaaS-платформа для управления мероприятиями музеев: онбординг тенантов, управление событиями, сотрудниками и подписками.

API обслуживает веб-панель администратора.

## Роли

| Роль | Описание |
|------|----------|
| `super_admin` | Администратор платформы — музеи, типы событий, назначение `museum_admin` |
| `museum_admin` | Администратор музея — профиль музея, сотрудники, события, площадки |
| `museum_stuff` | Сотрудник музея — работа с событиями и площадками (без управления пользователями) |


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

## Документация

- [architecture.md](architecture.md) — архитектура, модели данных, правила тенантности
