# Resource Booking System

A backend system for booking shared resources (seats, rooms, equipment) with database-level conflict detection to prevent double-booking.

**Stack:** FastAPI, PostgreSQL (NeonDB), SQLAlchemy, Alembic, JWT Auth

## Progress
- [x] Milestone 1: Authentication (register, login, JWT)
- [x] Milestone 2: Resource Management (Create + Read)
- [x] Milestone 3: Resource Management (Update + Delete)
- [X] Milestone 4: Booking Creation + Conflict Detection
- [X] Milestone 5: Booking Management
- [ ] Milestone 6: Admin & Reporting


### Server Reload
uvicorn app.main:app --reload