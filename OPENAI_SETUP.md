# 🔗 ربط حزم طويق بـ OpenAI

## ✅ الكود جاهز - فقط أضف API Key!

Backend حزم طويق **مُجهز بالكامل** للعمل مع OpenAI. تحتاج فقط إلى إضافة مفتاح API.

---

## 📋 الخطوات (3 دقائق)

### 1️⃣ الحصول على OpenAI API Key

1. اذهب إلى: **https://platform.openai.com/api-keys**
2. اضغط **Create new secret key**
3. اكتب اسم للمفتاح (مثلاً: `hazm-tuwaiq-prod`)
4. انسخ المفتاح (يبدأ بـ `sk-...`)
   
   ⚠️ **مهم جداً**: المفتاح يظهر **مرة واحدة فقط**! احفظه في مكان آمن.

---

### 2️⃣ إضافة المفتاح على Render

1. اذهب إلى: **https://dashboard.render.com**
2. اختر Service: **`hazm-tuwaiq-3`**
3. انقر **Environment** من القائمة الجانبية
4. اضغط **Add Environment Variable**
5. أضف:
   ```
   Key: OPENAI_API_KEY
   Value: sk-...your-actual-key-here
   ```
6. (اختياري) أضف أيضاً:
   ```
   Key: OPENAI_MODEL
   Value: gpt-4o-mini
   ```
7. اضغط **Save Changes**

⏳ **انتظر 2-3 دقائق** - Render ستعيد نشر التطبيق تلقائياً.

---

### 3️⃣ التحقق من أن OpenAI يعمل

#### عبر Terminal:
```bash
curl -X POST https://hazm-tuwaiq-3.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "ما هي أهم 5 إجراءات سلامة في موقع بناء؟",
    "session_id": "test123"
  }'
```

#### عبر Frontend:
1. افتح: **http://localhost:8080/index.html**
2. انقر على **💬 المساعد الذكي**
3. اكتب سؤال: "ما هي إجراءات السلامة الأساسية؟"
4. انقر **إرسال**

#### النتيجة المتوقعة:
- ✅ **إجابة طويلة ومفصلة** = OpenAI يعمل!
- ❌ **"⚠️ LLM service unavailable"** = تحقق من الخطوات

---

## 🔍 استكشاف الأخطاء

### المشكلة: "LLM service unavailable"

**الحلول:**

1. **تحقق من المفتاح:**
   - هل نسخت المفتاح كاملاً؟
   - هل المفتاح صحيح (يبدأ بـ `sk-`)?

2. **تحقق من Render:**
   ```
   Dashboard → hazm-tuwaiq-3 → Environment
   ```
   هل `OPENAI_API_KEY` موجود؟

3. **تحقق من Logs:**
   ```
   Dashboard → hazm-tuwaiq-3 → Logs
   ```
   ابحث عن رسائل خطأ.

4. **تحقق من الرصيد:**
   - https://platform.openai.com/usage
   - هل لديك رصيد كافٍ؟

5. **أعد النشر يدوياً:**
   ```
   Dashboard → hazm-tuwaiq-3 → Manual Deploy → Deploy latest commit
   ```

---

## 💰 التكلفة المتوقعة

### النموذج: `gpt-4o-mini`
- **السعر**: $0.150 لكل مليون token (input)
- **مثال**: 1000 سؤال = حوالي $0.50 - $2.00
- **مناسب لـ**: الاختبار والإنتاج

### بدائل أخرى:
```
# أرخص
OPENAI_MODEL=gpt-3.5-turbo

# أقوى (لكن أغلى)
OPENAI_MODEL=gpt-4o
```

---

## 🧪 اختبار سريع

### Test Script
```bash
# في Terminal
cd /workspaces/hazm-tuwaiq
curl -X POST https://hazm-tuwaiq-3.onrender.com/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, are you working?", "session_id": "test"}'
```

### إذا نجح:
```json
{
  "id": "chat_000001",
  "session_id": "test",
  "user_message": "Hello, are you working?",
  "assistant_response": "Yes! I'm HAZM TUWAIQ Safety Copilot...",
  "timestamp": "2025-12-30T..."
}
```

### إذا فشل:
```json
{
  "message": "⚠️ AI Chat Error: No LLM provider configured..."
}
```

---

## 📊 ما يحصل خلف الكواليس

### عند إرسال رسالة للـ Chatbot:

1. **Frontend** يرسل POST إلى `/chat`
2. **Backend** (`app.py`) يستقبل الطلب
3. **LLM Module** (`llm.py`) يتحقق من `OPENAI_API_KEY`
4. **إذا موجود**:
   - يستدعي OpenAI API
   - يرسل System Prompt (ISO 45001, OSHA)
   - يستقبل الرد
   - يرجع structured response
5. **إذا غير موجود**:
   - يرجع Fallback message
   - مع تعليمات كيفية إصلاح المشكلة

---

## 🎯 الكود الجاهز

### Backend: `llm.py`
```python
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if OPENAI_KEY:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_KEY)
    
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=1500
    )
```

### System Prompt المُعد:
```
You are HAZM TUWAIQ Safety Copilot
- ISO 45001:2018
- OSHA regulations
- Risk assessment (HAZOP, FMEA)
- Safety culture
- Hazard control hierarchy
```

---

## ✅ الخلاصة

| الخطوة | الحالة |
|--------|--------|
| الكود جاهز | ✅ |
| OpenAI SDK مثبت | ✅ |
| System Prompt جاهز | ✅ |
| Error Handling | ✅ |
| **تحتاج فقط** | ➡️ **OPENAI_API_KEY** |

---

## 🚀 التالي

بعد إضافة API Key:

1. ✅ Chatbot سيعمل بذكاء حقيقي
2. ✅ إجابات مفصلة ومخصصة
3. ✅ مراجع ISO 45001 و OSHA
4. ✅ تحليل المخاطر الذكي
5. ✅ توصيات السلامة الاحترافية

---

**💡 نصيحة نهائية:**
احفظ `OPENAI_API_KEY` في مكان آمن! لا تشاركه مع أحد ولا تضعه في GitHub.

**🔗 روابط مفيدة:**
- OpenAI Dashboard: https://platform.openai.com
- Render Dashboard: https://dashboard.render.com
- Hazm Tuwaiq Backend: https://hazm-tuwaiq-3.onrender.com
