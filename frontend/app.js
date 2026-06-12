const CONFIG = {
  API_BASE_URL: 'http://localhost:8000/api/v1',
};

const I18N = {
  ar: {
    app_title: 'السلامة الذكية | Smart Safety - منصة الذكاء الاصطناعي للسلامة',
    logo_title: 'حزم طويق',
    home: 'الرئيسية',
    loading: 'جاري التحميل...',
    connected: 'متصل',
    disconnected: 'غير متصل',
    retry_connection: 'إعادة المحاولة',
    nav_dashboard: 'لوحة التحكم',
    nav_cameras: 'الكاميرات',
    nav_detection: 'الكشف والقراءة',
    nav_chatbot: 'المساعد الذكي',
    nav_incidents: 'الحوادث',
    nav_risk: 'تقييم المخاطر',
    nav_inspections: 'التفتيش',
    nav_reports: 'التقارير',
    stat_cameras: 'الكاميرات النشطة',
    stat_detections: 'الكشوفات اليوم',
    stat_incidents: 'الحوادث المفتوحة',
    stat_chats: 'المحادثات',
    recent_incidents: 'الحوادث الأخيرة',
    recent_detections: 'الكشوفات الأخيرة',
    view_all: 'عرض الكل',
    add_camera: 'إضافة كاميرا جديدة',
    loading_cameras: 'جاري تحميل الكاميرات...',
    upload_detection: 'رفع صورة للكشف والقراءة',
    upload_hint: 'اضغط أو اسحب صورة هنا',
    choose_image: 'اختر صورة',
    detect_objects: 'كشف الأشياء',
    detection_history: 'سجل الكشوفات',
    chatbot_title: '💬 المساعد الذكي للسلامة',
    clear_chat: 'مسح المحادثة',
    chatbot_welcome: 'مرحباً بك في المساعد الذكي!',
    chatbot_help: 'أنا هنا لمساعدتك في كل ما يتعلق بالسلامة والصحة المهنية',
    quick_safety: 'إجراءات السلامة',
    quick_report: 'الإبلاغ عن حادثة',
    quick_iso: 'معايير ISO 45001',
    chat_placeholder: 'اكتب سؤالك هنا...',
    report_incident: 'الإبلاغ عن حادثة',
    all_incidents: 'كل الحوادث',
    critical: 'حرجة',
    high: 'عالية',
    medium: 'متوسطة',
    low: 'منخفضة',
    loading_incidents: 'جاري تحميل الحوادث...',
    new_risk: 'تقييم مخاطر جديد',
    loading_risks: 'جاري تحميل تقييمات المخاطر...',
    new_inspection: 'تفتيش جديد',
    loading_inspections: 'جاري تحميل التفتيشات...',
    new_report: 'توليد تقرير جديد',
    export_data: 'تصدير البيانات',
    available_reports: 'التقارير المتاحة',
    loading_reports: 'جاري تحميل التقارير...',
    no_incidents: 'لا توجد حوادث',
    no_detections: 'لا توجد كشوفات',
    no_cameras: 'لا توجد كاميرات',
    no_risks: 'لا توجد مخاطر',
    no_inspections: 'لا توجد تفتيشات',
    no_data: 'لا يوجد',
    chat_error: 'خطأ',
    risk_label: 'المخاطر',
    status_label: 'الحالة',
    residual_label: 'المتبقي',
    weekly_report: 'تقرير أسبوعي',
    generated: 'تم التوليد',
    camera_health: 'حالة الكاميرا',
    camera_name_prompt: 'اسم الكاميرا',
    incident_title_prompt: 'عنوان الحادثة',
    hazard_prompt: 'الخطر',
    add: 'إضافة',
    health: 'الحالة',
  },
  en: {
    app_title: 'Smart Safety | AI Safety Platform',
    logo_title: 'Hazm Tuwaiq',
    home: 'Home',
    loading: 'Loading...',
    connected: 'Connected',
    disconnected: 'Disconnected',
    retry_connection: 'Retry',
    nav_dashboard: 'Dashboard',
    nav_cameras: 'Cameras',
    nav_detection: 'Detection',
    nav_chatbot: 'AI Assistant',
    nav_incidents: 'Incidents',
    nav_risk: 'Risk Assessment',
    nav_inspections: 'Inspections',
    nav_reports: 'Reports',
    stat_cameras: 'Active Cameras',
    stat_detections: 'Detections Today',
    stat_incidents: 'Open Incidents',
    stat_chats: 'Conversations',
    recent_incidents: 'Recent Incidents',
    recent_detections: 'Recent Detections',
    view_all: 'View All',
    add_camera: 'Add New Camera',
    loading_cameras: 'Loading cameras...',
    upload_detection: 'Upload Image for Detection',
    upload_hint: 'Click or drag an image here',
    choose_image: 'Choose Image',
    detect_objects: 'Detect Objects',
    detection_history: 'Detection History',
    chatbot_title: '💬 AI Safety Assistant',
    clear_chat: 'Clear Chat',
    chatbot_welcome: 'Welcome to AI Assistant!',
    chatbot_help: 'I am here to help you with safety and occupational health topics.',
    quick_safety: 'Safety Procedures',
    quick_report: 'Report Incident',
    quick_iso: 'ISO 45001 Standards',
    chat_placeholder: 'Type your question here...',
    report_incident: 'Report Incident',
    all_incidents: 'All Incidents',
    critical: 'Critical',
    high: 'High',
    medium: 'Medium',
    low: 'Low',
    loading_incidents: 'Loading incidents...',
    new_risk: 'New Risk Assessment',
    loading_risks: 'Loading risk assessments...',
    new_inspection: 'New Inspection',
    loading_inspections: 'Loading inspections...',
    new_report: 'Generate New Report',
    export_data: 'Export Data',
    available_reports: 'Available Reports',
    loading_reports: 'Loading reports...',
    no_incidents: 'No incidents',
    no_detections: 'No detections',
    no_cameras: 'No cameras',
    no_risks: 'No risks',
    no_inspections: 'No inspections',
    no_data: 'No data',
    chat_error: 'Error',
    risk_label: 'Risk',
    status_label: 'Status',
    residual_label: 'Residual',
    weekly_report: 'Weekly Report',
    generated: 'Generated',
    camera_health: 'Camera health',
    camera_name_prompt: 'Camera name',
    incident_title_prompt: 'Incident title',
    hazard_prompt: 'Hazard',
    add: 'Add',
    health: 'Health',
  },
};

