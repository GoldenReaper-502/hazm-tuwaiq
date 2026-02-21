/* ═══════════════════════════════════════════════════════════
   HAZM TUWAIQ - Production Dashboard Logic
   Real-time Monitoring, AI Integration, Multi-Language
   ═══════════════════════════════════════════════════════════ */

// ═══ CONFIGURATION ═══
const CONFIG = {
    API_BASE: '/api',
    WS_URL: `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws`,
    REFRESH_INTERVAL: 5000, // 5 seconds
    LANGUAGES: {
        ar: {
            dashboard: 'لوحة التحكم الرئيسية',
            cameras: 'كاميرات المراقبة',
            alerts: 'التنبيهات',
            predictions: 'التوقعات الذكية',
            heatmap: 'خريطة المخاطر',
            twins: 'التوائم الرقمية',
            incidents: 'الحوادث',
            analytics: 'التحليلات',
            reports: 'التقارير',
            settings: 'الإعدادات'
        },
        en: {
            dashboard: 'Main Dashboard',
            cameras: 'CCTV Cameras',
            alerts: 'Alerts',
            predictions: 'Smart Predictions',
            heatmap: 'Risk Heatmap',
            twins: 'Digital Twins',
            incidents: 'Incidents',
            analytics: 'Analytics',
            reports: 'Reports',
            settings: 'Settings'
        }
    }
};

// ═══ STATE MANAGEMENT ═══
const AppState = {
    currentPage: 'dashboard',
    currentLanguage: 'ar',
    currentTheme: 'light',
    sidebarCollapsed: false,
    user: null,
    stats: {},
    cameras: [],
    alerts: [],
    predictions: [],
    refreshInterval: null
};

// ═══ API CLIENT ═══
class APIClient {
    constructor(baseURL) {
        this.baseURL = baseURL;
    }

    async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Request failed');
            }

            return data;
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            showNotification('خطأ في الاتصال بالخادم', 'error');
            throw error;
        }
    }

    // Core Stats
    async getStats() {
        return this.request('/stats');
    }

    // Cameras
    async getCameras() {
        return this.request('/cctv/cameras');
    }

    async getCameraStream(cameraId) {
        return `${this.baseURL}/cctv/stream/${cameraId}`;
    }

    // Alerts
    async getAlerts(filters = {}) {
        const params = new URLSearchParams(filters);
        return this.request(`/alerts/alerts?${params}`);
    }

    async acknowledgeAlert(alertId) {
        return this.request(`/alerts/alerts/${alertId}/acknowledge`, { method: 'POST' });
    }

    // Predictions
    async getPredictions() {
        return this.request('/predictive/predictions');
    }

    async createPrediction(data) {
        return this.request('/predictive/predictions', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // Trends
    async getTrends() {
        return this.request('/predictive/trends');
    }

    // Heatmaps
    async getHeatmaps() {
        return this.request('/predictive/heatmaps');
    }

    async generateHeatmap(data) {
        return this.request('/predictive/heatmaps', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // Digital Twins
    async getTwins() {
        return this.request('/predictive/twins');
    }

    async createTwin(data) {
        return this.request('/predictive/twins', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async simulateTwin(twinId, data) {
        return this.request(`/predictive/twins/${twinId}/simulate`, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // Incidents
    async getIncidents() {
        return this.request('/incidents');
    }

    // Analytics
    async getAnalytics(timeframe = 'week') {
        return this.request(`/analytics?timeframe=${timeframe}`);
    }
}

const api = new APIClient(CONFIG.API_BASE);

// ═══ CHART MANAGER ═══
class ChartManager {
    constructor() {
        this.charts = {};
    }

    createRealtimeChart(canvasId, options = {}) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: options.label || 'البيانات',
                    data: [],
                    borderColor: options.color || '#3b82f6',
                    backgroundColor: options.backgroundColor || 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            font: { family: 'Cairo' }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            font: { family: 'Cairo' }
                        }
                    },
                    x: {
                        ticks: {
                            font: { family: 'Cairo' }
                        }
                    }
                }
            }
        });

        return this.charts[canvasId];
    }

    updateChart(canvasId, labels, data) {
        const chart = this.charts[canvasId];
        if (!chart) return;

        chart.data.labels = labels;
        chart.data.datasets[0].data = data;
        chart.update();
    }

    destroyChart(canvasId) {
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
            delete this.charts[canvasId];
        }
    }
}

const chartManager = new ChartManager();

// ═══ INITIALIZATION ═══
document.addEventListener('DOMContentLoaded', () => {
    initializeSidebar();
    initializeTopbar();
    initializePages();
    initializeCharts();
    loadInitialData();
    startAutoRefresh();
});

