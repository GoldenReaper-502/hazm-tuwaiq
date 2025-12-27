// ====== إعدادات ======
const DEFAULT_API = "https://hazm-tuwaiq.onrender.com"; // عدّلها لرابط الـ backend عندك
const LS_API = "hazm_api_url";
const LS_KEY = "hazm_api_key";

function $(id){ return document.getElementById(id); }

function getCfg(){
  const apiUrl = (localStorage.getItem(LS_API) || DEFAULT_API).replace(/\/+$/,'');
  const apiKey = localStorage.getItem(LS_KEY) || "";
  return { apiUrl, apiKey };
}
function setCfg(apiUrl, apiKey){
  localStorage.setItem(LS_API, apiUrl.replace(/\/+$/,''));
  localStorage.setItem(LS_KEY, apiKey || "");
}

function headersJSON(){
  const { apiKey } = getCfg();
  const h = { "Content-Type": "application/json" };
  if (apiKey) h["x-api-key"] = apiKey;
  return h;
}

function headersAny(){
  const { apiKey } = getCfg();
  const h = {};
  if (apiKey) h["x-api-key"] = apiKey;
  return h;
}

function pretty(obj){
  return JSON.stringify(obj, null, 2);
}

function badgeForSeverity(sev){
  const s = (sev || "").toLowerCase();
  if (s === "critical") return `<span class="badge danger">CRITICAL</span>`;
  if (s === "high") return `<span class="badge warn">HIGH</span>`;
  if (s === "medium") return `<span class="badge">MEDIUM</span>`;
  return `<span class="badge">LOW</span>`;
}

// ====== Health ======
async function loadHealth(){
  const { apiUrl } = getCfg();
  $("healthOut").textContent = "جارِ الاتصال...";
  try{
    // بعض backends عندك root "/" وبعضها "/health" - نجرب الاثنين
    let res = await fetch(`${apiUrl}/`);
    if (!res.ok){
      res = await fetch(`${apiUrl}/health`);
    }
    const data = await res.json();
    $("healthOut").textContent = pretty(data);
  }catch(e){
    $("healthOut").textContent = `خطأ: ${e.message}`;
  }
}

// ====== Incidents ======
async function listIncidents(){
  const { apiUrl } = getCfg();
  $("listWrap").innerHTML = "";
  try{
    const res = await fetch(`${apiUrl}/incidents`, { headers: headersAny() });
    const data = await res.json();
    if (!Array.isArray(data) || data.length === 0){
      $("listWrap").innerHTML = `<div class="item"><div class="meta">لا يوجد بلاغات</div></div>`;
      return;
    }
    $("listWrap").innerHTML = data
      .slice().reverse()
      .map(i => `
        <div class="item">
          <div class="meta">
            <div>${badgeForSeverity(i.severity)} <b>${i.title || "-"}</b></div>
            <div>${i.created_at_utc || ""}</div>
          </div>
          <div class="muted">الموقع: ${i.location || "-"}</div>
          <div style="margin-top:6px">${i.description || ""}</div>
          <div class="muted" style="margin-top:8px">ID: ${i.id ?? "-"}</div>
        </div>
      `).join("");
  }catch(e){
    $("listWrap").innerHTML = `<div class="item"><div class="meta">خطأ: ${e.message}</div></div>`;
  }
}

async function createIncident(payload){
  const { apiUrl } = getCfg();
  $("createOut").textContent = "جارِ الإرسال...";
  try{
    const res = await fetch(`${apiUrl}/incidents`, {
      method:"POST",
      headers: headersJSON(),
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    $("createOut").textContent = pretty(data);
    await listIncidents();
  }catch(e){
    $("createOut").textContent = `خطأ: ${e.message}`;
  }
}

// ====== Uploads (حسب app.py عندك) ======
// نفترض عندك endpoints: POST /uploads و GET /uploads
async function uploadFile(file, tag){
  const { apiUrl } = getCfg();
  $("uploadOut").textContent = "جارِ الرفع...";
  try{
    const form = new FormData();
    form.append("file", file);
    if (tag) form.append("tag", tag);

    const res = await fetch(`${apiUrl}/uploads`, {
      method:"POST",
      headers: headersAny(), // لا نحط Content-Type مع FormData
      body: form
    });
    const data = await res.json();
    $("uploadOut").textContent = pretty(data);
  }catch(e){
    $("uploadOut").textContent = `خطأ: ${e.message}`;
  }
}

async function listUploads(){
  const { apiUrl } = getCfg();
  $("uploadsWrap").innerHTML = "";
  try{
    const res = await fetch(`${apiUrl}/uploads`, { headers: headersAny() });
    const data = await res.json();
    if (!Array.isArray(data) || data.length === 0){
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
          <div class="muted">Tag: ${u.tag || "-"}</div>
          <div class="muted">ID: ${u.id || "-"}</div>
        </div>
      `).join("");
  }catch(e){
    $("uploadsWrap").innerHTML = `<div class="item"><div class="meta">خطأ: ${e.message}</div></div>`;
  }
}

// ====== init ======
function init(){
  const cfg = getCfg();
  $("apiUrl").value = cfg.apiUrl;
  $("apiKey").value = cfg.apiKey;

  $("saveCfg").addEventListener("click", () => {
    const apiUrl = $("apiUrl").value.trim() || DEFAULT_API;
    const apiKey = $("apiKey").value.trim();
    setCfg(apiUrl, apiKey);
    $("healthOut").textContent = "تم حفظ الإعدادات.";
  });

  $("btnHealth").addEventListener("click", loadHealth);

  $("incidentForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      title: $("title").value.trim(),
      location: $("location").value.trim() || null,
      description: $("description").value.trim() || null,
      severity: $("severity").value
    };
    await createIncident(payload);
  });

  $("btnCreateDemo").addEventListener("click", async () => {
    await createIncident({
      title: "بلاغ تجريبي — حزم طويق",
      location: "Gate 3",
      description: "اختبار سريع للتأكد من الربط بين الواجهة والـ API.",
      severity: "medium"
    });
  });

  $("btnClear").addEventListener("click", () => {
    $("title").value = "";
    $("location").value = "";
    $("description").value = "";
    $("severity").value = "medium";
    $("createOut").textContent = "تم المسح.";
  });

  $("btnList").addEventListener("click", listIncidents);
  $("btnClearList").addEventListener("click", () => $("listWrap").innerHTML = "");

  $("uploadForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const file = $("uploadFile").files?.[0];
    const tag = $("uploadTag").value.trim();
    if (!file){
      $("uploadOut").textContent = "اختار ملف أولاً.";
      return;
    }
    await uploadFile(file, tag);
  });

  $("btnListUploads").addEventListener("click", listUploads);

  $("openDocs").addEventListener("click", (e) => {
    e.preventDefault();
    const { apiUrl } = getCfg();
    window.open(`${apiUrl}/docs`, "_blank");
  });

  // تحميل أولي
  loadHealth();
  listIncidents();
}

document.addEventListener("DOMContentLoaded", init);
