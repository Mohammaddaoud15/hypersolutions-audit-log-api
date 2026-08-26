# HyperSolutions Compliance Audit Log API

A REST API service for logging, retrieving, filtering, and searching compliance
audit trails — built for enterprise data governance use cases where every
access to or modification of sensitive data needs to be tracked and queryable.

## Features

- **JWT authentication** — register and log in to receive a bearer token
- **Role-aware access control** — `User` accounts only see their own logs;
  `Admin` / `Auditor` / `System` accounts can see all logs
- **Audit log CRUD** — create, retrieve by ID, list (paginated), and
  advanced search (by action, user, and date range)
- **PostgreSQL persistence** via SQLAlchemy, with schema migrations managed
  by Alembic
- **Dockerized** — API + database run together with a single command
- **pytest suite** covering auth flows and log access/ownership rules

## Tech Stack

| Layer          | Technology                     |
|----------------|---------------------------------|
| Framework      | FastAPI                        |
| Database       | PostgreSQL                     |
| ORM            | SQLAlchemy                     |
| Migrations     | Alembic                        |
| Validation     | Pydantic / pydantic-settings   |
| Auth           | JWT (python-jose) + bcrypt     |
| Testing        | pytest, pytest-cov, httpx      |
| Containers     | Docker, Docker Compose         |

## Project Structure

```
hypersolutions-audit-log-api/
├── app/
│   ├── main.py            # FastAPI app setup, router registration, /health
│   ├── models.py          # SQLAlchemy models (User, AuditLog)
│   ├── schemas.py         # Pydantic request/response schemas
│   ├── database.py        # Engine + session setup
│   ├── core/
│   │   ├── auth.py        # Password hashing, JWT creation
│   │   ├── config.py      # Settings (env-driven)
│   │   ├── dependencies.py# get_db, get_current_user
│   │   └── exceptions.py  # Shared HTTPException subclasses
│   └── routes/
│       ├── auth.py        # /auth/register, /auth/login
│       └── logs.py        # /logs, /logs/{id}, /logs/search
├── alembic/                # Migration environment + versions
├── tests/                  # pytest suite (auth + logs)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── pyproject.toml
└── .env.example
```

## Prerequisites

- Docker & Docker Compose (recommended path), **or**
- Python 3.12+ and a local PostgreSQL instance (manual path)

## Getting Started (Docker — recommended)

1. **Clone the repo and copy the environment template:**

```bash
   git clone <repo-url>
   cd hypersolutions-audit-log-api
   cp .env.example .env
```

   Edit `.env` and set a strong `JWT_SECRET` before running anything beyond
   local experimentation.

2. **Start the services:**

```bash
   docker-compose up --build
```

   This brings up a `postgres:15-alpine` container and the API container.
   The API waits for the database to report healthy before starting.

3. **Apply database migrations** (in a second terminal, once the containers
   are up):

```bash
   docker-compose exec web alembic upgrade head
```

   The tables are not created automatically on boot — migrations must be
   applied once before the first request.

4. **Open the interactive API docs:**

   Visit **http://localhost:8000/docs** (Swagger UI) or
   **http://localhost:8000/redoc**.

## Getting Started (local, without Docker)

1. Create a virtual environment and install dependencies:

```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and point `DATABASE_URL` at a running
   PostgreSQL instance you control.

3. Apply migrations:

```bash
   alembic upgrade head
```

4. Run the API:

```bash
   uvicorn app.main:app --reload
```

## Environment Variables

| Variable              | Description                                    | Default (example)      |
|-----------------------|-------------------------------------------------|-------------------------|
| `DATABASE_URL`        | PostgreSQL connection string (`postgresql+psycopg://...`) | — required |
| `JWT_SECRET`          | Secret used to sign JWTs — **change in production** | — required |
| `JWT_ALGORITHM`       | JWT signing algorithm                          | `HS256`                |
| `JWT_EXPIRE_MINUTES`  | Access token lifetime, in minutes              | `30`                    |

See `.env.example` for a ready-to-copy template.

## Authentication

1. **Register** a user (defaults to the `User` role):

```bash
   curl -X POST http://localhost:8000/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username": "alice", "password": "a-strong-password"}'
```

2. **Log in** to receive a JWT (note: this endpoint expects
   `application/x-www-form-urlencoded`, not JSON, per the OAuth2 password
   flow):

```bash
   curl -X POST http://localhost:8000/auth/login \
     -d "username=alice&password=a-strong-password"
```

   Response:

```json
   { "access_token": "<jwt>", "token_type": "bearer" }
```

3. **Call protected endpoints** with the token:

```bash
   curl http://localhost:8000/logs \
     -H "Authorization: Bearer <jwt>"
```

> **Note on roles:** new accounts are always created with the `User` role.
> `Admin`, `Auditor`, and `System` accounts (which can see every user's logs,
> not just their own) currently have to be assigned directly in the
> database — there is no self-service or bootstrap endpoint for elevated
> roles yet.

## API Reference

| Method | Endpoint       | Auth required | Description                                  |
|--------|----------------|:--------------:|-----------------------------------------------|
| POST   | `/auth/register` | No           | Create a new user account                     |
| POST   | `/auth/login`     | No           | Exchange credentials for a JWT                |
| POST   | `/logs`           | Yes          | Create an audit log entry                     |
| GET    | `/logs`           | Yes          | List logs (paginated: `skip`, `limit`)        |
| GET    | `/logs/{id}`      | Yes          | Retrieve a single log entry by ID             |
| GET    | `/logs/search`    | Yes          | Filter by `action`, `target_user_id`, `start_date`, `end_date` |
| GET    | `/health`         | No           | Service health check                          |

Full request/response schemas are available in the Swagger UI at `/docs`.

### Access rules

- A `User` can create logs and can only view/list/search **their own** logs.
- `Admin`, `Auditor`, and `System` accounts can view/list/search **all**
  users' logs.
- Requesting a log that doesn't exist returns `404`; requesting another
  user's log without an elevated role returns `403`.

## Running Tests

```bash
pytest --cov=app --cov-report=term-missing
```

Tests run against an in-memory SQLite database (via dependency override),
so no external database is needed to run the suite.

## Linting & Type Checking

```bash
ruff check .
mypy app/
```

## Data Model

**User**
- `id` (UUID), `username` (unique), `hashed_password`, `role`

**AuditLog**
- `id` (UUID)
- `timestamp` — when the action occurred
- `user_id` — who performed the action (FK → User)
- `action` — `READ` / `WRITE` / `DELETE` / `EXPORT`
- `resource_type` — e.g. `Table`, `Dataset`, `Credential`
- `resource_id` — identifier of the affected resource
- `status` — `SUCCESS` / `FAILED`
- `details` — free-form JSON context

