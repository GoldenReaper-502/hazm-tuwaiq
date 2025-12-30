/**
 * HAZM TUWAIQ - Golden Edition Frontend
 * Complete application logic for all modules
 */

// ==========================================
// Configuration
// ==========================================
const CONFIG = {
  API_BASE_URL: 'https://hazm-tuwaiq-3.onrender.com',
  // API_BASE_URL: 'http://localhost:8000',  // للتطوير المحلي
};

// ==========================================
// State Management
// ==========================================
const state = {
  theme: localStorage.getItem('theme') || 'light',
  language: localStorage.getItem('language') || 'ar',
  chatHistory: JSON.parse(localStorage.getItem('chatHistory') || '[]'),
  lastDetection: JSON.parse(localStorage.getItem('lastDetection') || 'null'),
  sessionId: localStorage.getItem('sessionId') || `session_${Date.now()}`,
};

// ==========================================
// i18n Dictionary
// ==========================================
const i18n = {
  ar: {
    appTitle: 'حزم طويق',
    systemStatus: 'حالة النظام',
    cctvManagement: 'إدارة الكاميرات',
    objectDetection: 'كشف الأشياء',
    alertsIncidents: 'التنبيهات والحوادث',
    reports: 'التقارير',
    adminPanel: 'لوحة الإدارة',
    chat: 'الدردشة مع السلامة الذكية',
    online: 'متصل',
    offline: 'غير متصل',
    unknown: 'غير معروف',
    checkStatus: 'فحص الحالة',
    listCameras: 'قائمة الكاميرات',
    addCamera: 'إضافة كاميرا',
    uploadImage: 'رفع صورة',
    detectObjects: 'كشف الأشياء',
    viewAlerts: 'عرض التنبيهات',
    reportIncident: 'الإبلاغ عن حادثة',
    generateReport: 'توليد تقرير',
    exportData: 'تصدير البيانات',
    manageUsers: 'إدارة المستخدمين',
    createRole: 'إنشاء دور',
    sendMessage: 'إرسال رسالة',
    darkMode: 'الوضع الداكن',
    lightMode: 'الوضع الفاتح',
    english: 'English',
    arabic: 'العربية',
    loading: 'جاري التحميل...',
    error: 'خطأ',
    success: 'نجح',
    noData: 'لا توجد بيانات',
  },
  en: {
    appTitle: 'Hazm Tuwaiq',
    systemStatus: 'System Status',
    cctvManagement: 'CCTV Management',
    objectDetection: 'Object Detection',
    alertsIncidents: 'Alerts & Incidents',
    reports: 'Reports',
    adminPanel: 'Admin Panel',
    chat: 'Safety Copilot Chat',
    online: 'Online',
    offline: 'Offline',
    unknown: 'Unknown',
    checkStatus: 'Check Status',
    listCameras: 'List Cameras',
    addCamera: 'Add Camera',
    uploadImage: 'Upload Image',
    detectObjects: 'Detect Objects',
    viewAlerts: 'View Alerts',
    reportIncident: 'Report Incident',
    generateReport: 'Generate Report',
    exportData: 'Export Data',
    manageUsers: 'Manage Users',
    createRole: 'Create Role',
    sendMessage: 'Send Message',
    darkMode: 'Dark Mode',
    lightMode: 'Light Mode',
    english: 'English',
    arabic: 'العربية',
    loading: 'Loading...',
    error: 'Error',
    success: 'Success',
    noData: 'No data available',
  }
};

// ==========================================
// Safe API Fetch
// ==========================================
async function apiFetch(endpoint, options = {}) {
  try {
    const url = CONFIG.API_BASE_URL + endpoint;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });

    const text = await response.text();
    const contentType = response.headers.get('content-type');

    if (contentType && contentType.includes('application/json')) {
      const data = JSON.parse(text);
      if (!response.ok) {
        throw new Error(data.detail || data.message || `HTTP ${response.status}`);
      }
      return data;
    } else {
      throw new Error(`Expected JSON but got: ${text.slice(0, 100)}`);
    }
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

// ==========================================
// Module Functions
// ==========================================

