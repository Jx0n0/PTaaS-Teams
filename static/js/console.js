const API='';
let access=localStorage.getItem('access');
let refresh=localStorage.getItem('refresh');

const $ = (id)=>document.getElementById(id);

async function request(path, options={}){
  const headers={'Content-Type':'application/json', ...(options.headers||{})};
  if(access) headers.Authorization=`Bearer ${access}`;
  let res=await fetch(`${API}${path}`, {...options, headers});
  if(res.status===401 && refresh){
    const rr=await fetch('/api/v1/auth/refresh',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({refresh})});
    if(rr.ok){const d=await rr.json();access=d.access;localStorage.setItem('access',access);headers.Authorization=`Bearer ${access}`;res=await fetch(`${API}${path}`, {...options, headers});}
  }
  if(!res.ok) throw new Error(await res.text());
  return res.json();
}

async function login(){
  try{
    const data=await request('/api/v1/auth/login',{method:'POST',body:JSON.stringify({username:$('username').value,password:$('password').value})});
    access=data.access;refresh=data.refresh;localStorage.setItem('access',access);localStorage.setItem('refresh',refresh);
    $('loginPanel').classList.add('hidden');$('appPanel').classList.remove('hidden');await loadAll();
  }catch{ $('loginMsg').innerText='登录失败，请检查用户名密码'; }
}

async function loadAll(){await Promise.all([loadMe(),loadUsers(),loadRoles(),loadBindings(),loadSelects()]);}
async function loadMe(){ $('meBox').textContent=JSON.stringify(await request('/api/v1/auth/me'),null,2); }
async function loadUsers(){ const ds=await request('/api/v1/users/'); $('usersBody').innerHTML=ds.map(x=>`<tr><td>${x.id}</td><td>${x.username}</td><td>${x.email||''}</td><td>${(x.roles||[]).join(',')}</td></tr>`).join(''); window._users=ds; }
async function loadRoles(){ const ds=await request('/api/v1/roles/'); $('rolesBody').innerHTML=ds.map(x=>`<tr><td>${x.id}</td><td>${x.code}</td><td>${x.name}</td><td>${x.description||''}</td></tr>`).join(''); window._roles=ds; }
async function loadBindings(){ const ds=await request('/api/v1/user-roles/'); $('bindingsBody').innerHTML=ds.map(x=>`<tr><td>${x.id}</td><td>${x.user}</td><td>${x.role}</td><td>${x.scope_type}</td></tr>`).join(''); }

function loadSelects(){
  $('bindUser').innerHTML=(window._users||[]).map(u=>`<option value='${u.id}'>${u.username}</option>`).join('');
  $('bindRole').innerHTML=(window._roles||[]).map(r=>`<option value='${r.id}'>${r.code}</option>`).join('');
}

async function createUser(){await request('/api/v1/users/',{method:'POST',body:JSON.stringify({username:$('newUsername').value,email:$('newEmail').value,full_name:$('newFullName').value,password:$('newPassword').value})});await loadUsers();}
async function createRole(){await request('/api/v1/roles/',{method:'POST',body:JSON.stringify({code:$('roleCode').value,name:$('roleName').value,description:$('roleDesc').value})});await loadRoles();loadSelects();}
async function createBinding(){await request('/api/v1/user-roles/',{method:'POST',body:JSON.stringify({user:Number($('bindUser').value),role:Number($('bindRole').value),scope_type:$('bindScope').value})});await loadBindings();}
async function changePassword(){await request('/api/v1/auth/change-password',{method:'POST',body:JSON.stringify({old_password:$('oldPwd').value,new_password:$('newPwd').value,new_password_confirm:$('newPwd2').value})});alert('密码修改成功');}

function initTabs(){
  const map={dashboard:'dashboardTab',users:'usersTab',roles:'rolesTab',bindings:'bindingsTab',security:'securityTab'};
  document.querySelectorAll('.nav').forEach(btn=>btn.onclick=()=>{document.querySelectorAll('.nav').forEach(x=>x.classList.remove('active'));btn.classList.add('active');Object.values(map).forEach(id=>$(id).classList.add('hidden'));$(map[btn.dataset.tab]).classList.remove('hidden');});
}

function logout(){localStorage.clear();location.reload();}

$('loginBtn').onclick=login;$('createUserBtn').onclick=createUser;$('createRoleBtn').onclick=createRole;$('bindBtn').onclick=createBinding;$('pwdBtn').onclick=changePassword;$('logoutBtn').onclick=logout;initTabs();
if(access){$('loginPanel').classList.add('hidden');$('appPanel').classList.remove('hidden');loadAll();}
