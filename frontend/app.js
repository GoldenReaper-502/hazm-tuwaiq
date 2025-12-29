// ====== إعدادات ======
// Auto-detect API URL based on environment
const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const isRenderFrontend = window.location.hostname.includes('hazm-frontend') || window.location.hostname.includes('onrender.com');

let DEFAULT_API;
if (isLocalhost) {
  DEFAULT_API = "http://localhost:8000";
} else if (isRenderFrontend) {
  // On Render, Frontend and Backend are separate services
  DEFAULT_API = "https://hazm-backend.onrender.com";
} else {
  DEFAULT_API = window.location.origin;
}

const LS_API = "hazm_api_url";
const LS_KEY = "hazm_api_key";
const LS_CHAT_HISTORY = "hazm_chat_history";

// Development mode - show logs
const IS_DEV = true;

function log(msg) {
  if (IS_DEV) console.log("[Hazm]", msg);
}

function $(id) { return document.getElementById(id); }

// ====== Auto-fix Settings ======
// Reset to localhost if we're on localhost and settings point to Render
(function autoFixSettings() {
  const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  const savedUrl = localStorage.getItem(LS_API);
  
  if (isLocalhost && savedUrl && savedUrl.includes('render.com')) {
    console.log('[Hazm] Auto-fixing: Resetting API URL to localhost');
    localStorage.setItem(LS_API, 'http://localhost:8000');
    localStorage.removeItem(LS_KEY); // Clear API key too
  }
})();

// ====== Configuration ======
function getCfg() {
  const apiUrl = (localStorage.getItem(LS_API) || DEFAULT_API).replace(/\/+$/, '');
  const apiKey = localStorage.getItem(LS_KEY) || "";
  return { apiUrl, apiKey };
}

function setCfg(apiUrl, apiKey) {
  localStorage.setItem(LS_API, apiUrl.replace(/\/+$/, ''));
  localStorage.setItem(LS_KEY, apiKey || "");
}

function headersJSON() {
  const { apiKey } = getCfg();
  const h = { "Content-Type": "application/json" };
  if (apiKey) h["x-api-key"] = apiKey;
  return h;
}

function headersAny() {
  const { apiKey } = getCfg();
  const h = {};
  if (apiKey) h["x-api-key"] = apiKey;
  return h;
}

function pretty(obj) {
  return JSON.stringify(obj, null, 2);
}

// ====== Camera Management ======
class CameraManager {
  constructor() {
    this.stream = null;
    this.video = $("cameraVideo");
    this.canvas = $("detectionCanvas");
    this.ctx = this.canvas.getContext("2d");
    this.devices = [];
    this.currentDeviceId = null;
    this.status = "stopped";
    this.detectionEnabled = false;
    this.detectionInterval = null;
    this.lastDetection = null;
    
    this.setupListeners();
    this.discoverDevices();
  }

  setupListeners() {
    $("startCamera").addEventListener("click", () => this.start());
    $("stopCamera").addEventListener("click", () => this.stop());
    $("retryCamera").addEventListener("click", () => this.retry());
    $("deviceSelect").addEventListener("change", (e) => {
      this.currentDeviceId = e.target.value;
    });
    $("enableDetection").addEventListener("change", (e) => {
      this.detectionEnabled = e.target.checked;
      if (this.detectionEnabled && this.status === "running") {
        this.startDetection();
      } else {
        this.stopDetection();
      }
    });
  }

