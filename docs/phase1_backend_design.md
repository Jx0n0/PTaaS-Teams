# Phase 1 Backend Design (Django/DRF)

## 1. Model Design

### Auth & RBAC
- `User`: internal staff identity (`AUTH_USER_MODEL`) for PM/Tester/QA/Admin.
- `Role`: role template with stable code (`admin`, `pm`, `tester`, `qa`).
- `UserRole`: many-to-many mapping with scope:
  - `GLOBAL`: platform-level
  - `CUSTOMER`: customer-level
  - `PROJECT`: project-level

### Business Tree
- `Customer` -> `Project` -> `Asset` -> `Batch`.
- This aligns with future attachment points for `Scan File`, `Findings`, `History Findings`, and report workflow.

### Extensibility Principles
- Shared `TimeStampedModel` for all entities.
- Stable unique business identifiers (`Customer.code`, per-customer `Project.code`).
- `Batch.extra` JSON as extensible metadata slot for parser/workflow states.

## 2. Permission Scope

`ScopeService` resolves accessible customer/project sets by `UserRole`, with queryset filtering + object access checks.

Role capabilities in Phase 1:
- `Admin`: full platform access (user/role management + all business resources)
- `PM`: manage `Customer`/`Project` and read/write scoped resources
- `Tester`: manage `Asset`/`Batch` in scoped projects
- `QA`: read scoped resources (write for findings/report in later phases)

## 3. API Surface (Phase 1)

JWT:
- `POST /api/token/`
- `POST /api/token/refresh/`

CRUD ViewSets:
- `/api/users/`
- `/api/roles/`
- `/api/user-roles/`
- `/api/customers/`
- `/api/projects/`
- `/api/assets/`
- `/api/batches/`

## 4. Seed Strategy

Command: `python manage.py seed_initial_data`

Creates:
- roles: `admin`, `pm`, `tester`, `qa`
- users: `admin`, `pm_demo`, `tester_demo`, `qa_demo`
- baseline tree: `acme -> web-2026 -> Main Domain -> Q1 Full Scan`
- sample scoped role assignments on project level

## 5. Docker Runtime

- `docker-compose up --build`
- web container auto-runs migrations + seed command before dev server.
- default admin credential (dev only): `admin / Admin123!`.