// 1. System Status
async function checkSystemStatus() {
  const output = document.getElementById('status-output');
  output.innerHTML = '<div class="loading">جاري الفحص...</div>';
  
  try {
    const data = await apiFetch('/system/status');
    
    const llmStatus = data.llm_available 
      ? '<span class="status-online">✅ متصل</span>' 
      : `<span class="status-offline">❌ غير متصل (${data.llm_error || 'غير معروف'})</span>`;
    
    const cctvStatus = data.cctv_available 
      ? '<span class="status-online">✅ متصل</span>' 
      : `<span class="status-offline">❌ غير متصل (${data.cctv_error || 'غير معروف'})</span>`;
    
    output.innerHTML = `
      <div class="status-card">
        <h4>حالة النظام</h4>
        <p><strong>LLM:</strong> ${llmStatus}</p>
        <p><strong>CCTV:</strong> ${cctvStatus}</p>
        <p><strong>الوقت:</strong> ${data.timestamp}</p>
      </div>
    `;
  } catch (error) {
    output.innerHTML = `<div class="error">خطأ: ${error.message}</div>`;
  }
}

// 2. CCTV Cameras
async function listCameras() {
  const output = document.getElementById('cctv-output');
  output.innerHTML = '<div class="loading">جاري التحميل...</div>';
  
  try {
    const data = await apiFetch('/cctv/cameras');
    
    if (!data || data.length === 0) {
      output.innerHTML = '<div class="no-data">لا توجد كاميرات</div>';
      return;
    }
    
    const cameraList = data.map(cam => `
      <div class="camera-item">
        <strong>${cam.name || cam.id}</strong>
        <span class="${cam.enabled ? 'status-online' : 'status-offline'}">
          ${cam.enabled ? '🟢 مفعّل' : '🔴 معطّل'}
        </span>
      </div>
    `).join('');
    
    output.innerHTML = cameraList;
  } catch (error) {
    output.innerHTML = `<div class="error">خطأ: ${error.message}</div>`;
  }
}

async function addCamera() {
  const name = prompt('اسم الكاميرا:');
  const url = prompt('رابط RTSP:');
  
  if (!name || !url) return;
  
  const output = document.getElementById('cctv-output');
  output.innerHTML = '<div class="loading">جاري الإضافة...</div>';
  
  try {
    await apiFetch('/cctv/cameras', {
      method: 'POST',
      body: JSON.stringify({ name, url })
    });
    
    output.innerHTML = '<div class="success">✅ تمت الإضافة بنجاح</div>';
    setTimeout(listCameras, 1000);
  } catch (error) {
    output.innerHTML = `<div class="error">خطأ: ${error.message}</div>`;
  }
}

// 3. Object Detection
async function detectObjects() {
  const fileInput = document.getElementById('detection-file');
  const output = document.getElementById('detection-output');
  
  if (!fileInput.files || fileInput.files.length === 0) {
    output.innerHTML = '<div class="error">الرجاء اختيار صورة</div>';
    return;
  }
  
  const file = fileInput.files[0];
  output.innerHTML = '<div class="loading">جاري الكشف...</div>';
  
  try {
    // تحويل الصورة إلى base64
    const base64 = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result.split(',')[1]);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
    
    const data = await apiFetch('/detect', {
      method: 'POST',
      body: JSON.stringify({
        frame_data: base64,
        timestamp: new Date().toISOString()
      })
    });
    
    state.lastDetection = data;
    localStorage.setItem('lastDetection', JSON.stringify(data));
    
    const objects = data.objects || [];
    if (objects.length === 0) {
      output.innerHTML = '<div class="no-data">لم يتم اكتشاف أي أشياء</div>';
      return;
    }
    
    const objectList = objects.map(obj => `
      <div class="detection-item">
        <strong>${obj.label || obj.class}</strong>
        <span>الثقة: ${(obj.confidence * 100).toFixed(1)}%</span>
      </div>
    `).join('');
    
    output.innerHTML = `
      <div class="detection-result">
        <h4>النتائج (${objects.length} أشياء)</h4>
        ${objectList}
      </div>
    `;
  } catch (error) {
    output.innerHTML = `<div class="error">خطأ: ${error.message}</div>`;
  }
}