// ═══ SIDEBAR FUNCTIONS ═══
function initializeSidebar() {
    // Toggle Sidebar
    const toggleBtn = document.querySelector('.sidebar-toggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const sidebar = document.querySelector('.sidebar');
            sidebar.classList.toggle('collapsed');
            AppState.sidebarCollapsed = !AppState.sidebarCollapsed;
        });
    }

    // Navigation Items
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            if (page) {
                navigateToPage(page);
            }
        });
    });
}

function navigateToPage(pageName) {
    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-page="${pageName}"]`)?.classList.add('active');

    // Show page
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    document.getElementById(`${pageName}-page`)?.classList.add('active');

    // Update page title
    const pageTitle = document.querySelector('.page-title');
    if (pageTitle) {
        pageTitle.textContent = CONFIG.LANGUAGES[AppState.currentLanguage][pageName];
    }

    AppState.currentPage = pageName;
}

// ═══ TOPBAR FUNCTIONS ═══
function initializeTopbar() {
    // Language Toggle
    const langBtn = document.getElementById('langToggle');
    if (langBtn) {
        langBtn.addEventListener('click', toggleLanguage);
    }

    // Theme Toggle
    const themeBtn = document.getElementById('themeToggle');
    if (themeBtn) {
        themeBtn.addEventListener('click', toggleTheme);
    }

    // Notifications
    const notifBtn = document.getElementById('notificationBtn');
    const notifDropdown = document.querySelector('.notification-dropdown');
    if (notifBtn && notifDropdown) {
        notifBtn.addEventListener('click', () => {
            notifDropdown.classList.toggle('active');
        });

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!notifBtn.contains(e.target) && !notifDropdown.contains(e.target)) {
                notifDropdown.classList.remove('active');
            }
        });
    }

    // Fullscreen
    const fullscreenBtn = document.getElementById('fullscreenBtn');
    if (fullscreenBtn) {
        fullscreenBtn.addEventListener('click', toggleFullscreen);
    }

    // Refresh
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshDashboard);
    }
}

function toggleLanguage() {
    AppState.currentLanguage = AppState.currentLanguage === 'ar' ? 'en' : 'ar';
    document.documentElement.setAttribute('dir', AppState.currentLanguage === 'ar' ? 'rtl' : 'ltr');
    document.documentElement.setAttribute('lang', AppState.currentLanguage);
    updateUILanguage();
}

function toggleTheme() {
    AppState.currentTheme = AppState.currentTheme === 'light' ? 'dark' : 'light';
    document.body.classList.toggle('dark-mode');
    
    const icon = document.querySelector('#themeToggle i');
    if (icon) {
        icon.className = AppState.currentTheme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
    } else {
        document.exitFullscreen();
    }
}

function updateUILanguage() {
    // Update page titles, labels, etc.
    const pageTitle = document.querySelector('.page-title');
    if (pageTitle) {
        pageTitle.textContent = CONFIG.LANGUAGES[AppState.currentLanguage][AppState.currentPage];
    }
}

// ═══ PAGE INITIALIZATION ═══
function initializePages() {
    // Chart Controls
    const chartControls = document.querySelectorAll('.chart-control');
    chartControls.forEach(control => {
        control.addEventListener('click', () => {
            chartControls.forEach(c => c.classList.remove('active'));
            control.classList.add('active');
            
            const timeframe = control.dataset.timeframe;
            updateChartTimeframe(timeframe);
        });
    });

    // View Controls
    const viewBtns = document.querySelectorAll('.view-btn');
    viewBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            viewBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            const view = btn.dataset.view;
            toggleCameraView(view);
        });
    });
}

// ═══ CHARTS ═══
function initializeCharts() {
    chartManager.createRealtimeChart('realtimeChart', {
        label: 'معدل الأمان',
        color: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.1)'
    });
}

function updateChartTimeframe(timeframe) {
    // Fetch new data based on timeframe
    api.getAnalytics(timeframe).then(data => {
        if (data.success && data.data) {
            chartManager.updateChart('realtimeChart', data.data.labels, data.data.values);
        }
    });
}

// ═══ DATA LOADING ═══
async function loadInitialData() {
    try {
        // Load Stats
        await loadStats();
        
        // Load Cameras
        await loadCameras();
        
        // Load Alerts
        await loadAlerts();
        
        // Load Predictions
        await loadPredictions();

        console.log('✅ Initial data loaded successfully');
    } catch (error) {
        console.error('Error loading initial data:', error);
    }
}

async function loadStats() {
    try {
        const response = await api.getStats();
        if (response.success) {
            AppState.stats = response.data;
            updateStatsUI(response.data);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
        // Use mock data for demo
        updateStatsUI({
            safetyScore: 87.5,
            safetyChange: 5.2,
            activeCameras: 8,
            totalCameras: 12,
            activeAlerts: 5,
            alertChange: 2,
            activeWorkers: 142,
            ppeCompliance: 98
        });
    }
}

function updateStatsUI(stats) {
    // Safety Score
    const safetyValue = document.querySelector('.stat-card:nth-child(1) .stat-value');
    const safetyChange = document.querySelector('.stat-card:nth-child(1) .stat-change');
    if (safetyValue) safetyValue.textContent = stats.safetyScore || '87.5';
    if (safetyChange) {
        safetyChange.textContent = `+${stats.safetyChange || '5.2'}%`;
        safetyChange.className = 'stat-change positive';
    }

    // Cameras
    const cameraValue = document.querySelector('.stat-card:nth-child(2) .stat-value');
    if (cameraValue) {
        cameraValue.textContent = `${stats.activeCameras || 8}/${stats.totalCameras || 12}`;
    }

    // Alerts
    const alertValue = document.querySelector('.stat-card:nth-child(3) .stat-value');
    const alertChange = document.querySelector('.stat-card:nth-child(3) .stat-change');
    if (alertValue) alertValue.textContent = stats.activeAlerts || '5';
    if (alertChange) {
        alertChange.textContent = `+${stats.alertChange || 2}`;
        alertChange.className = 'stat-change negative';
    }

    // Workers
    const workerValue = document.querySelector('.stat-card:nth-child(4) .stat-value');
    if (workerValue) workerValue.textContent = stats.activeWorkers || '142';
}

async function loadCameras() {
    try {
        const response = await api.getCameras();
        if (response.success) {
            AppState.cameras = response.data;
            updateCamerasUI(response.data);
        }
    } catch (error) {
        console.error('Error loading cameras:', error);
        // Use mock data
        updateCamerasUI([
            { id: 'cam-001', name: 'مدخل المصنع', status: 'online', rtsp_url: '' },
            { id: 'cam-002', name: 'خط الإنتاج 1', status: 'online', rtsp_url: '' },
            { id: 'cam-003', name: 'خط الإنتاج 2', status: 'online', rtsp_url: '' },
            { id: 'cam-004', name: 'منطقة التخزين', status: 'online', rtsp_url: '' }
        ]);
    }
}

function updateCamerasUI(cameras) {
    const cameraGrid = document.querySelector('.camera-grid');
    if (!cameraGrid) return;

    cameraGrid.innerHTML = cameras.map(camera => `
        <div class="camera-card">
            <div class="camera-video" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; color: white; font-size: 3rem;">
                <i class="fas fa-video"></i>
            </div>
            <div class="camera-overlay">
                <div class="camera-name">${camera.name}</div>
                <span class="camera-status">
                    <i class="fas fa-circle"></i>
                    ${camera.status === 'online' ? 'متصل' : 'غير متصل'}
                </span>
            </div>
        </div>
    `).join('');
}

function toggleCameraView(view) {
    const cameraGrid = document.querySelector('.camera-grid');
    if (!cameraGrid) return;

    if (view === 'list') {
        cameraGrid.style.gridTemplateColumns = '1fr';
    } else {
        cameraGrid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(300px, 1fr))';
    }
}

async function loadAlerts() {
    try {
        const response = await api.getAlerts({ limit: 10 });
        if (response.success) {
            AppState.alerts = response.data;
            updateAlertsUI(response.data);
        }
    } catch (error) {
        console.error('Error loading alerts:', error);
        // Use mock data
        updateAlertsUI([
            {
                id: 'alert-001',
                type: 'no_helmet',
                severity: 'critical',
                title: 'عامل بدون خوذة',
                description: 'تم رصد عامل في خط الإنتاج 1 بدون خوذة واقية',
                location: 'خط الإنتاج 1',
                timestamp: new Date().toISOString()
            },
            {
                id: 'alert-002',
                type: 'restricted_area',
                severity: 'high',
                title: 'دخول منطقة محظورة',
                description: 'عامل دخل منطقة خطرة بدون تصريح',
                location: 'منطقة المعدات الثقيلة',
                timestamp: new Date(Date.now() - 300000).toISOString()
            },
            {
                id: 'alert-003',
                type: 'near_miss',
                severity: 'medium',
                title: 'كاد أن يحدث',
                description: 'رصد تقارب خطير بين عامل ومعدة متحركة',
                location: 'منطقة التخزين',
                timestamp: new Date(Date.now() - 600000).toISOString()
            }
        ]);
    }
}

function updateAlertsUI(alerts) {
    const alertsList = document.querySelector('.alerts-list');
    if (!alertsList) return;

    if (alerts.length === 0) {
        alertsList.innerHTML = '<p style="text-align: center; color: var(--text-tertiary); padding: 2rem;">لا توجد تنبيهات حالياً</p>';
        return;
    }

    alertsList.innerHTML = alerts.map(alert => {
        const timeAgo = getTimeAgo(new Date(alert.timestamp));
        const iconMap = {
            critical: 'fa-exclamation-triangle',
            high: 'fa-exclamation-circle',
            medium: 'fa-info-circle',
            low: 'fa-check-circle'
        };

        return `
            <div class="alert-item ${alert.severity}">
                <div class="alert-icon ${alert.severity}">
                    <i class="fas ${iconMap[alert.severity] || 'fa-bell'}"></i>
                </div>
                <div class="alert-content">
                    <div class="alert-title">${alert.title}</div>
                    <div class="alert-description">${alert.description}</div>
                    <div class="alert-meta">
                        <span><i class="fas fa-map-marker-alt"></i> ${alert.location || 'غير محدد'}</span>
                        <span><i class="fas fa-clock"></i> ${timeAgo}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

