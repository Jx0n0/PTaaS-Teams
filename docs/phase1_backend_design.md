# Phase 1 Backend Design (Django/DRF)

## Scope for current stage
Current stage focuses on platform infrastructure only:
- Login authentication
- User management
- Role management
- User-role binding
- Basic permission boundary
- Password change
- Built-in admin account (dev seed)
- Base user info API
- Django admin support

Business tree entities (`Customer/Project/Asset/Batch`) remain as extension-ready placeholders only.

## Auth APIs (`/api/v1/auth/*`)
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/change-password`

### Login response
- `access`
- `refresh`
- `user` (`id`, `username`, `email`, `full_name`, `is_active`, `roles`)
- `roles`

### Password policy handling
- validate old password
- confirm new password twice
- use Django default password hash + validators
- increment `token_version` for future forced relogin mechanism

## Seed Strategy
Command: `python manage.py seed_initial_data`

Default local dev users:
- `admin / Admin123!`
- `pm_demo / Pm123456!`
- `tester_demo / Tester123!`
- `qa_demo / Qa123456!`

## Docker Runtime
- `docker compose up --build`
- web container auto-runs migrations + seed command before dev server.