const PAGE_TITLE_KEYS = {
  dashboard: 'nav_dashboard',
  cameras: 'nav_cameras',
  detection: 'nav_detection',
  chatbot: 'nav_chatbot',
  incidents: 'nav_incidents',
  risk: 'nav_risk',
  inspections: 'nav_inspections',
  reports: 'nav_reports',
};

const I18N = {
  ar: {
    app_title: 'السلامة الذكية | Smart Safety - منصة الذكاء الاصطناعي للسلامة',
    logo_title: 'حزم طويق',
    home: 'الرئيسية',
    loading: 'جاري التحميل...',
    connected: 'متصل',
    nav_dashboard: 'لوحة التحكم',
    nav_cameras: 'الكاميرات',
    nav_detection: 'الكشف والقراءة',
    nav_chatbot: 'المساعد الذكي',
    nav_incidents: 'الحوادث',
    nav_risk: 'تقييم المخاطر',
    nav_inspections: 'التفتيش',
    nav_reports: 'التقارير',
    stat_cameras: 'الكاميرات النشطة',
    stat_detections: 'الكشوفات اليوم',
    stat_incidents: 'الحوادث المفتوحة',
    stat_chats: 'المحادثات',
    recent_incidents: 'الحوادث الأخيرة',
    recent_detections: 'الكشوفات الأخيرة',
    view_all: 'عرض الكل',
    add_camera: 'إضافة كاميرا جديدة',
    loading_cameras: 'جاري تحميل الكاميرات...',
    upload_detection: 'رفع صورة للكشف والقراءة',
    upload_hint: 'اضغط أو اسحب صورة هنا',
    choose_image: 'اختر صورة',
    detect_objects: 'كشف الأشياء',
    detection_history: 'سجل الكشوفات',
    chatbot_title: '💬 المساعد الذكي للسلامة',
    clear_chat: 'مسح المحادثة',
    chatbot_welcome: 'مرحباً بك في المساعد الذكي!',
    chatbot_help: 'أنا هنا لمساعدتك في كل ما يتعلق بالسلامة والصحة المهنية',
    quick_safety: 'إجراءات السلامة',
    quick_report: 'الإبلاغ عن حادثة',
    quick_iso: 'معايير ISO 45001',
    chat_placeholder: 'اكتب سؤالك هنا...',
    report_incident: 'الإبلاغ عن حادثة',
    all_incidents: 'كل الحوادث',
    critical: 'حرجة',
    high: 'عالية',
    medium: 'متوسطة',
    low: 'منخفضة',
    loading_incidents: 'جاري تحميل الحوادث...',
    new_risk: 'تقييم مخاطر جديد',
    loading_risks: 'جاري تحميل تقييمات المخاطر...',
    new_inspection: 'تفتيش جديد',
    loading_inspections: 'جاري تحميل التفتيشات...',
    new_report: 'توليد تقرير جديد',
    export_data: 'تصدير البيانات',
    available_reports: 'التقارير المتاحة',
    loading_reports: 'جاري تحميل التقارير...',
    no_incidents: 'لا توجد حوادث',
    no_detections: 'لا توجد كشوفات',
    no_cameras: 'لا توجد كاميرات',
    no_risks: 'لا توجد مخاطر',
    no_inspections: 'لا توجد تفتيشات',
    no_data: 'لا يوجد',
    chat_error: 'خطأ',
    risk_label: 'المخاطر',
    status_label: 'الحالة',
    residual_label: 'المتبقي',
    weekly_report: 'تقرير أسبوعي',
    generated: 'تم التوليد',
    camera_health: 'حالة الكاميرا',
    camera_name_prompt: 'اسم الكاميرا',
    incident_title_prompt: 'عنوان الحادثة',
    hazard_prompt: 'الخطر',
    add: 'إضافة',
    health: 'الحالة',
  },
  en: {
    app_title: 'Smart Safety | AI Safety Platform',
    logo_title: 'Hazm Tuwaiq',
    home: 'Home',
    loading: 'Loading...',
    connected: 'Connected',
    nav_dashboard: 'Dashboard',
    nav_cameras: 'Cameras',
    nav_detection: 'Detection',
    nav_chatbot: 'AI Assistant',
    nav_incidents: 'Incidents',
    nav_risk: 'Risk Assessment',
    nav_inspections: 'Inspections',
    nav_reports: 'Reports',
    stat_cameras: 'Active Cameras',
    stat_detections: 'Detections Today',
    stat_incidents: 'Open Incidents',
    stat_chats: 'Conversations',
    recent_incidents: 'Recent Incidents',
    recent_detections: 'Recent Detections',
    view_all: 'View All',
    add_camera: 'Add New Camera',
    loading_cameras: 'Loading cameras...',
    upload_detection: 'Upload Image for Detection',
    upload_hint: 'Click or drag an image here',
    choose_image: 'Choose Image',
    detect_objects: 'Detect Objects',
    detection_history: 'Detection History',
    chatbot_title: '💬 AI Safety Assistant',
    clear_chat: 'Clear Chat',
    chatbot_welcome: 'Welcome to AI Assistant!',
    chatbot_help: 'I am here to help you with safety and occupational health topics.',
    quick_safety: 'Safety Procedures',
    quick_report: 'Report Incident',
    quick_iso: 'ISO 45001 Standards',
    chat_placeholder: 'Type your question here...',
    report_incident: 'Report Incident',
    all_incidents: 'All Incidents',
    critical: 'Critical',
    high: 'High',
    medium: 'Medium',
    low: 'Low',
    loading_incidents: 'Loading incidents...',
    new_risk: 'New Risk Assessment',
    loading_risks: 'Loading risk assessments...',
    new_inspection: 'New Inspection',
    loading_inspections: 'Loading inspections...',
    new_report: 'Generate New Report',
    export_data: 'Export Data',
    available_reports: 'Available Reports',
    loading_reports: 'Loading reports...',
    no_incidents: 'No incidents',
    no_detections: 'No detections',
    no_cameras: 'No cameras',
    no_risks: 'No risks',
    no_inspections: 'No inspections',
    no_data: 'No data',
    chat_error: 'Error',
    risk_label: 'Risk',
    status_label: 'Status',
    residual_label: 'Residual',
    weekly_report: 'Weekly Report',
    generated: 'Generated',
    camera_health: 'Camera health',
    camera_name_prompt: 'Camera name',
    incident_title_prompt: 'Incident title',
    hazard_prompt: 'Hazard',
    add: 'Add',
    health: 'Health',
  },
};

