# Resource Booking System

A backend system for booking shared university resources (library seats, study rooms, equipment) — built to solve a real concurrency problem: **preventing double-booking at the database level**, not just in application code.

## The Core Problem This Solves

Most beginner booking systems check for conflicts like this:
```python
if overlapping_booking_exists():
    raise Error
else:
    create_booking()
```
This fails under concurrent requests — two users can both pass the "is it free?" check at the exact same moment, and both bookings get created. This is a classic race condition.

This project solves it using a **PostgreSQL exclusion constraint**, so the database itself guarantees no two confirmed bookings for the same resource can ever overlap — even under simultaneous requests, with zero extra application logic needed:

```sql
ALTER TABLE booking
ADD CONSTRAINT no_overlapping_bookings
EXCLUDE USING gist (
    resource_id WITH =,
    tstzrange(start_time, end_time) WITH &&
)
WHERE (status = 'confirmed');
```

When a conflicting booking is attempted, the database rejects the insert, and the API returns a clean `409 Conflict`.

## Tech Stack

- **Framework:** FastAPI
- **Database:** PostgreSQL (NeonDB — serverless Postgres)
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Auth:** JWT (python-jose) + bcrypt password hashing (passlib)
- **Validation:** Pydantic

## Architecture

```
Client → FastAPI → SQLAlchemy → PostgreSQL (NeonDB)
```

Layered structure:
```
app/
  api/          # route handlers
  core/         # config, security (JWT, password hashing, RBAC dependencies)
  models/       # SQLAlchemy models
  schemas/      # Pydantic request/response schemas
  services/     # (business logic layer)
  db/           # database session management
```

## Permission Model

Two roles: `user` and `admin`, controlled via a `role` column (not a separate table).

| Action | User | Admin |
|---|---|---|
| Register / Login / View own profile | ✅ | ✅ |
| Browse resources / check availability | ✅ | ✅ |
| Create / cancel own booking | ✅ | ✅ |
| View / cancel own booking only | ✅ | ✅ (any booking) |
| Create / update / delete resources | ❌ | ✅ |
| View all bookings (admin dashboard) | ❌ | ✅ |
| View a resource's full booking history | ❌ | ✅ |

Two-layer authorization: **role-based** (admin-only endpoints via a `require_admin` dependency) and **ownership-based** (a user can only access their own bookings unless they're an admin).

## Design Decisions Worth Noting

- **Soft delete everywhere** (`is_active` on resources, `cancelled` status on bookings) — preserves history and reporting integrity instead of losing data on delete.
- **UUID primary keys** instead of sequential integers — avoids exposing record counts and simplifies future multi-database scenarios.
- **Cancelling a booking automatically frees the slot** — because the exclusion constraint only applies `WHERE status = 'confirmed'`, no extra code is needed to make a cancelled slot re-bookable.

## API Overview

### Auth
| Method | Endpoint | Access |
|---|---|---|
| POST | `/auth/register` | Public |
| POST | `/auth/login` | Public |
| GET | `/auth/me` | Authenticated |

### Resources
| Method | Endpoint | Access |
|---|---|---|
| POST | `/resources` | Admin |
| GET | `/resources` | Authenticated |
| GET | `/resources/{id}` | Authenticated |
| PUT | `/resources/{id}` | Admin |
| DELETE | `/resources/{id}` | Admin |
| GET | `/resources/{id}/bookings` | Admin |

### Bookings
| Method | Endpoint | Access |
|---|---|---|
| POST | `/bookings` | Authenticated |
| GET | `/bookings/me` | Authenticated (own only) |
| GET | `/bookings/{id}` | Owner or Admin |
| DELETE | `/bookings/{id}` | Owner or Admin |
| GET | `/bookings/admin/all` | Admin |

## Running Locally

1. Clone the repo:
   ```bash
   git clone https://github.com/your-username/resource-booking-system.git
   cd resource-booking-system
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

3. Create a `.env` file:
   ```
   DATABASE_URL=your-neondb-connection-string
   SECRET_KEY=your-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```

4. Enable the required PostgreSQL extension (run once in your database):
   ```sql
   CREATE EXTENSION IF NOT EXISTS btree_gist;
   ```

5. Run migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

7. Open `http://127.0.0.1:8000/docs` for the interactive API docs.

## Status

Core backend complete — all planned milestones (auth, resource management, booking with conflict detection, booking management, admin reporting) are implemented and manually tested.