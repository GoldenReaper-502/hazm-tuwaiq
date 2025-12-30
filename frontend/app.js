// ===========================================
// HAZM TUWAIQ - Complete Application Logic
// ===========================================

const CONFIG = {
    API_BASE_URL: 'http://localhost:5000/api', // ASP.NET Core Backend
    // API_BASE_URL: 'https://hazm-tuwaiq-3.onrender.com', // Python Backend (Old)
};

const state = {
    theme: localStorage.getItem('theme') || 'light',
    language: localStorage.getItem('language') || 'ar',
    currentPage: 'dashboard',
    chatHistory: JSON.parse(localStorage.getItem('chatHistory') || '[]'),
    sessionId: localStorage.getItem('sessionId') || `session_${Date.now()}`,
};

// ===========================================
// Safe API Fetch - Production Ready
// ===========================================
async function apiFetch(endpoint, options = {}) {
    try {
        const url = CONFIG.API_BASE_URL + endpoint;
        const response = await fetch(url, {
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            ...options
        });
        
        // Get content type
        const contentType = response.headers.get('content-type') || '';
        
        // Validate JSON response
        if (!contentType.includes('application/json') && 
            !contentType.includes('application/problem+json')) {
            const text = await response.text();
            throw new Error(`Expected JSON but got ${contentType}: ${text.slice(0, 100)}`);
        }
        
        // Parse JSON
        const text = await response.text();
        let data;
        try {
            data = JSON.parse(text);
        } catch (e) {
            throw new Error(`Invalid JSON response: ${text.slice(0, 100)}`);
        }
        
        // Handle errors
        if (!response.ok) {
            const errorMessage = data.detail || data.title || data.message || `HTTP ${response.status}`;
            throw new Error(errorMessage);
        }
        
        return data;
    } catch (error) {
        console.error(`API Error [${endpoint}]:`, error);
        throw error;
    }
}

// ===========================================
// Navigation
// ===========================================
function navigateTo(pageName) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    
    // Show selected page
    const page = document.getElementById(pageName + 'Page');
    if (page) {
        page.classList.add('active');
        state.currentPage = pageName;
        
        // Update nav items
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        const activeNav = document.querySelector(`[data-page="${pageName}"]`);
        if (activeNav) activeNav.classList.add('active');
        
        // Update page title
        const titles = {
            dashboard: 'لوحة التحكم',
            cameras: 'الكاميرات',
            detection: 'الكشف والقراءة',
            chatbot: 'المساعد الذكي',
            incidents: 'الحوادث',
            risk: 'تقييم المخاطر',
            inspections: 'التفتيش',
            reports: 'التقارير'
        };
        document.getElementById('pageTitle').textContent = titles[pageName] || pageName;
        document.getElementById('breadcrumbPage').textContent = titles[pageName] || pageName;
        
        // Load page data
        loadPageData(pageName);
    }
}

function loadPageData(pageName) {
    switch(pageName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'cameras':
            loadCameras();
            break;
        case 'detection':
            loadDetectionHistory();
            break;
        case 'chatbot':
            loadChatHistory();
            break;
        case 'incidents':
            loadIncidents();
            break;
        case 'risk':
            loadRiskAssessments();
            break;
        case 'inspections':
            loadInspections();
            break;
        case 'reports':
            loadReports();
            break;
    }
}

