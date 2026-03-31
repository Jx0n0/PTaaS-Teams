# Frontend (Phase 1) - Embedded Console on Django

## What changed
To avoid environment/network issues, frontend is now served directly by Django at `http://localhost:8000/`.

No extra Node/Vite runtime is required for Phase 1 demo.

## Features on `/`
- 登录
- 我的信息 (`/api/v1/auth/me`)
- 用户管理（列表 + 新建）
- 角色管理（列表 + 新建）
- 用户角色绑定（列表 + 新建）
- 修改密码

## Run
```bash
docker compose up --build
```

Then open:
- `http://localhost:8000/`

## Technical implementation
- Template: `templates/console.html`
- Static JS: `static/js/console.js`
- Static CSS: `static/css/console.css`
- Root view: `config/views.py`