const PAGE_TITLE_KEYS = {
  dashboard: 'nav_dashboard',
  cameras: 'nav_cameras',
  detection: 'nav_detection',
  chatbot: 'nav_chatbot',
  incidents: 'nav_incidents',
  risk: 'nav_risk',
  inspections: 'nav_inspections',
  reports: 'nav_reports',
};

const state = {
  theme: localStorage.getItem('theme') || 'light',
  language: localStorage.getItem('language') || 'ar',
  currentPage: 'dashboard',
  chatHistory: JSON.parse(localStorage.getItem('chatHistory') || '[]'),
  token: localStorage.getItem('token') || null,
};

let healthIntervalId = null;
function t(key) {
  return I18N[state.language]?.[key] || I18N.ar[key] || key;
}

function setText(selector, key) {
  const el = document.querySelector(selector);
  if (el) el.textContent = t(key);
}

function applyTranslations() {
  document.title = t('app_title');
  document.documentElement.lang = state.language;
  document.documentElement.dir = state.language === 'ar' ? 'rtl' : 'ltr';
  document.getElementById('langText').textContent = state.language === 'ar' ? 'EN' : 'عر';

  setText('.logo-text', 'logo_title');
  setText('.breadcrumb span:first-child', 'home');
setText('#systemStatus span:last-child', 'loading');

  setText('[data-page="dashboard"] .nav-text', 'nav_dashboard');
  setText('[data-page="cameras"] .nav-text', 'nav_cameras');
  setText('[data-page="detection"] .nav-text', 'nav_detection');
  setText('[data-page="chatbot"] .nav-text', 'nav_chatbot');
  setText('[data-page="incidents"] .nav-text', 'nav_incidents');
  setText('[data-page="risk"] .nav-text', 'nav_risk');
  setText('[data-page="inspections"] .nav-text', 'nav_inspections');
  setText('[data-page="reports"] .nav-text', 'nav_reports');

  setText('.stats-grid .stat-card:nth-child(1) p', 'stat_cameras');
  setText('.stats-grid .stat-card:nth-child(2) p', 'stat_detections');
  setText('.stats-grid .stat-card:nth-child(3) p', 'stat_incidents');
  setText('.stats-grid .stat-card:nth-child(4) p', 'stat_chats');

  setText('#dashboardPage .dashboard-grid .card:nth-child(1) .card-header h3', 'recent_incidents');
  setText('#dashboardPage .dashboard-grid .card:nth-child(1) .card-header .btn-link', 'view_all');
  setText('#dashboardPage .dashboard-grid .card:nth-child(2) .card-header h3', 'recent_detections');
  setText('#dashboardPage .dashboard-grid .card:nth-child(2) .card-header .btn-link', 'view_all');

  const addCameraBtn = document.querySelector('#camerasPage .page-actions .btn');
  if (addCameraBtn) addCameraBtn.innerHTML = `<span>➕</span> ${t('add_camera')}`;
  setText('#camerasPage .loading', 'loading_cameras');
  setText('#detectionPage .card:nth-child(1) .card-header h3', 'upload_detection');
  setText('#uploadArea .upload-content p', 'upload_hint');
  setText('#uploadArea .upload-content .btn', 'choose_image');
  setText('#detectBtn', 'detect_objects');
  setText('#detectionPage .card:nth-child(2) .card-header h3', 'detection_history');

  setText('#chatbotPage .chat-header h3', 'chatbot_title');
  setText('#chatbotPage .chat-header .btn-link', 'clear_chat');
  setText('#chatInput', 'chat_placeholder');
  const chatInput = document.getElementById('chatInput');
  if (chatInput) chatInput.placeholder = t('chat_placeholder');

  const reportIncidentBtn = document.querySelector('#incidentsPage .page-actions .btn');
  if (reportIncidentBtn) reportIncidentBtn.innerHTML = `<span>➕</span> ${t('report_incident')}`;
  setText('#severityFilter option[value=""]', 'all_incidents');
  setText('#severityFilter option[value="critical"]', 'critical');
  setText('#severityFilter option[value="high"]', 'high');
  setText('#severityFilter option[value="medium"]', 'medium');
  setText('#severityFilter option[value="low"]', 'low');

  const newRiskBtn = document.querySelector('#riskPage .page-actions .btn');
  if (newRiskBtn) newRiskBtn.innerHTML = `<span>➕</span> ${t('new_risk')}`;
  const newInspectionBtn = document.querySelector('#inspectionsPage .page-actions .btn');
  if (newInspectionBtn) newInspectionBtn.innerHTML = `<span>➕</span> ${t('new_inspection')}`;
  const reportBtn = document.querySelector('#reportsPage .page-actions .btn.btn-primary');
  if (reportBtn) reportBtn.innerHTML = `<span>📄</span> ${t('new_report')}`;
  const exportBtn = document.querySelector('#reportsPage .page-actions .btn.btn-secondary');
  if (exportBtn) exportBtn.innerHTML = `<span>📊</span> ${t('export_data')}`;
  setText('#reportsPage .card-header h3', 'available_reports');

  updatePageTitle();
  loadChatHistory();
}