// 4. Alerts & Incidents
async function loadAlerts() {
  const output = document.getElementById('alerts-output');
  output.innerHTML = '<div class="loading">جاري التحميل...</div>';
  
  try {
    const data = await apiFetch('/alerts');
    
    if (!data || data.length === 0) {
      output.innerHTML = '<div class="no-data">لا توجد تنبيهات</div>';
      return;
    }
    
    const alertList = data.slice(0, 10).map(alert => `
      <div class="alert-item ${alert.severity}">
        <strong>${alert.type || 'تنبيه'}</strong>
        <p>${alert.message || 'لا يوجد وصف'}</p>
        <small>${alert.timestamp || ''}</small>
        ${!alert.acknowledged ? '<button onclick="acknowledgeAlert(\'' + alert.id + '\')">تأكيد</button>' : ''}
      </div>
    `).join('');
    
    output.innerHTML = alertList;
  } catch (error) {
    output.innerHTML = `<div class="error">خطأ: ${error.message}</div>`;
  }
}

async function acknowledgeAlert(alertId) {
  try {
    await apiFetch(`/alerts/ack/${alertId}`, { method: 'POST' });
    loadAlerts();
  } catch (error) {
    alert(`خطأ: ${error.message}`);
  }
}

async function submitIncident() {
  const title = prompt('عنوان الحادثة:');
  const description = prompt('الوصف:');
  
  if (!title || !description) return;
  
  const output = document.getElementById('alerts-output');
  output.innerHTML = '<div class="loading">جاري الإرسال...</div>';
  
  try {
    await apiFetch('/incidents', {
      method: 'POST',
      body: JSON.stringify({
        title,
        description,
        severity: 'medium',
        timestamp: new Date().toISOString()
      })
    });
    
    output.innerHTML = '<div class="success">✅ تم الإبلاغ بنجاح</div>';
    setTimeout(loadAlerts, 1000);
  } catch (error) {
    output.innerHTML = `<div class="error">خطأ: ${error.message}</div>`;
  }
}

async function submitNearMiss() {
  const description = prompt('وصف الحادث القريب:');
  
  if (!description) return;
  
  const output = document.getElementById('alerts-output');
  output.innerHTML = '<div class="loading">جاري الإرسال...</div>';
  
  try {
    await apiFetch('/near-miss', {
      method: 'POST',
      body: JSON.stringify({
        description,
        timestamp: new Date().toISOString()
      })
    });
    
    output.innerHTML = '<div class="success">✅ تم الإبلاغ بنجاح</div>';
  } catch (error) {
    output.innerHTML = `<div class="error">خطأ: ${error.message}</div>`;
  }
}

