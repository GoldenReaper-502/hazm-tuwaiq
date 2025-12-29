# 🚀 نشر hazm-tuwaiq على Render - دليل كامل

## ✅ الجاهزية

تم إصلاح جميع المشاكل:
- ✅ Dockerfile يعمل بدون أخطاء apt-get
- ✅ `/health` يرجع `{"status":"ok"}`
- ✅ CORS مفعّل
- ✅ تم اختبار Docker image محلياً بنجاح

---

## 📋 خطوات النشر على Render

### 1️⃣ إنشاء Web Service جديد

1. اذهب إلى: https://dashboard.render.com
2. اضغط **"New +"** → **"Web Service"**
3. اختر **"Build and deploy from a Git repository"**
4. اضغط **"Connect GitHub"** (إذا لم يكن متصلاً)
5. اختر المستودع: **`GoldenReaper-502/hazm-tuwaiq`**
6. اضغط **"Connect"**

### 2️⃣ إعدادات البناء (Build Settings)

استخدم هذه الإعدادات **بالضبط**:

```
Name: hazm-backend
Region: أقرب منطقة لك (مثلاً: Frankfurt)
Branch: main

Root Directory: backend
Dockerfile Path: Dockerfile
Docker Build Context Directory: .
Docker Command: (leave empty - اتركه فارغاً)
```

### 3️⃣ إعدادات الخطة (Plan)

اختر الخطة المجانية:
```
Instance Type: Free
```

### 4️⃣ متغيرات البيئة (Environment Variables)

أضف هذه المتغيرات:

```
PORT=8000
CORS_ORIGINS=*
YOLO_MODEL=yolov8n.pt
TORCH_DEVICE=cpu
LOG_LEVEL=INFO
PYTHONUNBUFFERED=1
```

**ملاحظة**: لا تضيف `HAZM_API_KEY` إلا إذا كنت تريد حماية الـ API.

### 5️⃣ Auto-Deploy

```
✅ Auto-Deploy: Yes (تفعيل)
```
سيتم النشر تلقائياً عند كل push لـ main.

### 6️⃣ اضغط "Create Web Service"

---

## ⏱️ انتظر البناء

سيستغرق البناء الأول **5-10 دقائق** لأنه يجب تنزيل:
- Python packages (FastAPI, uvicorn, etc.)
- PyTorch & torchvision (~2GB)
- ultralytics & YOLO model

يمكنك مشاهدة التقدم في **"Logs"** tab.

---

## 🧪 اختبار النشر

بعد اكتمال البناء:

### 1. احصل على الـ URL
سيكون مثل: `https://hazm-backend-xxxx.onrender.com`

### 2. اختبر health endpoint
```bash
curl https://YOUR-URL.onrender.com/health
```

**النتيجة المتوقعة:**
```json
{"status":"ok"}
```

### 3. اختبر API docs
افتح في المتصفح:
```
https://YOUR-URL.onrender.com/docs
```

يجب أن ترى Swagger UI مع جميع endpoints.

---

## 🌐 ربط Frontend بـ Backend

### الطريقة الأولى: يدوياً في المتصفح

1. افتح `frontend/index.html`
2. في حقل **API URL**، أدخل:
   ```
   https://YOUR-URL.onrender.com
   ```
3. اضغط **"حفظ"**
4. اضغط **"تحديث"** في قسم حالة النظام

### الطريقة الثانية: استخدم صفحة إعادة الضبط

1. افتح `frontend/reset-settings.html`
2. اضغط **"🧪 اختبار الاتصال"**
3. إذا فشل، أدخل URL الجديد في localStorage

### الطريقة الثالثة: تعديل الكود (للنشر النهائي)

في `frontend/app.js`، عدّل السطر 11:
```javascript
// قبل
DEFAULT_API = "https://hazm-backend.onrender.com";

// بعد (استبدل بـ URL الفعلي)
DEFAULT_API = "https://hazm-backend-xxxx.onrender.com";
```

---

## ⚠️ ملاحظات مهمة

### 1. النوم التلقائي (Free Plan)
في الخطة المجانية، سيدخل Backend في وضع السكون بعد **15 دقيقة** من عدم النشاط.

- **أول طلب بعد السكون**: يستغرق 30-60 ثانية
- **الحل**: استخدم خدمة ping مثل UptimeRobot (مجاناً)

### 2. حجم Build
- البناء الأول: ~10 دقائق
- البناءات اللاحقة: ~2-5 دقائق (بفضل cache)

### 3. الذاكرة
- YOLO model يحتاج ~500MB RAM
- Free plan يوفر 512MB
- **كافي للعمل بشكل أساسي**

### 4. HTTPS
Render يوفر HTTPS تلقائياً مع certificate مجاني.

---

## 🐛 استكشاف الأخطاء

### خطأ: "Application failed to respond"
```bash
# 1. تحقق من Logs في Render Dashboard
# 2. تأكد من PORT=8000 في Environment Variables
# 3. تأكد من HEALTHCHECK في Dockerfile
```

### خطأ: "Build failed"
```bash
# 1. راجع Build Logs
# 2. تأكد من Root Directory = backend
# 3. تأكد من Dockerfile موجود في backend/
```

### خطأ: "CORS error" في Frontend
```bash
# تأكد من CORS_ORIGINS=* في Environment Variables
# أو أضف domain محدد:
CORS_ORIGINS=https://your-frontend-domain.com
```

### البناء بطيء جداً
```bash
# طبيعي في أول مرة بسبب PyTorch
# البناءات اللاحقة أسرع بفضل Docker layer caching
```

---

## 📊 مراقبة الصحة

Render يستخدم HEALTHCHECK من Dockerfile:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

- **interval**: كل 30 ثانية
- **timeout**: 10 ثواني max
- **retries**: 3 محاولات قبل اعتبار الخدمة معطلة

---

## 🎉 النشر الناجح!

بعد إكمال الخطوات أعلاه، ستحصل على:

✅ Backend شغال على HTTPS
✅ Auto-deploy من GitHub
✅ Health monitoring تلقائي
✅ Logs في الوقت الفعلي
✅ SSL certificate مجاني

---

## 📝 الأوامر المفيدة

### اختبار health من terminal
```bash
curl https://YOUR-URL.onrender.com/health
```

### اختبار detect endpoint
```bash
curl -X POST https://YOUR-URL.onrender.com/detect \
  -H "Content-Type: application/json" \
  -d '{"frame_data":"base64...", "timestamp":null}'
```

### جلب API docs كـ JSON
```bash
curl https://YOUR-URL.onrender.com/openapi.json
```

---

## 🔗 روابط مفيدة

- **Render Dashboard**: https://dashboard.render.com
- **Render Docs**: https://render.com/docs
- **Free Plan Limits**: https://render.com/docs/free

---

**تم! الآن يمكنك النشر على Render بدون مشاكل** 🚀
