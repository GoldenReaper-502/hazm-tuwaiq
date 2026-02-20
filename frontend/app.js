const CONFIG = {
  API_BASE_URL: '/api/v1',
};

const state = {
  theme: localStorage.getItem('theme') || 'light',
  language: localStorage.getItem('language') || 'ar',
  currentPage: 'dashboard',
  chatHistory: JSON.parse(localStorage.getItem('chatHistory') || '[]'),
  token: localStorage.getItem('token') || null,
};

async function apiFetch(endpoint, options = {}) {
  const headers = { Accept: 'application/json', ...(options.headers || {}) };
  if (!(options.body instanceof FormData)) headers['Content-Type'] = 'application/json';
  if (state.token) headers['Authorization'] = `Bearer ${state.token}`;
  const response = await fetch(`${CONFIG.API_BASE_URL}${endpoint}`, { ...options, headers });
  const data = await response.json().catch(() => ({}));
  if (!response.ok || data.ok === false) {
    const msg = data?.error?.message || data?.detail?.error?.message || data?.detail || `HTTP ${response.status}`;
    throw new Error(msg);
  }
  return data.data ?? data;
}

function showError(id, e) { document.getElementById(id).innerHTML = `<div class="error">${e.message}</div>`; }
function fmt(v) { return v ?? '-'; }

async function ensureLogin() {
  if (state.token) return;
  const res = await apiFetch('/auth/login', { method: 'POST', body: JSON.stringify({ username: 'admin', password: 'Admin@123' }) });
  state.token = res.access_token;
  localStorage.setItem('token', state.token);
}

function navigateTo(pageName) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById(pageName + 'Page')?.classList.add('active');
  document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
  document.querySelector(`[data-page="${pageName}"]`)?.classList.add('active');
  state.currentPage = pageName;
  const titles = { dashboard:'لوحة التحكم', cameras:'الكاميرات', detection:'الكشف والقراءة', chatbot:'المساعد الذكي', incidents:'الحوادث', risk:'تقييم المخاطر', inspections:'التفتيش', reports:'التقارير' };
  document.getElementById('pageTitle').textContent = titles[pageName];
  document.getElementById('breadcrumbPage').textContent = titles[pageName];
  loadPageData(pageName);
}

async function loadPageData(pageName) {
  await ensureLogin();
  ({ dashboard:loadDashboard, cameras:loadCameras, detection:loadDetectionHistory, chatbot:loadChatHistory, incidents:loadIncidents, risk:loadRisks, inspections:loadInspections, reports:loadReports }[pageName] || (()=>{}))();
}

async function loadDashboard() {
  try {
    const data = await apiFetch('/dashboard/overview');
    document.getElementById('camerasCount').textContent = fmt(data.counters.cameras_active);
    document.getElementById('detectionsCount').textContent = (data.last_detections || []).length;
    document.getElementById('incidentsCount').textContent = fmt(data.counters.incidents_open);
    document.getElementById('chatsCount').textContent = state.chatHistory.length;
    document.getElementById('recentIncidents').innerHTML = (data.last_incidents || []).map(x => `<div class="incident-item"><strong>${x.title}</strong><small>${x.created_at || ''}</small></div>`).join('') || '<div class="loading">لا توجد حوادث</div>';
    document.getElementById('recentDetections').innerHTML = (data.last_detections || []).map(x => `<div class="incident-item"><strong>${x.event_type}</strong><small>${x.created_at || ''}</small></div>`).join('') || '<div class="loading">لا توجد كشوفات</div>';
    const b = document.getElementById('systemStatus');
    b.innerHTML = '<span class="status-dot"></span><span>متصل</span>';
  } catch (e) { showError('recentIncidents', e); showError('recentDetections', e); }
}

