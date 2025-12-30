# 🏆 HAZM TUWAIQ - دليل النشر الذهبي

## 📚 المحتويات

1. [تشغيل Frontend في Codespaces](#تشغيل-frontend-في-codespaces)
2. [إعداد المتغيرات البيئية على Render](#إعداد-المتغيرات-البيئية-على-render)
3. [التحقق السريع من Endpoints](#التحقق-السريع-من-endpoints)
4. [اختبار الدردشة بالذكاء الاصطناعي الحقيقي](#اختبار-الدردشة-بالذكاء-الاصطناعي-الحقيقي)

---

## تشغيل Frontend في Codespaces

### الخطوة 1: تشغيل خادم HTTP محلي

```bash
cd /workspaces/hazm-tuwaiq/frontend
python3 -m http.server 8080
```

### الخطوة 2: فتح المتصفح

في Codespaces، اضغط على زر "Ports" في الشريط السفلي، ثم اضغط على أيقونة "الكرة الأرضية" بجوار المنفذ 8080.

أو استخدم:
```bash
$BROWSER http://localhost:8080
```

### الخطوة 3: اختبار الصفحات

- **الإصدار الذهبي**: [http://localhost:8080/index_golden.html](http://localhost:8080/index_golden.html)
- **الإصدار الأساسي**: [http://localhost:8080/index.html](http://localhost:8080/index.html)

---

## إعداد المتغيرات البيئية على Render

### للدردشة بالذكاء الاصطناعي الحقيقي

1. انتقل إلى لوحة تحكم Render: [https://dashboard.render.com](https://dashboard.render.com)

2. اختر خدمة `hazm-tuwaiq-3`

3. انتقل إلى **Environment** → **Environment Variables**

4. أضف المتغيرات التالية:

```
OPENAI_API_KEY=sk-...your-key-here
OPENAI_MODEL=gpt-4o-mini
LLM_PROVIDER=openai
```

**ملاحظة**: للحصول على مفتاح OpenAI:
- انتقل إلى [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- قم بإنشاء مفتاح جديد
- انسخ المفتاح (سيظهر مرة واحدة فقط!)

5. اضغط **Save Changes**

6. أعد نشر الخدمة:

```bash
# في Codespaces
git add .
git commit -m "Enable real AI chat"
git push origin main
```

Render ستعيد النشر تلقائيًا.

---

## التحقق السريع من Endpoints

### استخدام سكريبت Validate

```bash
cd /workspaces/hazm-tuwaiq/backend
python3 validate.py
```

سيختبر السكريبت:
- ✅ `/health` - فحص الصحة
- ✅ `/system/status` - حالة النظام
- ✅ `/chat` - الدردشة
- ✅ `/detect` - الكشف

### استخدام curl يدويًا

#### فحص الصحة
```bash
curl https://hazm-tuwaiq-3.onrender.com/health
```

الاستجابة المتوقعة:
```json
{"status": "ok", "timestamp": "..."}
```

#### حالة النظام
```bash
curl https://hazm-tuwaiq-3.onrender.com/system/status
```

الاستجابة المتوقعة:
```json
{
  "llm_available": true,
  "cctv_available": true,
  "last_error": null
}
```

#### اختبار الدردشة
```bash
curl -X POST https://hazm-tuwaiq-3.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "ما هي إجراءات السلامة الأساسية؟",
    "session_id": "test"
  }'
```

الاستجابة المتوقعة (مع AI حقيقي):
```json
{
  "message": "إجراءات السلامة الأساسية تشمل...",
  "sources": ["ISO 45001", "OSHA"],
  "confidence": 0.95
}
```

الاستجابة المتوقعة (بدون AI - وضع الاحتياطي):
```json
{
  "message": "⚠️ LLM service unavailable...",
  "fallback_mode": true
}
```

---

## اختبار الدردشة بالذكاء الاصطناعي الحقيقي

### كيف تعرف أن AI يعمل؟

#### مؤشرات AI حقيقي ✅
- رسائل طويلة ومفصلة
- إجابات سياقية ومنطقية
- مراجع محددة (ISO 45001, OSHA)
- درجة ثقة (confidence) عالية
- لا توجد رسالة "fallback_mode"

#### مؤشرات وضع الاحتياطي ⚠️
- رسالة تبدأ بـ "⚠️ LLM service unavailable"
- `"fallback_mode": true` في الاستجابة
- رسائل قصيرة ونمطية
- نفس الرد لأسئلة مختلفة

### مثال على الاختبار

1. افتح Dashboard الذهبي
2. انقر على **Safety Copilot Chat**
3. اكتب سؤال معقد:
   ```
   ما هي أهم 5 إجراءات سلامة في موقع بناء به رافعات؟
   ```

4. إذا كانت الإجابة:
   - **مفصلة ومرقمة** → ✅ AI حقيقي يعمل
   - **"⚠️ LLM service unavailable"** → ⚠️ تحقق من OPENAI_API_KEY

---

## حل المشاكل

### المشكلة: "OPENAI_API_KEY not set"

**الحل:**
```bash
# في Render Dashboard
Environment Variables → Add
Name: OPENAI_API_KEY
Value: sk-...your-key
```

### المشكلة: "Chat always returns fallback"

**الحل:**
1. تحقق من أن `OPENAI_API_KEY` صالح
2. تحقق من رصيد OpenAI: [https://platform.openai.com/usage](https://platform.openai.com/usage)
3. تحقق من Logs في Render:
```bash
# في Render Dashboard
Logs → Latest Logs
```

### المشكلة: "Module cv2 not found"

**الحل:**
```bash
# في backend/requirements.txt
opencv-python-headless==4.8.1.78
```

ثم:
```bash
git add backend/requirements.txt
git commit -m "Add opencv"
git push
```

---

## البنية التفصيلية

### Frontend Files (Golden Edition)
```
frontend/
├── index_golden.html     # صفحة رئيسية كاملة مع 7 وحدات
├── styles_golden.css     # نظام تصميم كامل مع Dark Mode
├── app_golden.js         # منطق التطبيق الكامل
└── assets/               # الصور والأيقونات
```

### Backend Structure
```
backend/
├── app.py               # تطبيق FastAPI الرئيسي
├── llm.py               # تكامل LLM (OpenAI/Anthropic)
├── cctv.py              # معالجة الكاميرات
├── behavior.py          # تحليل السلوك
├── tracking.py          # تتبع الكائنات
├── report_generator.py  # توليد التقارير
└── validate.py          # سكريبت التحقق
```

---

## الوحدات المتاحة

### 1. System Status ✅
- حالة LLM
- حالة CCTV
- آخر خطأ
- Endpoint: `/system/status`

### 2. CCTV Management ✅
- قائمة الكاميرات
- إضافة/حذف كاميرا
- Endpoints: `/cameras`, `/camera/add`, `/camera/delete`

### 3. Object Detection ✅
- رفع صورة
- كشف المخاطر (YOLO)
- Endpoint: `/detect`

### 4. Alerts & Incidents ✅
- قائمة التنبيهات
- تأكيد التنبيهات
- إنشاء حادثة/near-miss
- Endpoints: `/alerts`, `/alerts/ack`, `/incident`, `/near-miss`

### 5. Reports ✅
- توليد تقرير PDF
- تصدير Excel
- Endpoints: `/export/pdf`, `/export/excel`

### 6. Admin Panel ✅
- إدارة المستخدمين
- إنشاء أدوار
- Endpoint: `/admin/roles`

### 7. Safety Copilot Chat ✅
- دردشة ذكية مع AI
- سياق ISO 45001/OSHA
- Endpoint: `/chat`

---

## الميزات المتقدمة

### Dark/Light Theme
```javascript
// في app_golden.js
document.getElementById('theme-toggle').addEventListener('click', () => {
  document.body.classList.toggle('dark-theme');
  localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
});
```

### Arabic/English Toggle
```javascript
// في app_golden.js
document.getElementById('lang-toggle').addEventListener('click', () => {
  state.language = state.language === 'ar' ? 'en' : 'ar';
  updateLanguage();
});
```

### Safe API Calls
```javascript
// في app_golden.js
async function apiFetch(endpoint, options = {}) {
  const rawResponse = await fetch(CONFIG.API_BASE_URL + endpoint, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  });
  
  const text = await rawResponse.text();
  const contentType = rawResponse.headers.get('content-type');
  
  if (contentType && contentType.includes('application/json')) {
    return JSON.parse(text);
  } else {
    throw new Error(`Expected JSON but got: ${text.slice(0, 100)}`);
  }
}
```

---

## الخلاصة

✅ **Frontend**: صفحة ذهبية كاملة مع 7 وحدات  
✅ **Backend**: LLM حقيقي مع Safety Copilot  
✅ **Testing**: سكريبت validate.py للتحقق السريع  
✅ **Documentation**: دليل شامل بالعربية والإنجليزية

**الرابط المباشر**: https://hazm-tuwaiq-3.onrender.com

---

## الدعم

للمشاكل أو الأسئلة:
1. راجع [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. تحقق من Logs في Render
3. استخدم `validate.py` للتشخيص