function updatePageTitle() {
  const key = PAGE_TITLE_KEYS[state.currentPage] || 'nav_dashboard';
  document.getElementById('pageTitle').textContent = t(key);
  document.getElementById('breadcrumbPage').textContent = t(key);
}

function updateSystemStatus(isConnected, errorMessage = '') {
  const b = document.getElementById('systemStatus');
  if (!b) return;

  if (isConnected) {
    b.classList.remove('is-disconnected');
    b.innerHTML = `<span class="status-dot"></span><span>${t('connected')}</span>`;
    return;
  }

  b.classList.add('is-disconnected');

  const details = errorMessage
    ? `<small class="status-error">${errorMessage}</small>`
    : '';

  b.innerHTML = `
    <span class="status-dot"></span>
    <span>${t('disconnected')}</span>
    <button class="status-retry" id="retryConnectionBtn">
      ${t('retry_connection')}
    </button>
    ${details}
  `;

  document
    .getElementById('retryConnectionBtn')
    ?.addEventListener('click', () => pingHealth(true));
}

async function pingHealth(showError = false) {
  try {
    const response = await fetch(`${CONFIG.API_BASE_URL}/health`, {
      headers: { Accept: 'application/json' }
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok || data.status !== 'ok')
      throw new Error(`HTTP ${response.status}`);

    updateSystemStatus(true);

  } catch (e) {
    updateSystemStatus(false, showError ? e.message : '');
  }
}

function startHealthMonitor() {
  if (healthIntervalId) clearInterval(healthIntervalId);

  pingHealth();
  healthIntervalId = setInterval(() => pingHealth(), 10000);
}
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
  updatePageTitle();
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
    document.getElementById('recentIncidents').innerHTML = (data.last_incidents || []).map(x => `<div class="incident-item"><strong>${x.title}</strong><small>${x.created_at || ''}</small></div>`).join('') || `<div class="loading">${t('no_incidents')}</div>`;
    document.getElementById('recentDetections').innerHTML = (data.last_detections || []).map(x => `<div class="incident-item"><strong>${x.event_type}</strong><small>${x.created_at || ''}</small></div>`).join('') || `<div class="loading">${t('no_detections')}</div>`;
updateSystemStatus(true);
  } catch (e) { showError('recentIncidents', e); showError('recentDetections', e); }
}