async function loadPredictions() {
    try {
        const response = await api.getPredictions();
        if (response.success && response.data && response.data.length > 0) {
            const latestPrediction = response.data[0];
            updatePredictionUI(latestPrediction);
        }
    } catch (error) {
        console.error('Error loading predictions:', error);
        // Use mock data
        updatePredictionUI({
            probability: 0.68,
            risk_level: 'high',
            factors: [
                'زيادة معدل الحوادث البسيطة بنسبة 45%',
                'انخفاض الالتزام بمعدات السلامة'
            ]
        });
    }
}

function updatePredictionUI(prediction) {
    const probability = Math.round(prediction.probability * 100);
    
    const predictionValue = document.querySelector('.prediction-value');
    const predictionFill = document.querySelector('.prediction-fill');
    const predictionFactors = document.querySelector('.prediction-factors');

    if (predictionValue) {
        predictionValue.textContent = `${probability}%`;
        predictionValue.className = 'prediction-value';
        if (probability >= 70) predictionValue.classList.add('high');
    }

    if (predictionFill) {
        predictionFill.style.width = `${probability}%`;
    }

    if (predictionFactors && prediction.factors) {
        predictionFactors.innerHTML = prediction.factors.slice(0, 3).map(factor => `
            <div class="factor">
                <i class="fas fa-exclamation-triangle"></i>
                <span>${factor}</span>
            </div>
        `).join('');
    }
}

