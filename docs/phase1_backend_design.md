# Phase 1 Backend Design (Django/DRF)

## Auth & Password
Endpoints:
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/change-password`

`change-password` payload:
- `old_password`
- `new_password`
- `confirm_password`

Validation:
- old password must be correct
- new and confirm must match
- new password cannot be empty
- Django default password validators enabled

## Base Permission Control (Role-based)
- `IsAuthenticatedUser`: logged-in baseline
- `IsPlatformAdmin`: Admin has full management rights
- User/Role/UserRole APIs default to admin-only
- `/auth/me` and `/auth/change-password` are accessible to logged-in users
- `ScopedPermissionMixin` reserved for future Customer/Project scope module evolution

## User & Role Models
- Custom `User` model (username/email/full_name/is_active/is_staff/is_superuser/timestamps)
- Independent `Role` model (code unique)
- `UserRole` binding model for role assignment (GLOBAL/CUSTOMER/PROJECT)

System boot creates built-in roles automatically:
- `ADMIN`
- `PM`
- `TESTER`
- `QA`

## User Management API
- `GET /api/v1/users`
- `POST /api/v1/users`
- `GET /api/v1/users/{id}`
- `PUT /api/v1/users/{id}`
- `PATCH /api/v1/users/{id}`
- `POST /api/v1/users/{id}/reset-password`

List supports filtering/search:
- `username`
- `email`
- `full_name`
- `is_active`
- `search`

Pagination enabled via DRF PageNumberPagination.