async function loadCameras() {
  const el = document.getElementById('camerasGrid');
  try {
    const cams = await apiFetch('/cameras');
    el.innerHTML = cams.map(c => `<div class="camera-card"><h4>${c.name}</h4><p>${c.site} - ${c.location}</p><p>${t('status_label')}: <strong>${c.status}</strong></p><button class="btn btn-secondary" onclick="checkCameraHealth(${c.id})">${t('health')}</button></div>`).join('') || `<div class="loading">${t('no_cameras')}</div>`;
  } catch (e) { showError('camerasGrid', e); }
}

async function checkCameraHealth(id){
  try{ const h = await apiFetch(`/cameras/${id}/health`); alert(`${t('camera_health')} ${id}: ${h.status}`);}catch(e){alert(e.message)}
}

function showAddCameraModal() {
  const name = prompt(t('camera_name_prompt')); if (!name) return;
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
    document.getElementById('detectionHistory').innerHTML = rows.map(r=>`<div class="incident-item"><strong>${r.event_type}</strong><small>${r.created_at}</small></div>`).join('') || `<div class="loading">${t('no_data')}</div>`;
  } catch(e){ showError('detectionHistory', e); }
}

function loadChatHistory(){
  const el = document.getElementById('chatMessages');
  const q1 = state.language === 'ar' ? 'ما هي إجراءات السلامة الأساسية؟' : 'What are the basic safety procedures?';
  const q2 = state.language === 'ar' ? 'كيف أبلغ عن حادثة؟' : 'How do I report an incident?';
  const q3 = state.language === 'ar' ? 'ما هي معايير ISO 45001؟' : 'What are ISO 45001 standards?';
  const base = `<div class="chat-welcome"><h4>${t('chatbot_welcome')}</h4><p>${t('chatbot_help')}</p><div class="quick-questions"><button class="quick-btn" onclick="sendQuickQuestion('${q1.replace(/'/g, "\\'")}')">${t('quick_safety')}</button><button class="quick-btn" onclick="sendQuickQuestion('${q2.replace(/'/g, "\\'")}')">${t('quick_report')}</button><button class="quick-btn" onclick="sendQuickQuestion('${q3.replace(/'/g, "\\'")}')">${t('quick_iso')}</button></div></div>`;
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
    state.chatHistory.push({ role:'bot', text: `${t('chat_error')}: ${e.message}` });
  }
  localStorage.setItem('chatHistory', JSON.stringify(state.chatHistory));
  loadChatHistory();
}

