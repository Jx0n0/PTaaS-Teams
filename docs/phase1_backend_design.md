# Phase 1 Backend Design (Django/DRF)

## User Model (Custom)
`users.User` is a custom auth model (not Django default extension-only pattern), with:
- `id` (UUID primary key)
- `username` (unique)
- `email` (unique)
- `full_name`
- password hash handled by Django (`set_password`)
- `is_active` / `is_staff` / `is_superuser`
- `created_at` / `updated_at`

## Role Model
`users.Role` is independent (not Django Group), with:
- `id` (UUID primary key)
- `code` (unique: `ADMIN`, `PM`, `TESTER`, `QA`)
- `name`
- `description`
- timestamps

Built-in roles are auto-created on migration via `post_migrate` hook.

## User Management API
- `GET /api/v1/users`
- `POST /api/v1/users`
- `GET /api/v1/users/{id}`
- `PUT /api/v1/users/{id}`
- `PATCH /api/v1/users/{id}`
- `POST /api/v1/users/{id}/reset-password/` (admin)

Supports:
- create user with secure password hashing
- update basic info
- enable/disable (`is_active`)
- detail query
- paginated list
- filtering/search by `username`, `email`, `full_name`, `is_active`, `search`

## Auth APIs
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/change-password`

## Frontend Integration
System management (用户管理/角色管理/角色绑定/修改密码) is grouped under one 一级菜单 in embedded console.
