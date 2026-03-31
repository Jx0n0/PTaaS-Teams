# Frontend (Phase 1) - Embedded Console on Django

## What changed
Frontend navigation is restructured by full product IA. Implemented features are interactive, and not-yet-developed features are shown as placeholder pages with titles.

## Navigation structure
- Dashboard
- client
  - client List
  - client Detail
    - Projects
    - Report Templates
    - Reports
- Projects
  - Project List
  - Project Detail
    - Asset List
    - Asset Detail
      - Batches
      - Scan Files
      - Findings
      - History Findings
- Assets
  - Asset List
- Findings
  - All Findings
  - My Findings
  - Finding Detail
- Templates
  - Vulnerability database
  - Report Templates
- Reports
  - Generate Report
  - Report List
  - Report Detail
- Workflow Center
  - My Tasks
  - QA Review Queue
  - Tester Tasks
  - PM Review
- 系统管理
  - 用户管理（已实现）
  - 角色管理（已实现）
  - 修改密码（已实现）
  - Audit Logs（占位）

## Run
```bash
docker compose up --build
```

Open: `http://localhost:8000/`

## Implemented interactive pages (Phase 1)
- 登录
- 用户管理（列表 + 新建）
- 角色管理（列表 + 新建）
- 修改密码

Other nav entries currently display placeholder titles for future phases.