async function loadIncidents(){
  try{ const rows = await apiFetch('/incidents');
    document.getElementById('incidentsList').innerHTML = rows.map(i=>`<div class="card" style="margin-bottom:1rem"><div class="card-body"><h4>${i.title}</h4><p>${t('risk_label')}: ${i.risk_score}</p><small>${i.status}</small></div></div>`).join('') || `<div class="loading">${t('no_incidents')}</div>`;
  } catch(e){ showError('incidentsList', e); }
}

function showAddIncidentModal(){
  const title = prompt(t('incident_title_prompt')); if(!title) return;
  apiFetch('/incidents', {method:'POST', body: JSON.stringify({ title, description:'Demo', site:'Plant-1', department:'Operations', severity:3, likelihood:3, status:'open' })}).then(loadIncidents).catch(e=>alert(e.message));
}

async function loadRisks(){
  try{ const rows = await apiFetch('/risks');
    document.getElementById('riskList').innerHTML = rows.map(r=>`<div class="card" style="margin-bottom:1rem"><div class="card-body"><h4>${r.hazard}</h4><p>${t('residual_label')}: ${r.residual_risk}</p><small>${r.site}</small></div></div>`).join('') || `<div class="loading">${t('no_risks')}</div>`;
  }catch(e){ showError('riskList', e); }
}