  async discoverDevices() {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      this.devices = devices.filter(d => d.kind === "videoinput");
      
      const select = $("deviceSelect");
      select.innerHTML = '';
      
      if (this.devices.length === 0) {
        select.innerHTML = '<option value="">لا توجد كاميرات متاحة</option>';
        this.setStatus("failed", "لا توجد أجهزة كاميرا متاحة");
        return;
      }
      
      this.devices.forEach((device, idx) => {
        const opt = document.createElement("option");
        opt.value = device.deviceId;
        opt.textContent = device.label || `كاميرا ${idx + 1}`;
        select.appendChild(opt);
      });
      
      this.currentDeviceId = this.devices[0].deviceId;
      log(`Found ${this.devices.length} camera(s)`);
    } catch (e) {
      log(`Error discovering devices: ${e.message}`);
      this.setStatus("failed", `خطأ في البحث عن الأجهزة: ${e.message}`);
    }
  }

  setStatus(status, message = "") {
    this.status = status;
    const statusText = $("cameraStatusText");
    const statusMap = {
      "stopped": "⚫ متوقفة",
      "starting": "🟡 تحضير...",
      "running": "🟢 تعمل",
      "failed": "🔴 خطأ",
      "retrying": "🟠 محاولة جديدة...",
    };
    
    statusText.textContent = statusMap[status] || status;
    if (message) {
      statusText.textContent += ` - ${message}`;
    }
    
    // Update button states
    $("startCamera").disabled = status !== "stopped";
    $("stopCamera").disabled = status !== "running";
    $("retryCamera").disabled = status !== "failed";
    $("enableDetection").disabled = status !== "running";
  }

  async start() {
    if (!this.currentDeviceId && this.devices.length === 0) {
      this.setStatus("failed", "لا توجد كاميرا متاحة");
      return;
    }

    this.setStatus("starting");
    
    try {
      const constraints = {
        video: {
          deviceId: this.currentDeviceId ? { exact: this.currentDeviceId } : undefined,
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
        audio: false,
      };

      this.stream = await navigator.mediaDevices.getUserMedia(constraints);
      this.video.srcObject = this.stream;

      // Wait for video to load and check dimensions
      await new Promise((resolve, reject) => {
        const checkReady = () => {
          if (this.video.videoWidth > 0 && this.video.videoHeight > 0) {
            resolve();
          } else {
            setTimeout(checkReady, 100);
          }
        };
        
        const timeout = setTimeout(() => {
          reject(new Error("فشل تحميل الكاميرا - شاشة سوداء"));
        }, 3000);

        this.video.onloadedmetadata = () => {
          clearTimeout(timeout);
          checkReady();
        };
      });

      // Setup canvas
      this.canvas.width = this.video.videoWidth;
      this.canvas.height = this.video.videoHeight;

      // Show video container
      $("videoContainer").style.display = "block";
      $("cameraError").style.display = "none";

      this.setStatus("running", `${this.video.videoWidth}x${this.video.videoHeight}`);
      log("Camera started successfully");

      if ($("enableDetection").checked) {
        this.startDetection();
      }
    } catch (e) {
      log(`Camera error: ${e.message}`);
      
      let errorMsg = e.message;
      if (e.name === "NotAllowedError") {
        errorMsg = "تم رفض صلاحيات الكاميرا. تحقق من إعدادات الخصوصية.";
      } else if (e.name === "NotFoundError") {
        errorMsg = "لا توجد كاميرا متاحة.";
      } else if (e.name === "NotReadableError") {
        errorMsg = "الكاميرا قيد الاستخدام من قبل تطبيق آخر.";
      } else if (e.message.includes("secure context")) {
        errorMsg = "يجب استخدام HTTPS. استخدم localhost أو https فقط.";
      }

      this.setStatus("failed", errorMsg);
      $("cameraError").textContent = `خطأ: ${errorMsg}`;
      $("cameraError").style.display = "block";
    }
  }

  stop() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
    this.video.srcObject = null;
    $("videoContainer").style.display = "none";
    this.setStatus("stopped");
    this.stopDetection();
    log("Camera stopped");
  }

  retry() {
    this.stop();
    setTimeout(() => this.start(), 500);
  }

  startDetection() {
    if (this.detectionInterval) return;
    
    log("Detection started");
    this.detectionInterval = setInterval(() => this.captureAndDetect(), 1200);
  }

  stopDetection() {
    if (this.detectionInterval) {
      clearInterval(this.detectionInterval);
      this.detectionInterval = null;
    }
    log("Detection stopped");
  }

  async captureAndDetect() {
    if (!this.video || this.video.videoWidth === 0) return;

    try {
      // Draw video frame to canvas
      this.ctx.drawImage(this.video, 0, 0);
      
      // Get base64 frame
      const frameData = this.canvas.toDataURL("image/jpeg", 0.8).split(',')[1];
      
      // Send to backend
      const { apiUrl } = getCfg();
      const response = await fetch(`${apiUrl}/detect`, {
        method: "POST",
        headers: headersJSON(),
        body: JSON.stringify({
          frame_data: frameData,
          timestamp: new Date().toISOString(),
        }),
      });

      if (!response.ok) {
        log(`Detection error: ${response.status}`);
        return;
      }

      // Check if response is JSON
      const contentType = response.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        log(`Unexpected response type: ${contentType}`);
        return;
      }

      const detection = await response.json();
      this.lastDetection = detection;
      
      // Update stats
      const now = new Date().toLocaleTimeString("ar-SA");
      $("detectionStats").textContent = `آخر تحديث: ${now} | ${detection.objects.length} أجسام`;
      
      // Draw overlays
      this.drawDetectionOverlay(detection);
      
      // Show results
      this.showDetectionResults(detection);
      
      log(`Detection: ${detection.objects.length} objects`);
    } catch (e) {
      log(`Capture error: ${e.message}`);
    }
  }

  drawDetectionOverlay(detection) {
    // Draw semi-transparent overlay with boxes
    this.ctx.strokeStyle = "#00FF00";
    this.ctx.lineWidth = 2;
    this.ctx.font = "12px Arial";
    this.ctx.fillStyle = "#00FF00";

    detection.objects.forEach(obj => {
      const bbox = obj.bbox || obj.box || obj.boxes || [0, 0, 0, 0];
      const [x1, y1, x2, y2] = bbox;
      try {
        this.ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);
      } catch (e) {}
      
      const cls = obj.class || obj.label || obj.name || 'obj';
      const conf = (typeof obj.confidence === 'number') ? obj.confidence : (obj.conf || 0);
      const label = `${cls} ${(conf * 100).toFixed(0)}%`;
      try {
        this.ctx.fillText(label, x1, Math.max(12, y1 - 5));
      } catch (e) {}
    });
  }

  showDetectionResults(detection) {
    $("detectionResult").style.display = "block";
    $("detectionOutput").textContent = JSON.stringify({
      id: detection.id,
      timestamp: detection.timestamp,
      objects: detection.objects.map(o => ({
        class: o.class,
        confidence: `${(o.confidence * 100).toFixed(1)}%`,
      })),
    }, null, 2);
  }
}