// 5. Reports
async function generateReport() {
  const output = document.getElementById('reports-output');
  output.innerHTML = '<div class="loading">جاري التوليد...</div>';
  
  try {
    const response = await fetch(CONFIG.API_BASE_URL + '/export/pdf', {
      method: 'GET',
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report_${Date.now()}.pdf`;
    a.click();
    
    output.innerHTML = '<div class="success">✅ تم التحميل</div>';
  } catch (error) {
    output.innerHTML = `<div class="error">خطأ: ${error.message}</div>`;
  }
}

async function exportExcel() {
  const output = document.getElementById('reports-output');
  output.innerHTML = '<div class="loading">جاري التصدير...</div>';
  
  try {
    const response = await fetch(CONFIG.API_BASE_URL + '/export/excel', {
      method: 'GET',
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `data_${Date.now()}.xlsx`;
    a.click();
    
    output.innerHTML = '<div class="success">✅ تم التصدير</div>';
  } catch (error) {
    output.innerHTML = `<div class="error">خطأ: ${error.message}</div>`;
  }
}

// 6. Admin Panel
async function createRole() {
  const roleName = prompt('اسم الدور:');
  const permissions = prompt('الصلاحيات (مفصولة بفواصل):');
  
  if (!roleName || !permissions) return;
  
  const output = document.getElementById('admin-output');
  output.innerHTML = '<div class="loading">جاري الإنشاء...</div>';
  
  try {
    await apiFetch('/admin/roles', {
      method: 'POST',
      body: JSON.stringify({
        name: roleName,
        permissions: permissions.split(',').map(p => p.trim())
      })
    });
    
    output.innerHTML = '<div class="success">✅ تم الإنشاء بنجاح</div>';
  } catch (error) {
    output.innerHTML = `<div class="error">خطأ: ${error.message}</div>`;
  }
}

// 7. Chat
async function sendChat() {
  const input = document.getElementById('chat-input');
  const output = document.getElementById('chat-output');
  const message = input.value.trim();
  
  if (!message) return;
  
  // عرض رسالة المستخدم
  const userBubble = document.createElement('div');
  userBubble.className = 'chat-bubble user-bubble';
  userBubble.textContent = message;
  output.appendChild(userBubble);
  
  // حفظ في التاريخ
  state.chatHistory.push({ role: 'user', content: message });
  localStorage.setItem('chatHistory', JSON.stringify(state.chatHistory));
  
  input.value = '';
  output.scrollTop = output.scrollHeight;
  
  // عرض مؤشر التحميل
  const loadingBubble = document.createElement('div');
  loadingBubble.className = 'chat-bubble assistant-bubble loading';
  loadingBubble.textContent = 'جاري التفكير...';
  output.appendChild(loadingBubble);
  output.scrollTop = output.scrollHeight;
  
  try {
    const data = await apiFetch('/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        session_id: state.sessionId,
        detection_result: state.lastDetection
      })
    });
    
    // إزالة مؤشر التحميل
    loadingBubble.remove();
    
    // عرض رد المساعد
    const assistantBubble = document.createElement('div');
    assistantBubble.className = 'chat-bubble assistant-bubble';
    assistantBubble.textContent = data.assistant_response || data.message || 'لا يوجد رد';
    output.appendChild(assistantBubble);
    
    // حفظ في التاريخ
    state.chatHistory.push({ role: 'assistant', content: data.assistant_response || data.message });
    localStorage.setItem('chatHistory', JSON.stringify(state.chatHistory));
    
    output.scrollTop = output.scrollHeight;
  } catch (error) {
    loadingBubble.remove();
    
    const errorBubble = document.createElement('div');
    errorBubble.className = 'chat-bubble assistant-bubble error';
    errorBubble.textContent = `خطأ: ${error.message}`;
    output.appendChild(errorBubble);
    
    output.scrollTop = output.scrollHeight;
  }
}

// ==========================================
// Theme & Language Toggle
// ==========================================
function toggleTheme() {
  state.theme = state.theme === 'light' ? 'dark' : 'light';
  document.body.classList.toggle('dark-theme');
  localStorage.setItem('theme', state.theme);
  
  const btn = document.getElementById('theme-toggle');
  btn.textContent = state.theme === 'dark' ? '☀️' : '🌙';
}

function toggleLanguage() {
  state.language = state.language === 'ar' ? 'en' : 'ar';
  localStorage.setItem('language', state.language);
  updateLanguage();
}

function updateLanguage() {
  const lang = state.language;
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
  
  // تحديث جميع النصوص
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (i18n[lang][key]) {
      el.textContent = i18n[lang][key];
    }
  });
  
  const langBtn = document.getElementById('lang-toggle');
  langBtn.textContent = lang === 'ar' ? 'EN' : 'عر';
}

// ==========================================
// Initialization
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  // تطبيق Theme المحفوظ
  if (state.theme === 'dark') {
    document.body.classList.add('dark-theme');
    document.getElementById('theme-toggle').textContent = '☀️';
  }
  
  // تطبيق اللغة المحفوظة
  updateLanguage();
  
  // استعادة تاريخ الدردشة
  const chatOutput = document.getElementById('chat-output');
  if (chatOutput && state.chatHistory.length > 0) {
    state.chatHistory.forEach(msg => {
      const bubble = document.createElement('div');
      bubble.className = `chat-bubble ${msg.role === 'user' ? 'user-bubble' : 'assistant-bubble'}`;
      bubble.textContent = msg.content;
      chatOutput.appendChild(bubble);
    });
    chatOutput.scrollTop = chatOutput.scrollHeight;
  }
  
  // فحص الحالة التلقائي
  checkSystemStatus();
  
  console.log('✅ HAZM TUWAIQ Golden Edition loaded');
});

// تصدير الوظائف للاستخدام العام
window.checkSystemStatus = checkSystemStatus;
window.listCameras = listCameras;
window.addCamera = addCamera;
window.detectObjects = detectObjects;
window.loadAlerts = loadAlerts;
window.acknowledgeAlert = acknowledgeAlert;
window.submitIncident = submitIncident;
window.submitNearMiss = submitNearMiss;
window.generateReport = generateReport;
window.exportExcel = exportExcel;
window.createRole = createRole;
window.sendChat = sendChat;
window.toggleTheme = toggleTheme;
window.toggleLanguage = toggleLanguage;
