# Backend Architecture

## Overview

The Wedding Plan API is a **FastAPI** application backed by **PostgreSQL**, served behind **Nginx**, and containerised with **Docker Compose**. It follows a layered architecture where every feature is expressed as a trio of files: a SQLAlchemy model, a Pydantic schema, and a FastAPI router.

---

## Technology Stack

| Layer | Technology | Version |
|---|---|---|
| Web framework | FastAPI | ≥ 0.104.1 |
| ASGI server | Uvicorn | 0.20.0 |
| Production server | Gunicorn | 21.2.0 |
| Reverse proxy | Nginx | (alpine image) |
| ORM | SQLAlchemy | 2.0.23 |
| Database | PostgreSQL | 15 |
| DB adapter | psycopg2 | 2.9.10 |
| Data validation | Pydantic v2 | 2.4.2 |
| Authentication | PyJWT + bcrypt | 2.8.0 / 4.0.1 |
| Password hashing | passlib | 1.7.4 |
| Config / env | environs | 9.5.0 |
| Email | fastapi-mail | 1.4.1 |
| Containerisation | Docker Compose | v3 |

---

## Infrastructure

```
┌─────────────────────────────────────────────┐
│                  Docker Network              │
│                 (local_sandbox)              │
│                                              │
│  ┌──────────┐    ┌──────────┐   ┌────────┐  │
│  │  Nginx   │───▶│  FastAPI │──▶│Postgres│  │
│  │ :8060    │    │  :8000   │   │ :5432  │  │
│  └──────────┘    └──────────┘   └────────┘  │
│  (public)        (internal)     (internal)  │
└─────────────────────────────────────────────┘
```

- **Nginx** is the only publicly exposed entry point (port `8060` locally). It proxies all requests to the FastAPI container.
- **FastAPI / Uvicorn** runs internally on port `8000` and is never exposed directly.
- **PostgreSQL 15** runs internally on port `5432` (mapped to `5492` on the host for local tooling access).
- The database is initialised on first start by mounting `sql/01-wedding-plan-schema.sql` into the PostgreSQL container's `docker-entrypoint-initdb.d/` directory.
- `docker compose watch` is configured on the API container so source changes under `src/app/` are synced into the running container without a full rebuild.

---

## Project Structure

```
wed-backend/
├── config/                        # Environment variable files (.env)
│   ├── config_api_local.env
│   └── config_db_local.env
├── nginx/                         # Nginx configs (local / prod)
├── sql/
│   ├── 01-wedding-plan-schema.sql # Full schema + seed data
│   ├── 01-wedding-plan-schema-prod.sql
│   └── 02-blog-posts.sql          # Blog feature migration
├── src/app/                       # Application root (Python path)
│   ├── app.py                     # FastAPI app creation + router registration
│   ├── requirements.txt
│   ├── database/
│   │   └── db.py                  # Engine, session factory, Base, get_session()
│   ├── models/
│   │   ├── __init__.py            # Re-exports all ORM models
│   │   ├── users.py
│   │   ├── reservations.py
│   │   ├── notes.py
│   │   ├── tasks.py
│   │   ├── gifts.py
│   │   ├── budget.py
│   │   ├── guests.py
│   │   ├── partner_profiles.py
│   │   ├── partner_expenses.py
│   │   └── blog.py
│   ├── schemas/
│   │   ├── notes.py
│   │   ├── tasks.py
│   │   ├── blog.py
│   │   └── ...                    # One file per feature
│   ├── routers/
│   │   ├── auth.py
│   │   ├── notes.py
│   │   ├── blog.py
│   │   └── ...                    # One file per feature
│   ├── utils/
│   │   └── security.py            # JWT helpers, password hashing, get_current_user
│   └── email_service/             # Email notification helpers
├── docker-compose-local.yml
└── docker-compose-prod.yml
```

---

## Application Entry Point

**`src/app/app.py`** creates the FastAPI instance and mounts every router:

```python
from fastapi import FastAPI
from routers import auth, dashboard, tasks, gifts, guests, budget, \
    reservations, vendors, notes, users, partner_expenses, blog

app = FastAPI(title="Wedding Plan API", version="1.0")

app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(tasks.router)
# ... all other routers
app.include_router(blog.router)
```

The working directory inside the container is `src/app/`, so all imports are relative to that root (e.g. `from routers import blog`, `from models import User`).

---

## Layered Architecture Pattern

Every feature follows the same three-layer pattern:

```
HTTP Request
     │
     ▼
┌──────────────────────────────────────┐
│  Router  (src/app/routers/[name].py) │  ← FastAPI path operations, auth dependency
└──────────────────────────────────────┘
     │  reads/writes via SQLAlchemy Session
     ▼
┌──────────────────────────────────────┐
│  Model   (src/app/models/[name].py)  │  ← SQLAlchemy ORM table definition
└──────────────────────────────────────┘
     │  validated by
     ▼
┌──────────────────────────────────────┐
│  Schema  (src/app/schemas/[name].py) │  ← Pydantic v2 request/response models
└──────────────────────────────────────┘
```

