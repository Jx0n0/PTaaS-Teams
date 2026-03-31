from django.http import HttpResponse


def root_landing(_request):
    html = """
<!doctype html>
<html lang='zh-CN'>
<head>
  <meta charset='utf-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1' />
  <title>PTaaS Teams Console</title>
  <style>
    body { margin:0; font-family: Inter, Arial, sans-serif; background:#f5f7fb; }
    .wrap { max-width: 860px; margin: 48px auto; padding: 0 16px; }
    .card { background:#fff; border-radius:16px; padding:28px; box-shadow:0 8px 28px rgba(20,20,43,.08); }
    h1 { margin:0 0 10px; color:#1f2937; }
    p { color:#4b5563; line-height:1.7; }
    .row { display:flex; gap:12px; flex-wrap: wrap; margin-top:20px; }
    a.btn { text-decoration:none; background:#1677ff; color:white; padding:10px 16px; border-radius:10px; }
    a.btn.secondary { background:#eef2ff; color:#374151; }
    code { background:#f3f4f6; padding:2px 6px; border-radius:6px; }
  </style>
</head>
<body>
  <div class='wrap'>
    <div class='card'>
      <h1>PTaaS Teams 平台入口</h1>
      <p>你访问的是后端服务端口 <code>:8000</code>。前端控制台运行在 <code>:5173</code>（Ant Design）。</p>
      <p>如果你已启动前端服务，请点击“打开前端控制台”。如果前端未启动，请先执行 <code>docker compose --profile frontend up --build</code>。</p>
      <div class='row'>
        <a class='btn' href='http://localhost:5173' target='_blank' rel='noreferrer'>打开前端控制台</a>
        <a class='btn secondary' href='/api/v1/auth/me'>查看 API 示例</a>
      </div>
    </div>
  </div>
</body>
</html>
"""
    return HttpResponse(html)