// ===========================================
// Dashboard Functions
// ===========================================
async function loadDashboard() {
    try {
        // Load stats
        const [cameras, detections, incidents] = await Promise.all([
            apiFetch('/cctv/cameras').catch(() => []),
            apiFetch('/detections').catch(() => []),
            apiFetch('/incidents').catch(() => [])
        ]);
        
        document.getElementById('camerasCount').textContent = cameras.length || '0';
        document.getElementById('detectionsCount').textContent = detections.length || '0';
        document.getElementById('incidentsCount').textContent = incidents.filter(i => i.status !== 'closed').length || '0';
        document.getElementById('chatsCount').textContent = state.chatHistory.length || '0';
        
        // Load recent incidents
        const recentIncidents = document.getElementById('recentIncidents');
        if (incidents.length === 0) {
            recentIncidents.innerHTML = '<div class="loading">لا توجد حوادث</div>';
        } else {
            recentIncidents.innerHTML = incidents.slice(0, 5).map(inc => `
                <div class="incident-item">
                    <strong>${inc.title || 'حادثة'}</strong>
                    <small>${inc.created_at || ''}</small>
                </div>
            `).join('');
        }
        
        // Load recent detections
        const recentDetections = document.getElementById('recentDetections');
        if (detections.length === 0) {
            recentDetections.innerHTML = '<div class="loading">لا توجد كشوفات</div>';
        } else {
            recentDetections.innerHTML = detections.slice(0, 5).map(det => `
                <div class="detection-item">
                    <strong>${det.objects?.length || 0} أشياء</strong>
                    <small>${det.timestamp || ''}</small>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Dashboard load error:', error);
    }
}

// ===========================================
// Cameras Functions
// ===========================================
async function loadCameras() {
    const grid = document.getElementById('camerasGrid');
    grid.innerHTML = '<div class="loading">جاري تحميل الكاميرات...</div>';
    
    try {
        const cameras = await apiFetch('/cctv/cameras');
        if (cameras.length === 0) {
            grid.innerHTML = '<div class="loading">لا توجد كاميرات</div>';
            return;
        }
        
        grid.innerHTML = cameras.map(cam => `
            <div class="camera-card">
                <h4>${cam.name || cam.id}</h4>
                <p>الحالة: ${cam.enabled ? '🟢 مفعّل' : '�� معطّل'}</p>
                <button class="btn btn-secondary" onclick="toggleCamera('${cam.id}', ${!cam.enabled})">
                    ${cam.enabled ? 'إيقاف' : 'تشغيل'}
                </button>
            </div>
        `).join('');
    } catch (error) {
        grid.innerHTML = `<div class="error">خطأ: ${error.message}</div>`;
    }
}

function showAddCameraModal() {
    document.getElementById('addCameraModal').classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

async function addCamera() {
    const name = document.getElementById('cameraName').value;
    const url = document.getElementById('cameraUrl').value;
    
    if (!name || !url) {
        alert('الرجاء ملء جميع الحقول');
        return;
    }
    
    try {
        await apiFetch('/cctv/cameras', {
            method: 'POST',
            body: JSON.stringify({ name, url })
        });
        closeModal('addCameraModal');
        loadCameras();
        document.getElementById('cameraName').value = '';
        document.getElementById('cameraUrl').value = '';
    } catch (error) {
        alert(`خطأ: ${error.message}`);
    }
}

async function toggleCamera(cameraId, enable) {
    try {
        const endpoint = enable ? `/cctv/cameras/${cameraId}/start` : `/cctv/cameras/${cameraId}/stop`;
        await apiFetch(endpoint, { method: 'POST' });
        loadCameras();
    } catch (error) {
        alert(`خطأ: ${error.message}`);
    }
}

// ===========================================
// Detection Functions
// ===========================================
function setupDetectionUpload() {
    const fileInput = document.getElementById('detectionFile');
    const uploadArea = document.getElementById('uploadArea');
    const preview = document.getElementById('detectionPreview');
    const previewImage = document.getElementById('previewImage');
    const detectBtn = document.getElementById('detectBtn');
    
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (event) => {
                previewImage.src = event.target.result;
                preview.style.display = 'block';
                detectBtn.style.display = 'inline-flex';
            };
            reader.readAsDataURL(file);
        }
    });
    
    uploadArea.addEventListener('click', () => fileInput.click());
}

async function detectObjects() {
    const fileInput = document.getElementById('detectionFile');
    const resultsDiv = document.getElementById('detectionResults');
    
    if (!fileInput.files || fileInput.files.length === 0) {
        resultsDiv.innerHTML = '<div class="error">الرجاء اختيار صورة</div>';
        return;
    }
    
    resultsDiv.innerHTML = '<div class="loading">جاري الكشف...</div>';
    
    try {
        const file = fileInput.files[0];
        const base64 = await new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result.split(',')[1]);
            reader.onerror = reject;
            reader.readAsDataURL(file);
        });
        
        const data = await apiFetch('/detect', {
            method: 'POST',
            body: JSON.stringify({ frame_data: base64, timestamp: new Date().toISOString() })
        });
        
        const objects = data.objects || [];
        if (objects.length === 0) {
            resultsDiv.innerHTML = '<div class="loading">لم يتم اكتشاف أي أشياء</div>';
        } else {
            resultsDiv.innerHTML = `
                <div class="success">
                    <h4>تم اكتشاف ${objects.length} أشياء:</h4>
                    ${objects.map(obj => `
                        <div style="margin: 10px 0;">
                            <strong>${obj.label || obj.class}</strong> - 
                            الثقة: ${(obj.confidence * 100).toFixed(1)}%
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        loadDetectionHistory();
    } catch (error) {
        resultsDiv.innerHTML = `<div class="error">خطأ: ${error.message}</div>`;
    }
}

async function loadDetectionHistory() {
    const history = document.getElementById('detectionHistory');
    if (!history) return;
    
    history.innerHTML = '<div class="loading">جاري التحميل...</div>';
    
    try {
        const detections = await apiFetch('/detections');
        if (detections.length === 0) {
            history.innerHTML = '<div class="loading">لا توجد كشوفات</div>';
        } else {
            history.innerHTML = detections.slice(0, 10).map(det => `
                <div class="card" style="margin-bottom: 1rem;">
                    <div class="card-body">
                        <strong>${det.objects?.length || 0} أشياء</strong>
                        <small>${det.timestamp || ''}</small>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        history.innerHTML = `<div class="error">خطأ: ${error.message}</div>`;
    }
}

// ===========================================
// Chat Functions
// ===========================================
function loadChatHistory() {
    const messagesDiv = document.getElementById('chatMessages');
    if (!messagesDiv) return;
    
    // Clear welcome message if there's history
    if (state.chatHistory.length > 0) {
        messagesDiv.innerHTML = '';
        state.chatHistory.forEach(msg => {
            const bubble = document.createElement('div');
            bubble.className = `chat-bubble ${msg.role === 'user' ? 'user-bubble' : 'assistant-bubble'}`;
            bubble.textContent = msg.content;
            messagesDiv.appendChild(bubble);
        });
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
}

function sendQuickQuestion(question) {
    document.getElementById('chatInput').value = question;
    sendChat();
}

async function sendChat() {
    const input = document.getElementById('chatInput');
    const messagesDiv = document.getElementById('chatMessages');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Clear welcome if first message
    const welcome = messagesDiv.querySelector('.chat-welcome');
    if (welcome) welcome.remove();
    
    // Add user message
    const userBubble = document.createElement('div');
    userBubble.className = 'chat-bubble user-bubble';
    userBubble.textContent = message;
    messagesDiv.appendChild(userBubble);
    
    state.chatHistory.push({ role: 'user', content: message });
    localStorage.setItem('chatHistory', JSON.stringify(state.chatHistory));
    
    input.value = '';
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    // Add loading
    const loadingBubble = document.createElement('div');
    loadingBubble.className = 'chat-bubble assistant-bubble';
    loadingBubble.textContent = 'جاري التفكير...';
    messagesDiv.appendChild(loadingBubble);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    try {
        const data = await apiFetch('/chat', {
            method: 'POST',
            body: JSON.stringify({ message, session_id: state.sessionId })
        });
        
        loadingBubble.remove();
        
        const assistantBubble = document.createElement('div');
        assistantBubble.className = 'chat-bubble assistant-bubble';
        assistantBubble.textContent = data.assistant_response || data.message || 'لا يوجد رد';
        messagesDiv.appendChild(assistantBubble);
        
        state.chatHistory.push({ role: 'assistant', content: data.assistant_response || data.message });
        localStorage.setItem('chatHistory', JSON.stringify(state.chatHistory));
        
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    } catch (error) {
        loadingBubble.remove();
        const errorBubble = document.createElement('div');
        errorBubble.className = 'chat-bubble assistant-bubble error';
        errorBubble.textContent = `خطأ: ${error.message}`;
        messagesDiv.appendChild(errorBubble);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
}

function clearChat() {
    state.chatHistory = [];
    localStorage.removeItem('chatHistory');
    document.getElementById('chatMessages').innerHTML = `
        <div class="chat-welcome">
            <h4>مرحباً بك في المساعد الذكي!</h4>
            <p>أنا هنا لمساعدتك في كل ما يتعلق بالسلامة والصحة المهنية</p>
        </div>
    `;
}

// ===========================================
// Incidents Functions
// ===========================================
async function loadIncidents() {
    const list = document.getElementById('incidentsList');
    list.innerHTML = '<div class="loading">جاري تحميل الحوادث...</div>';
    
    try {
        const incidents = await apiFetch('/incidents');
        if (incidents.length === 0) {
            list.innerHTML = '<div class="loading">لا توجد حوادث</div>';
        } else {
            list.innerHTML = incidents.map(inc => `
                <div class="card" style="margin-bottom: 1rem;">
                    <div class="card-body">
                        <h4>${inc.title || 'حادثة'}</h4>
                        <p>${inc.description || ''}</p>
                        <div style="display: flex; gap: 1rem; margin-top: 1rem;">
                            <span class="badge-${inc.severity || 'medium'}">${inc.severity || 'متوسط'}</span>
                            <small>${inc.created_at || ''}</small>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        list.innerHTML = `<div class="error">خطأ: ${error.message}</div>`;
    }
}

function showAddIncidentModal() {
    document.getElementById('addIncidentModal').classList.add('active');
}

async function submitIncident() {
    const title = document.getElementById('incidentTitle').value;
    const description = document.getElementById('incidentDescription').value;
    const severity = document.getElementById('incidentSeverity').value;
    
    if (!title || !description) {
        alert('الرجاء ملء جميع الحقول');
        return;
    }
    
    try {
        await apiFetch('/incidents', {
            method: 'POST',
            body: JSON.stringify({ title, description, severity, timestamp: new Date().toISOString() })
        });
        closeModal('addIncidentModal');
        loadIncidents();
        document.getElementById('incidentTitle').value = '';
        document.getElementById('incidentDescription').value = '';
    } catch (error) {
        alert(`خطأ: ${error.message}`);
    }
}

function filterIncidents() {
    // TODO: Implement filtering
    loadIncidents();
}

// ===========================================
// Risk Assessment Functions
// ===========================================
async function loadRiskAssessments() {
    const list = document.getElementById('riskList');
    list.innerHTML = '<div class="loading">جاري تحميل تقييمات المخاطر...</div>';
    
    try {
        const risks = await apiFetch('/risk-assessments');
        if (risks.length === 0) {
            list.innerHTML = '<div class="loading">لا توجد تقييمات</div>';
        } else {
            list.innerHTML = risks.map(risk => `
                <div class="card" style="margin-bottom: 1rem;">
                    <div class="card-body">
                        <h4>${risk.hazard_description || 'تقييم'}</h4>
                        <p>المخاطر: ${risk.risk_level || 'متوسط'}</p>
                        <small>${risk.created_at || ''}</small>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        list.innerHTML = `<div class="error">خطأ: ${error.message}</div>`;
    }
}

function showAddRiskModal() {
    alert('قريباً: نموذج تقييم المخاطر');
}

// ===========================================
// Inspections Functions
// ===========================================
async function loadInspections() {
    const list = document.getElementById('inspectionsList');
    list.innerHTML = '<div class="loading">جاري تحميل التفتيشات...</div>';
    
    try {
        const inspections = await apiFetch('/inspections');
        if (inspections.length === 0) {
            list.innerHTML = '<div class="loading">لا توجد تفتيشات</div>';
        } else {
            list.innerHTML = inspections.map(insp => `
                <div class="card" style="margin-bottom: 1rem;">
                    <div class="card-body">
                        <h4>${insp.location || 'تفتيش'}</h4>
                        <p>النتيجة: ${insp.result || 'جاري المراجعة'}</p>
                        <small>${insp.inspection_date || ''}</small>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        list.innerHTML = `<div class="error">خطأ: ${error.message}</div>`;
    }
}

function showAddInspectionModal() {
    alert('قريباً: نموذج التفتيش');
}

// ===========================================
// Reports Functions
// ===========================================
async function loadReports() {
    const list = document.getElementById('reportsList');
    list.innerHTML = '<div class="loading">جاري تحميل التقارير...</div>';
    
    try {
        const reports = await apiFetch('/reports');
        if (reports.length === 0) {
            list.innerHTML = '<div class="loading">لا توجد تقارير</div>';
        } else {
            list.innerHTML = reports.map(rep => `
                <div class="card" style="margin-bottom: 1rem;">
                    <div class="card-body">
                        <h4>تقرير ${rep.id || ''}</h4>
                        <p>${rep.description || 'تقرير عام'}</p>
                        <small>${rep.created_at || ''}</small>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        list.innerHTML = `<div class="error">خطأ: ${error.message}</div>`;
    }
}

async function generateReport() {
    try {
        const response = await fetch(CONFIG.API_BASE_URL + '/export/pdf');
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `report_${Date.now()}.pdf`;
        a.click();
    } catch (error) {
        alert(`خطأ: ${error.message}`);
    }
}

async function exportReports() {
    try {
        const response = await fetch(CONFIG.API_BASE_URL + '/reports/export');
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `data_${Date.now()}.xlsx`;
        a.click();
    } catch (error) {
        alert(`خطأ: ${error.message}`);
    }
}

// ===========================================
// Theme & System Status
// ===========================================
function toggleTheme() {
    state.theme = state.theme === 'light' ? 'dark' : 'light';
    document.body.classList.toggle('dark-theme');
    localStorage.setItem('theme', state.theme);
    document.getElementById('themeIcon').textContent = state.theme === 'dark' ? '☀️' : '🌙';
}

function toggleLanguage() {
    state.language = state.language === 'ar' ? 'en' : 'ar';
    localStorage.setItem('language', state.language);
    document.getElementById('langText').textContent = state.language === 'ar' ? 'EN' : 'عر';
    // TODO: Implement full i18n
}

async function checkSystemStatus() {
    try {
        const status = await apiFetch('/system/status');
        const badge = document.getElementById('systemStatus');
        if (status.llmAvailable && status.cctvAvailable) {
            badge.innerHTML = '<span class="status-dot"></span><span>متصل</span>';
            badge.style.background = 'var(--success)';
        } else {
            badge.innerHTML = '<span class="status-dot"></span><span>محدود</span>';
            badge.style.background = 'var(--warning)';
        }
    } catch (error) {
        const badge = document.getElementById('systemStatus');
        badge.innerHTML = '<span class="status-dot"></span><span>غير متصل</span>';
        badge.style.background = 'var(--danger)';
    }
}

// ===========================================
// Initialization
// ===========================================
document.addEventListener('DOMContentLoaded', () => {
    // Apply saved theme
    if (state.theme === 'dark') {
        document.body.classList.add('dark-theme');
        document.getElementById('themeIcon').textContent = '☀️';
    }
    
    // Setup event listeners
    document.querySelectorAll('.nav-item').forEach(nav => {
        nav.addEventListener('click', (e) => {
            e.preventDefault();
            const page = nav.getAttribute('data-page');
            if (page) navigateTo(page);
        });
    });
    
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
    document.getElementById('langToggle').addEventListener('click', toggleLanguage);
    
    // Setup chat input
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChat();
            }
        });
    }
    
    // Setup detection upload
    setupDetectionUpload();
    
    // Check system status
    checkSystemStatus();
    setInterval(checkSystemStatus, 30000); // Every 30 seconds
    
    // Load dashboard
    loadDashboard();
    
    console.log('✅ HAZM TUWAIQ initialized');
});