async function loadCameras() {
  const el = document.getElementById('camerasGrid');
  try {
    const cams = await apiFetch('/cameras');
    el.innerHTML = cams.map(c => `<div class="camera-card"><h4>${c.name}</h4><p>${c.site} - ${c.location}</p><p>الحالة: <strong>${c.status}</strong></p><button class="btn btn-secondary" onclick="checkCameraHealth(${c.id})">Health</button></div>`).join('') || '<div class="loading">لا توجد كاميرات</div>';
  } catch (e) { showError('camerasGrid', e); }
}

async function checkCameraHealth(id){
  try{ const h = await apiFetch(`/cameras/${id}/health`); alert(`Camera ${id}: ${h.status}`);}catch(e){alert(e.message)}
}

function showAddCameraModal() {
  const name = prompt('اسم الكاميرا'); if (!name) return;
  apiFetch('/cameras', { method:'POST', body: JSON.stringify({ name, site:'Plant-1', location:'Area-A', stream_url:'rtsp://demo' }) }).then(loadCameras).catch(e=>alert(e.message));
}

function setupDetectionUpload() {
  const fileInput = document.getElementById('detectionFile');
  const upload = document.getElementById('uploadArea');
  fileInput?.addEventListener('change', () => {
    const f = fileInput.files[0];
    if (!f) return;
    const reader = new FileReader();
    reader.onload = () => { document.getElementById('previewImage').src = reader.result; document.getElementById('detectionPreview').style.display = 'block'; document.getElementById('detectBtn').style.display = 'inline-flex'; };
    reader.readAsDataURL(f);
  });
  upload?.addEventListener('click', ()=>fileInput.click());
}

async function detectObjects() {
  const file = document.getElementById('detectionFile').files[0];
  if (!file) return;
  const fd = new FormData();
  fd.append('image', file);
  fd.append('zones_json', JSON.stringify([{ id:'restricted-1', type:'restricted', polygon:[[0,0],[0,600],[300,600],[300,0]] }]));
  try {
    const data = await apiFetch('/vision/detect/image', { method:'POST', body: fd, headers:{} });
    document.getElementById('detectionResults').innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    loadDetectionHistory();
  } catch (e) { showError('detectionResults', e); }
}

async function loadDetectionHistory(){
  try{ const rows = await apiFetch('/vision/events');
    document.getElementById('detectionHistory').innerHTML = rows.map(r=>`<div class="incident-item"><strong>${r.event_type}</strong><small>${r.created_at}</small></div>`).join('') || '<div class="loading">لا يوجد</div>';
  } catch(e){ showError('detectionHistory', e); }
}

function loadChatHistory(){
  const el = document.getElementById('chatMessages');
  const base = `<div class="chat-welcome"><h4>مرحباً بك في المساعد الذكي!</h4><p>اسأل عن السلامة والحوادث والمخاطر.</p></div>`;
  el.innerHTML = base + state.chatHistory.map(m=>`<div class="chat-bubble ${m.role==='user'?'user':'bot'}">${m.text}</div>`).join('');
}

function sendQuickQuestion(q){ document.getElementById('chatInput').value=q; sendChat(); }
function clearChat(){ state.chatHistory=[]; localStorage.setItem('chatHistory','[]'); loadChatHistory(); }

async function sendChat(){
  const input = document.getElementById('chatInput');
  const msg = input.value.trim(); if (!msg) return;
  state.chatHistory.push({ role:'user', text:msg });
  input.value='';
  try {
    const data = await apiFetch('/assistant/chat', { method:'POST', body: JSON.stringify({ message: msg }) });
    state.chatHistory.push({ role:'bot', text: data.reply });
  } catch (e) {
    state.chatHistory.push({ role:'bot', text: `خطأ: ${e.message}` });
  }
  localStorage.setItem('chatHistory', JSON.stringify(state.chatHistory));
  loadChatHistory();
}

async function loadIncidents(){
  try{ const rows = await apiFetch('/incidents');
    document.getElementById('incidentsList').innerHTML = rows.map(i=>`<div class="card" style="margin-bottom:1rem"><div class="card-body"><h4>${i.title}</h4><p>Risk: ${i.risk_score}</p><small>${i.status}</small></div></div>`).join('') || '<div class="loading">لا توجد حوادث</div>';
  } catch(e){ showError('incidentsList', e); }
}

