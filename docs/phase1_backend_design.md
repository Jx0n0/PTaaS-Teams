# Phase 1 Backend Design (Django/DRF)

## Auth & Password
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/change-password`

`change-password` payload:
- `old_password`
- `new_password`
- `confirm_password`

Validation:
- old password correct
- new password non-empty
- confirm matches new password
- Django password validators enabled

## Permission Baseline
- `IsAuthenticatedUser`: logged-in baseline
- `IsPlatformAdmin`: admin-only permission
- `AdminOnlyViewSetMixin`: reusable admin default for management viewsets
- `ScopedPermissionMixin`: future scope-control extension hook

## Customer Module
Model fields:
- `name`, `code`, `status(active/inactive/archived)`, `description`, timestamps

APIs:
- `GET /api/v1/customers` (pagination, search by name/code, status filter, project_count)
- `POST /api/v1/customers`
- `GET /api/v1/customers/{id}` (project_count + report_count)
- `PUT/PATCH /api/v1/customers/{id}`

Permissions:
- Admin/PM can write
- Tester/QA read-only

## Project Module
Model fields:
- `customer`, `name`, `code`, `test_type`, `status`, `description`, `start_date`, `end_date`, `created_by`, timestamps

APIs:
- `GET /api/v1/projects` (customer_id/status filter)
- `POST /api/v1/projects`
- `GET /api/v1/projects/{id}` (asset_count + batch_count)
- `PUT/PATCH /api/v1/projects/{id}`

Permissions:
- PM/Admin write
- Tester/QA read-only

## Report Template Module
APIs:
- `GET /api/v1/report-templates?customer_id=`
- `POST /api/v1/report-templates` (DOCX upload)
- `GET /api/v1/report-templates/{id}`
- `GET /api/v1/report-templates/{id}/download`
- `PUT /api/v1/report-templates/{id}`

Current storage abstraction:
- keeps `storage_key` (MinIO-ready)
- file stored using Django file storage for current phase

## Report Module
APIs:
- `POST /api/v1/reports/generate`
- `GET /api/v1/reports`
- `GET /api/v1/reports/{id}/download`

Current phase behavior:
- generate endpoint creates report record with `ready` state and generated key placeholder
- async Celery/docxtpl pipeline reserved for next phase

Permissions:
- PM-only for generate action
- read follows scoped access