// ====== Chat Management ======
class ChatManager {
  constructor() {
    this.sessionId = `session_${Date.now()}`;
    this.messages = this.loadHistory();
    this.isLoading = false;
    
    this.setupListeners();
    this.renderMessages();
  }

  setupListeners() {
    $("sendChat").addEventListener("click", () => this.sendMessage());
    $("chatInput").addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });
    $("clearChat").addEventListener("click", () => this.clearHistory());
    $("askAboutDetection").addEventListener("click", () => this.askAboutDetection());
  }

  loadHistory() {
    try {
      const data = localStorage.getItem(LS_CHAT_HISTORY);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      log(`Error loading chat history: ${e.message}`);
      return [];
    }
  }

  saveHistory() {
    try {
      localStorage.setItem(LS_CHAT_HISTORY, JSON.stringify(this.messages));
    } catch (e) {
      log(`Error saving chat history: ${e.message}`);
    }
  }

  async sendMessage() {
    const input = $("chatInput");
    const message = input.value.trim();

    if (!message) {
      $("chatStatus").textContent = "اكتب سؤالك أولاً";
      return;
    }

    if (this.isLoading) {
      $("chatStatus").textContent = "جارِ الإرسال...";
      return;
    }

    this.isLoading = true;
    $("sendChat").disabled = true;
    $("chatStatus").textContent = "جارِ الإرسال...";

    try {
      const { apiUrl } = getCfg();
      
      const payload = {
        message,
        detection_result: camera.lastDetection || null,
        session_id: this.sessionId,
      };

      const response = await fetch(`${apiUrl}/chat`, {
        method: "POST",
        headers: headersJSON(),
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText.substring(0, 100)}`);
      }

      const contentType = response.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        const text = await response.text();
        throw new Error(`توقع JSON لكن استلم: ${text.substring(0, 100)}...`);
      }

      const chatResponse = await response.json();
      
      // Add to messages (exactly ONE response per question)
      this.messages.push({
        role: "user",
        content: message,
        timestamp: new Date().toISOString(),
      });
      this.messages.push({
        role: "assistant",
        content: chatResponse.assistant_response,
        timestamp: chatResponse.timestamp,
        detectionAttached: chatResponse.detection_attached,
      });

      this.saveHistory();
      this.renderMessages();
      input.value = "";
      $("chatStatus").textContent = "تم الإرسال";
      
      log("Message sent successfully");
    } catch (e) {
      log(`Chat error: ${e.message}`);
      $("chatStatus").textContent = `خطأ: ${e.message}`;
    } finally {
      this.isLoading = false;
      $("sendChat").disabled = false;
    }
  }

  askAboutDetection() {
    if (!camera.lastDetection) {
      $("chatStatus").textContent = "لا توجد نتائج كشف حالية";
      return;
    }

    const detInfo = camera.lastDetection.objects
      .map(o => `${o.class} (${(o.confidence * 100).toFixed(0)}%)`)
      .join(", ");
    
    $("chatInput").value = `أخبرني عن هذا الكشف: ${detInfo}`;
    this.sendMessage();
  }

  renderMessages() {
    const container = $("chatMessages");
    container.innerHTML = '';

    this.messages.forEach(msg => {
      const div = document.createElement("div");
      div.className = `chat-message ${msg.role}`;
      
      const roleText = msg.role === "user" ? "أنت" : "النظام";
      const icon = msg.role === "user" ? "👤" : "🤖";
      
      let content = msg.content;
      if (msg.detectionAttached) {
        content += " (مرفق: نتيجة كشف)";
      }

      div.innerHTML = `
        <div class="chat-role">${icon} ${roleText}</div>
        <div class="chat-content">${this.escapeHtml(content)}</div>
        <div class="chat-time">${this.formatTime(msg.timestamp)}</div>
      `;

      container.appendChild(div);
    });

    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
  }

  clearHistory() {
    if (confirm("هل تريد مسح سجل الدردشة؟")) {
      this.messages = [];
      this.saveHistory();
      this.renderMessages();
      log("Chat history cleared");
    }
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  formatTime(timestamp) {
    if (!timestamp) return "";
    const date = new Date(timestamp);
    return date.toLocaleTimeString("ar-SA");
  }
}

// ====== Health Check ======
async function loadHealth() {
  const { apiUrl } = getCfg();
  $("statusOut").textContent = "جارِ الاتصال...";
  try {
    let res = await fetch(`${apiUrl}/`, { 
      headers: headersAny(),
      mode: 'cors'
    });
    
    if (!res.ok) {
      res = await fetch(`${apiUrl}/health`, {
        headers: headersAny(),
        mode: 'cors'
      });
    }
    
    const contentType = res.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      const text = await res.text();
      throw new Error(`Backend لا يرد بـ JSON. تحقق من أن الـ Backend يعمل على: ${apiUrl}\n\nالاستجابة: ${text.substring(0, 200)}`);
    }
    
    const data = await res.json();
    $("statusOut").textContent = pretty(data);
  } catch (e) {
    $("statusOut").textContent = `خطأ: ${e.message}\n\nتحقق من:\n1. Backend يعمل على ${apiUrl}\n2. لا يوجد حظر CORS\n3. الـ URL صحيح`;
  }
}

// ====== Incidents ======
async function listIncidents() {
  const { apiUrl } = getCfg();
  $("incidentsWrap").innerHTML = "";
  try {
    const res = await fetch(`${apiUrl}/incidents`, { 
      headers: headersAny(),
      mode: 'cors'
    });
    
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    
    const contentType = res.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      throw new Error("استجابة غير صحيحة من Backend");
    }
    
    const data = await res.json();
    if (!Array.isArray(data) || data.length === 0) {
      $("incidentsWrap").innerHTML = `<div class="item"><div class="meta">لا يوجد بلاغات</div></div>`;
      return;
    }
    $("incidentsWrap").innerHTML = data
      .slice().reverse()
      .map(i => `
        <div class="item">
          <div class="meta">
            <div>${badgeForSeverity(i.severity)} <b>${i.title || "-"}</b></div>
            <div>${i.created_at_utc || ""}</div>
          </div>
          <div class="muted">الموقع: ${i.location || "-"}</div>
          <div style="margin-top:6px">${i.description || ""}</div>
        </div>
      `).join("");
  } catch (e) {
    $("incidentsWrap").innerHTML = `<div class="item"><div class="meta">خطأ: ${e.message}</div></div>`;
  }
}

async function createIncident(payload) {
  const { apiUrl } = getCfg();
  $("incOut").textContent = "جارِ الإرسال...";
  try {
    const res = await fetch(`${apiUrl}/incidents`, {
      method: "POST",
      headers: headersJSON(),
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    $("incOut").textContent = pretty(data);
    await listIncidents();
  } catch (e) {
    $("incOut").textContent = `خطأ: ${e.message}`;
  }
}

function badgeForSeverity(sev) {
  const s = (sev || "").toLowerCase();
  if (s === "critical") return `<span class="badge danger">حرجة</span>`;
  if (s === "high") return `<span class="badge warn">عالية</span>`;
  if (s === "medium") return `<span class="badge">متوسطة</span>`;
  return `<span class="badge">منخفضة</span>`;
}

// ====== Uploads ======
async function uploadFile(file, tag) {
  const { apiUrl } = getCfg();
  $("uploadOut").textContent = "جارِ الرفع...";
  try {
    const form = new FormData();
    form.append("file", file);
    if (tag) form.append("tag", tag);

    const res = await fetch(`${apiUrl}/uploads`, {
      method: "POST",
      headers: headersAny(),
      body: form
    });
    const data = await res.json();
    $("uploadOut").textContent = pretty(data);
  } catch (e) {
    $("uploadOut").textContent = `خطأ: ${e.message}`;
  }
}

async function listUploads() {
  const { apiUrl } = getCfg();
  $("uploadsWrap").innerHTML = "";
  try {
    const res = await fetch(`${apiUrl}/uploads`, { headers: headersAny() });
    const data = await res.json();
    if (!Array.isArray(data) || data.length === 0) {
      $("uploadsWrap").innerHTML = `<div class="item"><div class="meta">لا يوجد مرفوعات</div></div>`;
      return;
    }
    $("uploadsWrap").innerHTML = data
      .slice().reverse()
      .map(u => `
        <div class="item">
          <div class="meta">
            <div><b>${u.filename || "-"}</b></div>
            <div>${u.created_at_utc || ""}</div>
          </div>
          <div class="muted">نوع: ${u.content_type || "-"}</div>
          <div class="muted">حجم: ${u.size_bytes ?? "-"} bytes</div>
        </div>
      `).join("");
  } catch (e) {
    $("uploadsWrap").innerHTML = `<div class="item"><div class="meta">خطأ: ${e.message}</div></div>`;
  }
}

// ====== Initialization ======
let camera;
let chat;

function init() {
  const cfg = getCfg();
  $("apiUrl").value = cfg.apiUrl;
  $("apiKey").value = cfg.apiKey;

  // Configuration
  $("saveCfg").addEventListener("click", () => {
    const apiUrl = $("apiUrl").value.trim() || DEFAULT_API;
    const apiKey = $("apiKey").value.trim();
    setCfg(apiUrl, apiKey);
    $("statusOut").textContent = "تم حفظ الإعدادات.";
    loadHealth();
  });

  // Health
  $("refreshStatus").addEventListener("click", loadHealth);

  // Camera
  camera = new CameraManager();

  // Chat
  chat = new ChatManager();

  // Incidents
  $("sendIncident").addEventListener("click", async (e) => {
    e.preventDefault();
    const payload = {
      title: $("incTitle").value.trim(),
      location: $("incLocation").value.trim() || null,
      description: $("incDesc").value.trim() || null,
      severity: $("incSeverity").value
    };
    await createIncident(payload);
  });

  $("refreshIncidents").addEventListener("click", listIncidents);

  // Uploads
  const uploadForm = document.querySelector('form') || {
    submit: (f) => {}
  };
  
  const uploadBtn = $("doUpload");
  if (uploadBtn) {
    uploadBtn.addEventListener("click", async () => {
      const file = $("uploadFile").files?.[0];
      const tag = $("uploadTag").value.trim();
      if (!file) {
        $("uploadOut").textContent = "اختار ملف أولاً.";
        return;
      }
      await uploadFile(file, tag);
    });
  }

  $("refreshStatus").click(); // Initial load
  listIncidents();
  listUploads();
  
  log("Initialization complete");
}

document.addEventListener("DOMContentLoaded", init);