function showAddIncidentModal(){
  const title = prompt('عنوان الحادثة'); if(!title) return;
  apiFetch('/incidents', {method:'POST', body: JSON.stringify({ title, description:'Demo', site:'Plant-1', department:'Operations', severity:3, likelihood:3, status:'open' })}).then(loadIncidents).catch(e=>alert(e.message));
}

async function loadRisks(){
  try{ const rows = await apiFetch('/risks');
    document.getElementById('riskList').innerHTML = rows.map(r=>`<div class="card" style="margin-bottom:1rem"><div class="card-body"><h4>${r.hazard}</h4><p>Residual: ${r.residual_risk}</p><small>${r.site}</small></div></div>`).join('') || '<div class="loading">لا توجد مخاطر</div>';
  }catch(e){ showError('riskList', e); }
}

function showAddRiskModal(){
  const hazard=prompt('الخطر'); if(!hazard) return;
  apiFetch('/risks',{method:'POST',body:JSON.stringify({hazard,site:'Plant-1',department:'Operations',controls:'PPE',severity:4,likelihood:3})}).then(loadRisks).catch(e=>alert(e.message));
}

async function loadInspections(){
  try{ const rows = await apiFetch('/inspections');
    document.getElementById('inspectionsList').innerHTML = rows.map(i=>`<div class="card" style="margin-bottom:1rem"><div class="card-body"><h4>${i.site} - ${i.department}</h4><p>Status: ${i.status}</p><small>${i.scheduled_date}</small></div></div>`).join('') || '<div class="loading">لا توجد تفتيشات</div>';
  }catch(e){ showError('inspectionsList', e); }
}

function showAddInspectionModal(){
  apiFetch('/inspections',{method:'POST',body:JSON.stringify({site:'Plant-1',department:'Operations',template_id:1,scheduled_date:new Date().toISOString().slice(0,10)})}).then(loadInspections).catch(e=>alert(e.message));
}

async function loadReports(){
  try { const data = await apiFetch('/reports/weekly');
    document.getElementById('reportsList').innerHTML = `<div class="card"><div class="card-body"><h4>Weekly Report</h4><pre>${JSON.stringify(data,null,2)}</pre></div></div>`;
  } catch(e){ showError('reportsList', e); }
}

async function generateReport(){
  try { const data = await apiFetch('/reports/export?type=weekly'); alert(`Generated: ${data.filename}`); } catch(e){ alert(e.message); }
}
async function exportReports(){ return generateReport(); }

function toggleTheme(){ state.theme = state.theme==='light'?'dark':'light'; document.body.classList.toggle('dark-theme'); localStorage.setItem('theme',state.theme); document.getElementById('themeIcon').textContent = state.theme==='dark'?'☀️':'🌙'; }
function toggleLanguage(){ state.language = state.language==='ar'?'en':'ar'; localStorage.setItem('language',state.language); document.getElementById('langText').textContent = state.language==='ar'?'EN':'عر'; document.documentElement.lang = state.language; document.documentElement.dir = state.language==='ar'?'rtl':'ltr'; }

document.addEventListener('DOMContentLoaded', async () => {
  if (state.theme==='dark'){ document.body.classList.add('dark-theme'); document.getElementById('themeIcon').textContent='☀️'; }
  document.querySelectorAll('.nav-item').forEach(nav => nav.addEventListener('click', e => { e.preventDefault(); navigateTo(nav.getAttribute('data-page')); }));
  document.getElementById('themeToggle')?.addEventListener('click', toggleTheme);
  document.getElementById('langToggle')?.addEventListener('click', toggleLanguage);
  document.getElementById('chatInput')?.addEventListener('keypress', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChat(); } });
  setupDetectionUpload();
  await ensureLogin();
  loadPageData('dashboard');
});
