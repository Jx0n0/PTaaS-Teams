const API = 'http://localhost:8000'
let access = localStorage.getItem('access')
let refresh = localStorage.getItem('refresh')

async function api(path, opts={}) {
  const headers = { 'Content-Type':'application/json', ...(opts.headers||{}) }
  if (access) headers.Authorization = `Bearer ${access}`
  let res = await fetch(`${API}${path}`, { ...opts, headers })
  if (res.status===401 && refresh) {
    const rr = await fetch(`${API}/api/v1/auth/refresh`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({refresh})})
    if (rr.ok) {
      const d = await rr.json(); access=d.access; localStorage.setItem('access', access)
      headers.Authorization = `Bearer ${access}`
      res = await fetch(`${API}${path}`, { ...opts, headers })
    }
  }
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

async function doLogin() {
  const username=document.getElementById('username').value
  const password=document.getElementById('password').value
  try{
    const d = await api('/api/v1/auth/login',{method:'POST',body:JSON.stringify({username,password})})
    access=d.access; refresh=d.refresh
    localStorage.setItem('access',access); localStorage.setItem('refresh',refresh)
    document.getElementById('loginCard').classList.add('hidden')
    document.getElementById('app').classList.remove('hidden')
    loadMe()
  }catch(e){document.getElementById('loginMsg').innerText='登录失败'}
}

async function loadMe(){document.getElementById('meOut').innerText=JSON.stringify(await api('/api/v1/auth/me'),null,2)}
async function loadUsers(){const ds=await api('/api/v1/users/');document.getElementById('usersBody').innerHTML=ds.map(x=>`<tr><td>${x.id}</td><td>${x.username}</td><td>${x.email||''}</td><td>${(x.roles||[]).join(',')}</td></tr>`).join('')}
async function loadRoles(){const ds=await api('/api/v1/roles/');document.getElementById('rolesBody').innerHTML=ds.map(x=>`<tr><td>${x.id}</td><td>${x.code}</td><td>${x.name}</td></tr>`).join('')}
async function loadUserRoles(){const ds=await api('/api/v1/user-roles/');document.getElementById('userRolesBody').innerHTML=ds.map(x=>`<tr><td>${x.id}</td><td>${x.user}</td><td>${x.role}</td><td>${x.scope_type}</td></tr>`).join('')}

async function changePwd(){
  const old_password=prompt('旧密码'); const new_password=prompt('新密码'); const new_password_confirm=prompt('确认新密码')
  await api('/api/v1/auth/change-password',{method:'POST',body:JSON.stringify({old_password,new_password,new_password_confirm})})
  alert('修改成功')
}
function logout(){localStorage.clear();location.reload()}

if (access){document.getElementById('loginCard').classList.add('hidden');document.getElementById('app').classList.remove('hidden');loadMe()}

window.doLogin=doLogin;window.loadMe=loadMe;window.loadUsers=loadUsers;window.loadRoles=loadRoles;window.loadUserRoles=loadUserRoles;window.changePwd=changePwd;window.logout=logout