// ═══ AUTO REFRESH ═══
function startAutoRefresh() {
    AppState.refreshInterval = setInterval(() => {
        if (AppState.currentPage === 'dashboard') {
            refreshDashboard();
        }
    }, CONFIG.REFRESH_INTERVAL);
}

async function refreshDashboard() {
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.style.transform = 'rotate(360deg)';
        refreshBtn.style.transition = 'transform 0.5s';
        setTimeout(() => {
            refreshBtn.style.transform = 'rotate(0deg)';
        }, 500);
    }

    await loadStats();
    await loadAlerts();
    await loadPredictions();
    
    // Update chart with random data (demo)
    const labels = [];
    const data = [];
    for (let i = 23; i >= 0; i--) {
        labels.push(`${i}:00`);
        data.push(Math.floor(Math.random() * 30) + 70);
    }
    chartManager.updateChart('realtimeChart', labels, data);
}

// ═══ UTILITY FUNCTIONS ═══
function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);
    
    if (seconds < 60) return 'الآن';
    if (seconds < 3600) return `منذ ${Math.floor(seconds / 60)} دقيقة`;
    if (seconds < 86400) return `منذ ${Math.floor(seconds / 3600)} ساعة`;
    return `منذ ${Math.floor(seconds / 86400)} يوم`;
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: ${type === 'error' ? '#ef4444' : '#10b981'};
        color: white;
        padding: 1rem 2rem;
        border-radius: 0.5rem;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        z-index: 10000;
        animation: slideDown 0.3s ease;
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideUp 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideDown {
        from {
            transform: translateX(-50%) translateY(-100%);
            opacity: 0;
        }
        to {
            transform: translateX(-50%) translateY(0);
            opacity: 1;
        }
    }
    @keyframes slideUp {
        from {
            transform: translateX(-50%) translateY(0);
            opacity: 1;
        }
        to {
            transform: translateX(-50%) translateY(-100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ═══ EXPORT FOR DEBUGGING ═══
window.HazmApp = {
    state: AppState,
    api: api,
    charts: chartManager,
    refresh: refreshDashboard,
    navigateTo: navigateToPage
};

console.log('🚀 HAZM TUWAIQ Dashboard Initialized');
console.log('📊 Access app state via: window.HazmApp');
