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
    $('loginPanel').classList.add('hidden');$('appPanel').classList.remove('hidden');await Promise.all([loadMe(),loadUsers(),loadRoles(),loadCustomers(),loadProjects(),loadBatches(),loadScanFiles(),loadFindings(),loadHistoryFindings()]);
  }catch{ $('loginMsg').innerText='登录失败，请检查用户名密码'; }
}

const listData=(payload)=>Array.isArray(payload)?payload:(payload.results||[]);
async function loadMe(){
  const me = await request('/api/v1/auth/me');
  $('meBox').textContent=JSON.stringify(me,null,2);
  $('currentUsername').textContent = me.username;
}
async function loadUsers(){ const ds=listData(await request('/api/v1/users')); $('usersBody').innerHTML=ds.map(x=>`<tr><td>${x.id}</td><td>${x.username}</td><td>${x.email||''}</td><td>${(x.roles||[]).join(',')}</td></tr>`).join(''); }
async function loadRoles(){ const ds=listData(await request('/api/v1/roles')); $('rolesBody').innerHTML=ds.map(x=>`<tr><td>${x.id}</td><td>${x.code}</td><td>${x.name}</td><td>${x.description||''}</td></tr>`).join(''); }
async function loadCustomers(){ const ds=listData(await request('/api/v1/customers')); $('customersBody').innerHTML=ds.map(x=>`<tr><td>${x.id}</td><td>${x.name||''}</td><td>${x.code||''}</td><td>${x.status||''}</td><td>${x.project_count ?? ''}</td></tr>`).join(''); }
async function loadProjects(){ const ds=listData(await request('/api/v1/projects')); $('projectsBody').innerHTML=ds.map(x=>`<tr><td>${x.id}</td><td>${x.name||''}</td><td>${x.customer?.name||''}</td><td>${x.test_type||''}</td><td>${x.status||''}</td></tr>`).join(''); }

async function loadBatches(){ const ds=listData(await request('/api/v1/batches')); $('batchesBody').innerHTML=ds.map(x=>`<tr><td>${x.id}</td><td>${x.name||''}</td><td>${x.batch_no||''}</td><td>${x.status||''}</td><td>${x.asset?.name||''}</td></tr>`).join(''); }
async function loadScanFiles(){ const ds=listData(await request('/api/v1/scan-files')); $('scanfilesBody').innerHTML=ds.map(x=>`<tr><td>${x.id}</td><td>${x.file_name||''}</td><td>${x.file_type||''}</td><td>${x.parse_status||''}</td><td>${x.uploaded_at||''}</td></tr>`).join(''); }
async function loadFindings(){ const ds=listData(await request('/api/v1/findings')); $('findingsBody').innerHTML=ds.map(x=>`<tr><td>${x.id}</td><td>${x.title||''}</td><td>${x.severity||''}</td><td>${x.status||''}</td><td>${x.source_type||''}</td></tr>`).join(''); }
async function loadHistoryFindings(){ const ds=listData(await request('/api/v1/history-findings')); $('historyFindingsBody').innerHTML=ds.map(x=>`<tr><td>${x.id}</td><td>${x.snapshot_title||''}</td><td>${x.snapshot_severity||''}</td><td>${x.snapshot_status||''}</td><td>${x.snapshot_at||''}</td></tr>`).join(''); }

async function createUser(){await request('/api/v1/users',{method:'POST',body:JSON.stringify({username:$('newUsername').value,email:$('newEmail').value,full_name:$('newFullName').value,password:$('newPassword').value})});await loadUsers();}
async function createRole(){await request('/api/v1/roles',{method:'POST',body:JSON.stringify({code:$('roleCode').value,name:$('roleName').value,description:$('roleDesc').value})});await loadRoles();}
async function changePassword(){
  await request('/api/v1/auth/change-password',{method:'POST',body:JSON.stringify({old_password:$('oldPwd').value,new_password:$('newPwd').value,confirm_password:$('confirmPwd').value})});
  alert('密码修改成功');
  closePwdModal();
}

function showTab(target, title){
  ['dashboardTab','usersTab','rolesTab','customersTab','projectsTab','batchesTab','scanfilesTab','findingsTab','historyFindingsTab','placeholderTab'].forEach(id=>$(id).classList.add('hidden'));
  if (target) {
    $(target).classList.remove('hidden');
  } else {
    $('placeholderTitle').textContent = title || '功能待开发';
    $('placeholderTab').classList.remove('hidden');
  }
}

function initNav(){
  const itemMap={dashboard:'dashboardTab',users:'usersTab',roles:'rolesTab',customers:'customersTab',projects:'projectsTab',batches:'batchesTab',scanfiles:'scanfilesTab',findings:'findingsTab',historyFindings:'historyFindingsTab'};
  document.querySelectorAll('.nav.item, .nav.sub, .nav.sub2, .nav.sub3').forEach(btn=>{
    btn.onclick=()=>{
      document.querySelectorAll('.nav').forEach(x=>x.classList.remove('active'));
      btn.classList.add('active');
      if(btn.dataset.implemented==='1') showTab(itemMap[btn.dataset.tab], btn.dataset.title);
      else showTab(null, btn.dataset.title);
    };
  });

  document.querySelectorAll('.group-toggle').forEach(btn=>{
    btn.onclick=()=>{
      const group = $(`group-${btn.dataset.group}`);
      group.classList.toggle('hidden');
    };
  });
}

function toggleUserDropdown(){ $('userDropdown').classList.toggle('hidden'); }
function openPwdModal(){ $('pwdModal').classList.remove('hidden'); $('userDropdown').classList.add('hidden'); }
function closePwdModal(){ $('pwdModal').classList.add('hidden'); }
function logout(){localStorage.clear();location.reload();}

$('loginBtn').onclick=login;
$('createUserBtn').onclick=createUser;
$('createRoleBtn').onclick=createRole;
$('submitPwdBtn').onclick=changePassword;
$('closePwdModalBtn').onclick=closePwdModal;
$('openPwdModalBtn').onclick=openPwdModal;
$('logoutBtn').onclick=logout;
$('userMenuBtn').onclick=toggleUserDropdown;
initNav();

if(access){$('loginPanel').classList.add('hidden');$('appPanel').classList.remove('hidden');Promise.all([loadMe(),loadUsers(),loadRoles(),loadCustomers(),loadProjects(),loadBatches(),loadScanFiles(),loadFindings(),loadHistoryFindings()]);}
