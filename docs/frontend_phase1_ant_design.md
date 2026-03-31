# Frontend (Ant Design) - Phase 1

## Goal
Provide an API-first internal operations console for platform base capabilities:
- Login / auth
- User management
- Role management
- User-role binding
- Password change

## Stack
- React + Vite
- Ant Design 5
- Axios

## Pages
1. Login page (`/` before auth)
2. Dashboard
3. User Management
4. Role Management
5. User-Role Binding
6. Account Security (Change Password)

## API Mapping
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/change-password`
- `GET/POST /api/v1/users/`
- `GET/POST /api/v1/roles/`
- `GET/POST /api/v1/user-roles/`

## Run
### Backend only (default, no Node image pull)
```bash
docker compose up --build
```
- Backend API: `http://localhost:8000`

### Backend + Frontend (requires network access to pull Node base image)
```bash
docker compose --profile frontend up --build
```
- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## Why frontend is optional profile
Some restricted environments cannot reach Docker Hub to pull `node:20-alpine`. Making frontend service profile-gated keeps backend boot reliable.