### Model conventions (`src/app/models/`)

- All tables live in the `weddingplan` PostgreSQL schema via `__table_args__ = {"schema": "weddingplan"}`.
- Primary keys are UUID, generated by `uuid.uuid4`.
- Foreign keys specify `ondelete="CASCADE"` to keep referential integrity.
- Timestamps use `server_default=func.now()` so the database owns the clock.
- `updated_at` columns additionally set `onupdate=func.now()`.

```python
class BlogPost(Base):
    __tablename__ = "blog_posts"
    __table_args__ = {"schema": "weddingplan"}

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id  = Column(UUID(as_uuid=True), ForeignKey("weddingplan.users.id", ondelete="CASCADE"), nullable=False)
    title      = Column(String(255), nullable=False)
    content    = Column(Text, nullable=False)
    excerpt    = Column(String(500), nullable=True)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

All models are imported in `models/__init__.py` so routers can do `from models import User, BlogPost`.

### Schema conventions (`src/app/schemas/`)

Each feature exposes up to four Pydantic models:

| Schema | Purpose |
|---|---|
| `[Feature]CreateSchema` | Input validation for POST |
| `[Feature]UpdateSchema` | Input validation for PATCH (all fields Optional) |
| `[Feature]ResponseSchema` | Output for authenticated endpoints, includes private fields |
| `[Feature]PublicSchema` | Output for unauthenticated public endpoints |

All response schemas set `model_config = ConfigDict(from_attributes=True)` to serialise ORM objects directly.

### Router conventions (`src/app/routers/`)

```python
router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskDashboard, status_code=201)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),   # ← auth guard
):
    ...
```

- `Depends(get_session)` injects a SQLAlchemy session that is closed after the request.
- `Depends(get_current_user)` validates the JWT and injects the `User` ORM object.
- Owner-scoped queries always filter by `[model].user_id == current_user.id` or `[model].author_id == current_user.id`.

---

## Database

### Schema

All tables belong to the `weddingplan` PostgreSQL schema. The `pgcrypto` extension is installed in the same schema to provide `gen_random_uuid()`.

### Tables

```
weddingplan
├── users                  Core identity + role table
├── partner_profiles       Business profile for PARTNER users
├── reservations           Event booking requests between couples and partners
├── notes                  Authored notes, optionally linked to a reservation
├── tasks                  Couple to-do checklist items
├── gifts                  Wedding gift registry items
├── budgets                Single budget record per user
├── guests                 Guest list, optionally linked to a reservation
├── partner_expenses       Business expense tracking for partners
└── blog_posts             Couple blog posts (published or draft)
```

### Entity Relationship Summary

```
users ──────────────────────────────────────────────────────────────────┐
  │ (PARTNER)                                                            │ (COUPLE)
  │                                                                      │
  ├──▶ partner_profiles (1:1)                                            │
  │                                                                      │
  ├──▶ reservations.partner_id ◀──────── reservations.couple_id ◀───────┤
  │         │                                                            │
  │         └──▶ notes.reservation_id                                    │
  │         └──▶ guests.reservation_id                                   │
  │                                                                      │
  ├──▶ partner_expenses                  tasks ◀────────────────────────┤
  │                                      gifts ◀────────────────────────┤
  │                                      budgets (1:1) ◀────────────────┤
  │                                      notes (global) ◀───────────────┤
  │                                      blog_posts ◀───────────────────┘
  └──────────────────────────────────────────────────────────────────────
```

### User Roles

| Role | Description |
|---|---|
| `COUPLE` | Main wedding planners. Own tasks, gifts, budget, guests, notes, and blog posts. |
| `PARTNER` | Venue / vendor accounts. Own partner profiles, receive reservations, log expenses. |
| `ADMIN` | Reserved for platform administration. |

### Migrations

There is no migration framework (e.g. Alembic). Schema changes are managed as numbered SQL files in `sql/`:

| File | Contents |
|---|---|
| `sql/01-wedding-plan-schema.sql` | Full initial schema + seed data (local) |
| `sql/01-wedding-plan-schema-prod.sql` | Full initial schema, no seed data (prod) |
| `sql/02-blog-posts.sql` | Adds `blog_posts` table and indexes |

The local Docker Compose mounts `01-wedding-plan-schema.sql` into the Postgres init directory. Subsequent migration files must be applied manually to existing environments.

---

## Authentication

**File:** `src/app/utils/security.py`

The API uses **JWT Bearer tokens** with the OAuth2 password flow.

### Token lifecycle

```
POST /auth/login  (username + password)
        │
        ▼
   verify_password()        bcrypt hash comparison
        │
        ▼
   create_access_token()    HS256 JWT, exp = now + ACCESS_TOKEN_EXPIRE_MINUTES
        │
        ▼
   { access_token, token_type: "bearer" }  ──▶  client stores token
