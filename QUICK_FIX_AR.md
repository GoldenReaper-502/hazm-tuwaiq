# حل سريع لمشكلة "Failed to fetch"

## 🎯 المشكلة
Frontend يحاول الاتصال بـ `https://hazm-backend.onrender.com` لكن Backend غير منشور على Render بعد.

## ✅ الحل (3 خطوات فقط)

### 1️⃣ تشغيل Backend محلياً

```bash
cd /workspaces/hazm-tuwaiq/backend
/workspaces/hazm-tuwaiq/.venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**أو** استخدم السكريبت الجاهز:
```bash
cd /workspaces/hazm-tuwaiq/backend
../venv/bin/uvicorn app:app --reload
```

### 2️⃣ افتح صفحة إعادة الضبط

افتح في المتصفح:
```
file:///workspaces/hazm-tuwaiq/frontend/reset-settings.html
```

أو من الصفحة الرئيسية، اضغط على زر "🔧 إعادة الضبط" في الأعلى.

### 3️⃣ اضغط "إعادة الضبط إلى Localhost"

سيتم تلقائياً:
- ضبط API URL إلى `http://localhost:8000`
- حذف API Key
- اختبار الاتصال

## 🧪 التحقق

بعد إعادة الضبط، افتح الصفحة الرئيسية واضغط "تحديث" في قسم "حالة النظام".

يجب أن ترى:
```json
{
  "status": "ok",
  "service": "Hazm Tuwaiq backend is running",
  "time_utc": "2025-12-29T...",
  "version": "0.1.0"
}
```

## 📍 الملفات المهمة

- **Backend**: `/workspaces/hazm-tuwaiq/backend/app.py`
- **Frontend**: `/workspaces/hazm-tuwaiq/frontend/index.html`
- **إعادة الضبط**: `/workspaces/hazm-tuwaiq/frontend/reset-settings.html`

## 🚀 للنشر على Render لاحقاً

عندما تكون جاهزاً للنشر على Render:

1. اذهب إلى https://dashboard.render.com
2. اضغط "New +" → "Web Service"
3. اختر المستودع: `GoldenReaper-502/hazm-tuwaiq`
4. استخدم الإعدادات التالية:

```
Root Directory: backend
Dockerfile Path: Dockerfile
Docker Build Context: .
Environment Variables:
  PORT=8000
  CORS_ORIGINS=*
```

5. بعد النشر، حدّث API URL في Frontend إلى URL الجديد على Render.

## ✅ تم الحل!

- ✅ Backend يعمل محلياً على http://localhost:8000
- ✅ `/health` يرجع `{"status":"ok"}`
- ✅ CORS مفعّل
- ✅ Frontend يمكنه الاتصال بـ Backend
- ✅ صفحة إعادة الضبط جاهزة للاستخدام