function showAddRiskModal(){
  const hazard=prompt(t('hazard_prompt')); if(!hazard) return;
  apiFetch('/risks',{method:'POST',body:JSON.stringify({hazard,site:'Plant-1',department:'Operations',controls:'PPE',severity:4,likelihood:3})}).then(loadRisks).catch(e=>alert(e.message));
}

async function loadInspections(){
  try{ const rows = await apiFetch('/inspections');
    document.getElementById('inspectionsList').innerHTML = rows.map(i=>`<div class="card" style="margin-bottom:1rem"><div class="card-body"><h4>${i.site} - ${i.department}</h4><p>${t('status_label')}: ${i.status}</p><small>${i.scheduled_date}</small></div></div>`).join('') || `<div class="loading">${t('no_inspections')}</div>`;
  }catch(e){ showError('inspectionsList', e); }
}

function showAddInspectionModal(){
  apiFetch('/inspections',{method:'POST',body:JSON.stringify({site:'Plant-1',department:'Operations',template_id:1,scheduled_date:new Date().toISOString().slice(0,10)})}).then(loadInspections).catch(e=>alert(e.message));
}

async function loadReports(){
  try { const data = await apiFetch('/reports/weekly');
    document.getElementById('reportsList').innerHTML = `<div class="card"><div class="card-body"><h4>${t('weekly_report')}</h4><pre>${JSON.stringify(data,null,2)}</pre></div></div>`;
  } catch(e){ showError('reportsList', e); }
}

async function generateReport(){
  try { const data = await apiFetch('/reports/export?type=weekly'); alert(`${t('generated')}: ${data.filename}`); } catch(e){ alert(e.message); }
}
async function exportReports(){ return generateReport(); }

function toggleTheme(){ state.theme = state.theme==='light'?'dark':'light'; document.body.classList.toggle('dark-theme'); localStorage.setItem('theme',state.theme); document.getElementById('themeIcon').textContent = state.theme==='dark'?'☀️':'🌙'; }
function toggleLanguage(){ state.language = state.language==='ar'?'en':'ar'; localStorage.setItem('language',state.language); applyTranslations(); updatePageTitle(); }

document.addEventListener('DOMContentLoaded', async () => {
  if (state.theme==='dark'){ document.body.classList.add('dark-theme'); document.getElementById('themeIcon').textContent='☀️'; }
  document.querySelectorAll('.nav-item').forEach(nav => nav.addEventListener('click', e => { e.preventDefault(); navigateTo(nav.getAttribute('data-page')); }));
  document.getElementById('themeToggle')?.addEventListener('click', toggleTheme);
  document.getElementById('langToggle')?.addEventListener('click', toggleLanguage);
  document.getElementById('chatInput')?.addEventListener('keypress', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChat(); } });
  setupDetectionUpload();
  applyTranslations();
startHealthMonitor();
  await ensureLogin();
  loadPageData('dashboard');
});
