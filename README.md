# Muzeon Backend

B2B SaaS-платформа для управления мероприятиями музеев: онбординг тенантов, управление событиями, продажа билетов, аналитика.

API обслуживает три клиента: веб-админку, публичный сайт и мобильное приложение.

## Пользователи

| Роль | Описание |
|---|---|
| `super_admin` | Администратор платформы — регистрирует музеи, управляет тенантами |
| `museum_admin` | Администратор музея — управляет сотрудниками, мероприятиями |
| `content` | Контент-менеджер — загружает материалы к мероприятиям |
| `marketer` | Маркетолог — управляет промо, уведомлениями |
| `analyst` | Аналитик — только чтение дашбордов и отчётов |

## Ключевые возможности

- **Мультитенантность** — каждый музей изолирован на уровне строк (row-level tenancy via `museum_id`)
- **Управление мероприятиями** — черновик → публикация → архив/отмена, группировка событий, промо-материалы
- **Продажа билетов** — категории цен, контроль вместимости, сезонные абонементы
- **Фискальная интеграция** — онлайн-касса (ФЗ-54)
- **Аналитика** — дашборды продаж, выручки, остатка мест; экспорт для бухгалтерии
- **Уведомления** — push/email

## Стек

- **Python 3.13+** / **FastAPI** — HTTP API
- **SQLAlchemy 2.x async** + **Alembic** — ORM и миграции
- **PostgreSQL** — основная БД
- **Redis** — кэш, очереди сессий
- **Celery + Redis** — фоновые задачи (отправка уведомлений, генерация отчётов)
- **S3-compatible** — хранение промо-материалов

## Быстрый старт

```bash
pip install -e ".[dev]"
cp .env.example .env
docker compose up -d postgres redis
alembic upgrade head
PYTHONPATH=app uvicorn app.main:app --reload
```

Документация API: `http://localhost:8000/docs`

## Структура проекта

```
muzeon-backend/
├── pyproject.toml
├── alembic.ini
├── alembic/versions/
└── src/
    ├── main.py                     # FastAPI app, подключение роутеров
    ├── config.py                   # Pydantic Settings (env vars)
    ├── shared/                     # Общие DDD-примитивы (не зависят от модулей)
    │   ├── domain/
    │   │   ├── base_entity.py      # BaseEntity с id/created_at
    │   │   ├── base_aggregate.py   # AggregateRoot — хранит domain events
    │   │   ├── value_object.py     # Immutable ValueObject
    │   │   ├── domain_event.py     # BaseDomainEvent
    │   │   └── repository.py      # Generic[T] абстрактный репозиторий
    │   └── infrastructure/
    │       ├── database.py         # AsyncEngine, get_session
    │       └── event_bus.py        # In-memory EventBus
    └── modules/
        ├── identity/               # Пользователи, аутентификация, JWT, роли
        ├── tenant/                 # Музей как тенант, подписка на платформу
        ├── events/                 # Мероприятия, типы, группы, промо-материалы
        ├── ticketing/              # Категории билетов, продажа, абонементы
        ├── analytics/              # Дашборды, отчёты (CQRS read side)
        └── notifications/          # Push/email уведомления
```

Детальное описание архитектуры → [architecture.md](architecture.md)

## API роутеры

| Prefix | Модуль | Доступ |
|---|---|---|
| `POST /api/v1/auth/login` | identity | все |
| `GET/POST /api/v1/admin/museums` | tenant | super_admin |
| `GET/POST /api/v1/museums/{id}/users` | identity | museum_admin |
| `GET/POST /api/v1/museums/{id}/events` | events | museum_admin, content |
| `GET/POST /api/v1/events/{id}/tickets` | ticketing | museum_admin |
| `GET /api/v1/museums/{id}/analytics` | analytics | analyst+ |
| `GET /api/v1/public/events` | events | публичный |
