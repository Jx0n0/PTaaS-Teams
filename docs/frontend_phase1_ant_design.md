# Frontend (Phase 1) - Embedded Console on Django

## Navigation
- 一级菜单默认展示
- 点击一级菜单后展开二级菜单（按需展示）
- 未开发功能显示占位标题页面

## Current IA
- 仪表盘
- 客户管理
- 项目管理
- 资产中心
- 漏洞中心
- 模板中心
- 报告中心
- 流程中心
- 系统管理
  - 用户管理（已实现）
  - 角色管理（已实现）
  - Audit Logs（占位）

## Top-right user menu
- 展示当前登录用户名
- 点击用户名显示下拉动画菜单
  - 修改密码（弹框）
  - 退出登录

## Run
```bash
docker compose up --build
```

Open: `http://localhost:8000/`
