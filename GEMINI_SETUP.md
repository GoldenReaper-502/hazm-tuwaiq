# 🆓 تفعيل Google Gemini المجاني - حزم طويق

## ✅ تم التعديل! الكود جاهز لـ Gemini

---

## 📝 الخطوات (3 دقائق)

### 1️⃣ احصل على Gemini API Key (مجاناً!)

1. اذهب إلى: **https://aistudio.google.com/app/apikey**
2. سجل دخول بحساب Google
3. اضغط **Create API Key**
4. اختر **Create API key in new project**
5. انسخ المفتاح (يبدأ بـ `AIza...`)

⏱️ **الوقت:** 1 دقيقة فقط!

---

### 2️⃣ أضف المفتاح في Render

1. اذهب إلى: **https://dashboard.render.com**
2. اختر Service: **hazm-tuwaiq-3**
3. اضغط **Environment** من القائمة الجانبية
4. اضغط **Add Environment Variable**
5. أضف:
   ```
   Key: GEMINI_API_KEY
   Value: AIza...your-actual-key
   ```
6. اضغط **Save Changes**

⏳ **انتظر 2-3 دقائق** - Render ستعيد نشر التطبيق تلقائياً

---

### 3️⃣ اختبار

#### عبر Terminal:
```bash
curl -X POST https://hazm-tuwaiq-3.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "ما هي أهم 3 إجراءات سلامة؟",
    "session_id": "test123"
  }'
```

#### عبر Frontend:
1. افتح: **http://localhost:8080/index.html**
2. اضغط: **💬 المساعد الذكي**
3. اكتب: "ما هي إجراءات السلامة الأساسية؟"
4. اضغط **إرسال**

#### ✅ النتيجة المتوقعة:
```json
{
  "assistant_response": "إليك أهم إجراءات السلامة...",
  "sources": ["Google Gemini gemini-2.0-flash-exp (FREE)"],
  "model_used": "gemini-2.0-flash-exp",
  "provider": "gemini"
}
```

---

## 🎯 التغييرات المنفذة

### ✅ ملف: backend/llm.py
```python
# إضافة دعم Gemini كأولوية أولى
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

# المحاولة بالترتيب: Gemini → OpenAI → Anthropic
if GEMINI_KEY:
    import google.generativeai as genai
    # ... استخدام Gemini
```

### ✅ ملف: backend/requirements.txt
```python
google-generativeai>=0.3.0  # Google Gemini - FREE LLM!
```

### ✅ ملف: backend/app.py
```python
# تحديث /system/status ليعرض المزود المستخدم
if os.getenv("GEMINI_API_KEY"):
    llm_provider = "Google Gemini (FREE)"
```

---

## 🆚 ترتيب الأولوية

النظام يحاول بهذا الترتيب:

1. **Gemini** (إذا موجود `GEMINI_API_KEY`) ← **الأولوية!**
2. **OpenAI** (إذا موجود `OPENAI_API_KEY`)
3. **Anthropic** (إذا موجود `ANTHROPIC_API_KEY`)
4. **Fallback** (رسالة خطأ مع تعليمات)

---

## 💰 المقارنة

| المزود | السعر | الحد | العربية | الجودة |
|--------|-------|------|---------|---------|
| **Gemini** | 🆓 | 60/min | ✅ ممتاز | ⭐⭐⭐⭐ |
| OpenAI | 💰 | حسب الرصيد | ✅ ممتاز | ⭐⭐⭐⭐⭐ |
| Anthropic | 💰 | حسب الرصيد | ✅ جيد | ⭐⭐⭐⭐⭐ |

**60 طلب/دقيقة = 3,600 طلب/ساعة = 86,400 طلب/يوم!** 🚀

---

## 🔧 تخصيص النموذج (اختياري)

إذا أردت استخدام نموذج Gemini مختلف:

```bash
# في Render Environment Variables
Key: GEMINI_MODEL
Value: gemini-1.5-pro  # أو gemini-1.5-flash
```

**النماذج المتاحة:**
- `gemini-2.0-flash-exp` (الافتراضي - الأسرع والأحدث)
- `gemini-1.5-pro` (أقوى، أبطأ قليلاً)
- `gemini-1.5-flash` (سريع جداً)

---

## ✅ التحقق من النجاح

### عبر System Status:
```bash
curl https://hazm-tuwaiq-3.onrender.com/system/status
```

**النتيجة:**
```json
{
  "llm_available": true,
  "llm_provider": "Google Gemini (FREE)",
  "cctv_available": true,
  "timestamp": "..."
}
```

### عبر Frontend:
افتح Developer Console (F12) وشاهد:
```javascript
✓ System Status: Gemini available
✓ LLM Provider: Google Gemini (FREE)
```

---

## 🎉 النتيجة

بعد التفعيل:
- ✅ **AI مجاني تماماً**
- ✅ **بدون بطاقة ائتمانية**
- ✅ **إجابات ممتازة بالعربية**
- ✅ **60 طلب/دقيقة**
- ✅ **يدعم ISO 45001 و OSHA**
- ✅ **تحليل مخاطر ذكي**

---

## 🔒 الأمان

**المفتاح آمن في:**
- ✅ Render Environment Variables (مشفر)

**لا تضع المفتاح في:**
- ❌ الكود
- ❌ GitHub
- ❌ الملفات المحلية

---

## 📞 الدعم

### مشكلة: "Gemini API error"
**الحل:**
1. تحقق من المفتاح في Render Environment
2. تأكد أنه يبدأ بـ `AIza`
3. راجع Render Logs

### مشكلة: "لا يظهر Gemini في System Status"
**الحل:**
1. تأكد من حفظ Environment Variable
2. انتظر 2-3 دقائق لإعادة النشر
3. أعد تحميل الصفحة

---

## 🚀 الخطوة التالية

**احصل على مفتاح Gemini الآن:**
👉 **https://aistudio.google.com/app/apikey**

ثم أضفه في Render وابدأ الاستمتاع بـ AI مجاني! 🎉