```

### Per-request validation

```
Authorization: Bearer <token>
        │
        ▼
   get_current_user()       Depends() used on every protected endpoint
        │  jwt.decode()     Validates signature and expiry
        │  payload["sub"]   Contains the user UUID
        │  db.query(User)   Fetches live user record
        ▼
   current_user: User       Injected into the route handler
```

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `JWT_SECRET_KEY` | `"secret"` | HMAC signing key — **must be overridden in production** |
| `ALGORITHM` | `"HS256"` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token lifetime in minutes |

---

## API Reference

Base URL (local): `http://localhost:8060`  
Interactive docs: `http://localhost:8060/docs`

### Auth — `/auth`

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | No | Register a new user |
| POST | `/auth/login` | No | OAuth2 password flow — returns JWT |

### Dashboard — `/dashboard`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/dashboard/` | Yes | Aggregated stats for the current user |

### Tasks — `/tasks`

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/tasks/` | Yes | Create a task |
| GET | `/tasks/` | Yes | List current user's tasks |
| PATCH | `/tasks/{task_id}` | Yes | Update a task (owner only) |
| DELETE | `/tasks/{task_id}` | Yes | Delete a task (owner only) |

### Gifts — `/gifts`

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/gifts/` | Yes | Add a gift registry item |
| GET | `/gifts/` | Yes | List current user's gifts |
| PATCH | `/gifts/{gift_id}` | Yes | Update a gift |
| DELETE | `/gifts/{gift_id}` | Yes | Delete a gift |

### Budget — `/budget`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/budget/` | Yes | Get current user's budget |
| PATCH | `/budget/` | Yes | Update budget amount |

### Guests — `/guests`

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/guests/` | Yes | Add a guest |
| GET | `/guests/` | Yes | List current user's guests |
| PATCH | `/guests/{guest_id}` | Yes | Update a guest |
| DELETE | `/guests/{guest_id}` | Yes | Delete a guest |

### Reservations — `/reservations`

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/reservations/guest` | No | Public: guest inquiry to a partner |
| GET | `/reservations/` | Yes | List reservations for current user |
| GET | `/reservations/{id}` | Yes | Get a single reservation |
| PATCH | `/reservations/{id}` | Yes | Update reservation status / details |
| DELETE | `/reservations/{id}` | Yes | Delete a reservation |

### Vendors — `/vendors`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/vendors/` | No | Public: list all partner profiles |
| GET | `/vendors/{partner_id}` | No | Public: get a single partner profile |

### Notes — `/notes`

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/notes/` | Yes | Create a note (optionally linked to a reservation) |
| GET | `/notes/` | Yes | List global notes for current user |
| PATCH | `/notes/{note_id}` | Yes | Update a note (author only) |

### Blog — `/blog`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/blog/public/` | No | Public: list all published blog posts |
| GET | `/blog/public/{id}` | No | Public: get a single published post |
| POST | `/blog/` | Yes | Create a blog post |
| GET | `/blog/` | Yes | List current user's blog posts |
| GET | `/blog/{id}` | Yes | Get a single post (author only) |
| PATCH | `/blog/{id}` | Yes | Update a post (author only) |
| DELETE | `/blog/{id}` | Yes | Delete a post (author only) |

### Users — `/users`

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/users/me` | Yes | Get current user's profile |
| PATCH | `/users/me` | Yes | Update current user's profile |

### Partner Expenses — `/partner-expenses`

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/partner-expenses/` | Yes | Log a business expense |
| GET | `/partner-expenses/` | Yes | List current partner's expenses |
| PATCH | `/partner-expenses/{id}` | Yes | Update an expense |
| DELETE | `/partner-expenses/{id}` | Yes | Delete an expense |

---

## Database Connection

**File:** `src/app/database/db.py`

```python
SQLALCHEMY_DATABASE_URL = (
    f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}'
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

`get_session` is a FastAPI dependency that opens a session at the start of each request and guarantees it is closed on completion, even if the handler raises.

### Environment variables

| Variable | Description |
|---|---|
| `DB_USER` | PostgreSQL username |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_HOST` | PostgreSQL host (container name in Docker) |
| `DB_PORT` | PostgreSQL port (default `5432`) |
| `DB_DATABASE` | Database name |

---

## Local Development

### Prerequisites

- Docker + Docker Compose
- A Docker network named `local_sandbox`:

  ```bash
  docker network create --subnet=172.27.0.0/16 local_sandbox
  ```

### Start the stack

```bash
docker compose -f docker-compose-local.yml up --build
```

The API will be available at `http://localhost:8060`.  
Interactive API docs: `http://localhost:8060/docs`

### Live reload

`docker compose watch` is configured — changes to `src/app/` are synced to the running container automatically.

### Applying additional SQL migrations

```bash
docker exec -i wedding-plan-database-local \
  psql -U postgres -d postgres < sql/02-blog-posts.sql
```

### Seed credentials (local only)

| Role | Username | Password |
|---|---|---|
| COUPLE | `alice_and_john` | `hashed_pass_123` |
| PARTNER | `grand_venue` | `hashed_pass_456` |
| PARTNER | `tasty_catering` | `hashed_pass_789` |
