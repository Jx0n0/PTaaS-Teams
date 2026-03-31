# Frontend (Ant Design Style) - Phase 1

## Why this version
In restricted environments, pulling `node:20-alpine` often fails. To ensure frontend can still run with Docker, this phase provides a **no-build static console** served by Python `http.server`.

## Capabilities
- Login / JWT token storage
- `/auth/me`
- User list
- Role list
- User-role binding list
- Change password

## Run
### Backend only
```bash
docker compose up --build
```

### Backend + Frontend
```bash
docker compose --profile frontend up --build
```

- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## Access notes
- `http://localhost:8000/` shows launcher page and frontend link.
- `http://localhost:5173/` shows interactive frontend console page.

## Implementation note
Frontend container now uses `python:3.12-slim` and serves `frontend/dist` directly, removing Node image dependency.
