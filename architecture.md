# Architecture — MUZEON Backend

## Technology Stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.13 |
| Framework | FastAPI |
| Database | PostgreSQL 17 (asyncpg) |
| ORM | SQLAlchemy 2.0 (async) |
| Session store | Redis 8 |
| Migrations | Alembic |
| Email | aiosmtplib (SMTP) |
| Password hashing | bcrypt |
| Package manager | uv |

---

## Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Presentation   app/api/          FastAPI routers, schemas  │
├─────────────────────────────────────────────────────────────┤
│  Application    app/services/     Business logic            │
├─────────────────────────────────────────────────────────────┤
│  Data access    app/repositories/ SQLAlchemy queries        │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure app/core/, app/db/ DB engine, Redis, config │
└─────────────────────────────────────────────────────────────┘
```

Dependencies flow downward only. Presentation knows nothing about repositories; services own transactions.

---

## Authentication

Session-based 2FA:

1. `POST /api/v1/auth/login` — validates password → generates 6-digit OTP → sends to email
2. `POST /api/v1/auth/verify` — validates OTP → creates Redis session → sets HTTP-only cookie
3. `GET  /api/v1/auth/me` — returns current user decoded from session
4. `POST /api/v1/auth/logout` — deletes session from Redis

### Redis session layout

```
Key                     Value (JSON)                        TTL
─────────────────────── ─────────────────────────────────── ────
session:{session_id}    {user_id, email, role, museum_id}   24 h
otp:{email}             {otp, attempts}                     10 min
```

Cookie: `session_id` — HttpOnly, Secure, SameSite=Lax.

OTP is rate-limited to 3 attempts; exceeding blocks the OTP and forces re-login.

---

## Multi-Tenancy

Row-level tenancy: every tenant-specific table has a `museum_id` column.

```
museum (tenant root)
  └── admin_users     museum_id FK  (nullable for super_admin)
  └── event           museum_id FK
  └── event_location  museum_id FK
```

Rules enforced at the service layer:
- `museum_id` comes from the session, never from request parameters.
- Non-super_admin roles can only read/write records belonging to their own `museum_id`.
- `super_admin` (`museum_id = NULL`) has platform-wide access.

---

## Authorization (RBAC)

| Role | Scope |
|---|---|
| `super_admin` | All museums: create, read, update, delete |
| `museum_admin` | Own museum: manage museum profile and users |
| `content` | Content operations within own museum |
| `marketer` | Marketing tools within own museum |
| `analyst` | Read-only analytics within own museum |

Enforced via FastAPI typed aliases:

```python
SuperAdmin   = Annotated[CurrentUserResponse, Depends(require_roles(super_admin))]
MuseumManager = Annotated[CurrentUserResponse, Depends(require_roles(super_admin, museum_admin))]
CurrentUser  = Annotated[CurrentUserResponse, Depends(get_current_user)]
```

`require_roles` raises HTTP 403 if the session user's role is not in the allowed set.

---

## API Reference

```
/api/v1/auth/
  POST  /login      Initiate login (password check → send OTP)
  POST  /verify     Verify OTP → create session cookie
  GET   /me         Current user info
  POST  /logout     Destroy session

/api/v1/museums/
  POST  /           Create museum + first admin (super_admin only)
  GET   /           List all museums (super_admin only)
  GET   /{id}       Get museum (own museum or super_admin)
  PATCH /{id}       Update museum; status/subscription require super_admin
  DELETE/{id}       Delete museum (super_admin only)

/api/v1/museums/{id}/users/
  POST  /           Create user within museum
  GET   /           List users in museum
  GET   /{user_id}  Get user
  PATCH /{user_id}  Update user
  DELETE/{user_id}  Delete user
