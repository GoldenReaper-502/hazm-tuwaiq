# 🚀 دليل النشر السريع على Render

## المتطلبات
- حساب GitHub
- حساب مجاني على [Render.com](https://render.com)
- المشروع على GitHub

## خطوات النشر

### 1️⃣ رفع الكود على GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2️⃣ إنشاء خدمة على Render

1. اذهب إلى [Render Dashboard](https://dashboard.render.com)
2. اضغط **New +** → **Blueprint**
3. اربط حساب GitHub الخاص بك
4. اختر المستودع: `GoldenReaper-502/hazm-tuwaiq`
5. اضغط **Apply**

### 3️⃣ التكوين التلقائي

Render سيقرأ ملف `render.yaml` ويقوم بـ:
- إنشاء Backend API (hazm-backend)
- إنشاء Frontend Static Site (hazm-frontend)
- تثبيت جميع المكتبات المطلوبة
- ربطهما معاً تلقائياً

### 4️⃣ الحصول على الروابط

بعد النشر ستحصل على:
- **Backend URL**: `https://hazm-backend.onrender.com`
- **Frontend URL**: `https://hazm-frontend.onrender.com`

### 5️⃣ تحديث Frontend (إذا لزم الأمر)

إذا لم يتم الربط تلقائياً، افتح `frontend/app.js` وغير:
```javascript
const DEFAULT_API = "https://hazm-backend.onrender.com";
```

ثم:
```bash
git add frontend/app.js
git commit -m "Update API URL"
git push
```

## ⚙️ إعدادات اختيارية

### تفعيل API Key (حماية)
في Render Dashboard → hazm-backend → Environment:
```
HAZM_API_KEY=your-secret-key-here
```

ثم في Frontend:
- اذهب للإعدادات
- أدخل نفس الـ API Key

## 🔍 التحقق من النشر

1. افتح Frontend URL
2. جرب رفع صورة للتحليل
3. تحقق من عمل الكاميرا والتقارير

## ⚡ ملاحظات مهمة

- **الخطة المجانية**: 
  - قد ينام الباك إند بعد 15 دقيقة من عدم الاستخدام
  - أول طلب بعد النوم قد يأخذ 30-60 ثانية
  
- **تحسين الأداء**:
  - التطبيق يستخدم تحميل تدريجي للموارد
  - النموذج يحمل في الخلفية
  - التطبيق يبدأ فوراً

## 🐛 حل المشاكل

### Backend لا يستجيب
```bash
# تحقق من السجلات في Render Dashboard
View Logs → hazm-backend
```

### Frontend لا يتصل بـ Backend
1. تحقق من CORS_ORIGINS في Backend
2. تحقق من DEFAULT_API في frontend/app.js
3. تأكد من أن Backend يعمل (زر الصفحة)

## 📞 دعم إضافي

- [Render Docs](https://render.com/docs)
- [Render Community](https://community.render.com)

---
✅ **جاهز للنشر الآن!**