```

---

## Directory Structure

```
app/
├── api/
│   ├── dependencies.py      Dependency injection: auth, services, roles
│   └── v1/
│       ├── router.py        Aggregates all sub-routers under /api/v1
│       └── endpoints/
│           ├── auth.py
│           ├── museums.py
│           └── users.py
├── core/
│   ├── config.py            pydantic-settings: DB, Redis, SMTP, session TTLs
│   ├── exceptions.py        HTTP exception subclasses (401/403/404/409)
│   ├── redis.py             Redis client singleton, init/close lifecycle
│   └── security.py          bcrypt hashing, OTP generation, session ID generation
├── db/
│   ├── session.py           SQLAlchemy async engine + session factory
│   ├── mixin/
│   │   ├── date_audit.py    DateMixin: created_at, updated_at
│   │   └── user_audit.py    UserAuditMixin: created_by, updated_by
│   └── models/
│       ├── base.py          DeclarativeBase with auto snake_case table names
│       ├── museum.py        Museum (tenant root)
│       ├── admin_users.py   AdminUsers (all roles)
│       ├── event.py         Event, EventLocation, EventType
│       └── admin_user_audit.py  Audit log
├── enums/
│   ├── database.py          MuseumStatusEnum, SubscriptionPlanEnum, UserRoleEnum, EventStatusEnum
│   └── audit.py             AuditAction
├── repositories/
│   ├── base.py              Generic async CRUD (get_by_id, get_all, create, update, delete)
│   ├── admin_user.py        get_by_email, get_by_museum, get_by_id_and_museum
│   └── museum.py            get_by_inn, get_by_ogrn
├── schemas/
│   ├── auth.py              LoginRequest, OTPVerifyRequest, CurrentUserResponse
│   ├── museum.py            MuseumCreate, MuseumUpdate, MuseumResponse, MuseumListResponse
│   └── user.py              UserCreate, UserUpdate, UserResponse, UserListResponse
└── services/
    ├── auth.py              AuthService: initiate_login, verify_otp, get_current_user, logout
    ├── email.py             send_otp_email (skipped when EMAIL_ENABLED=false)
    ├── museum.py            MuseumService: create, get, list_all, update, delete
    └── user.py              UserService: create, list_by_museum, get, update, delete

tests/
├── conftest.py              AsyncClient + dependency_overrides fixtures
├── test_auth.py             Login, OTP verify, /me, logout
├── test_museums.py          Museum CRUD
└── test_users.py            User management within museum
```

---

## Data Models

### Museum

Tenant root aggregate.

| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| name | varchar(255) | |
| legal_name | varchar(255) | |
| inn | varchar(12) UNIQUE | |
| ogrn | varchar(13) UNIQUE | |
| email | varchar(100) | |
| phone | varchar(11) | |
| address | varchar(255) | |
| status | enum | trial → active → inactive / blocked |
| subscription_plan | enum | free / basic / premium |
| subscription_end_date | timestamptz | |

Museum is always created in `trial` status. Status and subscription changes are `super_admin`-only.

### AdminUser

All platform users regardless of role.

| Column | Type | Notes |
|---|---|---|
| id | bigint PK | |
| email | varchar(100) UNIQUE | |
| password | varchar(255) | bcrypt hash |
| first_name | varchar(100) | |
| last_name | varchar(100) | |
| role | enum | |
| is_active | boolean | |
| museum_id | bigint FK | NULL for super_admin |

### Event / EventLocation / EventType

All tenant-scoped (museum_id FK). EventLocation was fixed to include `museum_id` alongside the existing audit columns.

---

## Configuration

Environment variables (see `.env.example`):

| Variable | Description |
|---|---|
| `DATABASE_URL` | asyncpg URL |
| `REDIS_URL` | Redis connection URL |
| `REDIS_PASSWORD` | Redis auth password |
| `SESSION_TTL` | Session lifetime in seconds (default 86400) |
| `OTP_TTL` | OTP lifetime in seconds (default 600) |
| `OTP_MAX_ATTEMPTS` | Max wrong OTP attempts before lockout (default 3) |
| `SMTP_HOST/PORT/USER/PASSWORD/FROM/TLS` | SMTP credentials |
| `EMAIL_ENABLED` | Set `false` in local/test to log OTP to console |
| `APP_ENV` | `local` (debug on, email off) or `dev` |

---

## Testing

```bash
uv run pytest
```

Tests mock the service layer using FastAPI `dependency_overrides`. No real DB or Redis is required. Each test file configures `AsyncMock` responses for the relevant service methods.

```python
# Example: override auth service for a specific test
mock_auth_service.initiate_login.side_effect = AuthenticationError("Invalid credentials")
response = await client.post("/api/v1/auth/login", json={...})
assert response.status_code == 401
```

---

## Future Bounded Contexts (planned)

### Event Management
Full event lifecycle: draft → published → archived / canceled. Promo materials via S3.

### Ticketing
Ticket categories, orders, season passes, fiscal integration (Atol / OrangeData).

### Analytics
CQRS read side: projections from domain events, dashboards, CSV/XLSX exports.

### Notifications
Domain event subscribers → Celery tasks → SMTP / FCM / APNs.

### Outbox Pattern
Domain events persisted in `outbox_events` within the same DB transaction, then relayed to Redis Pub/Sub or Kafka by a relay worker. Guarantees at-least-once delivery.
