# 🧪 API Testing Guide

## Quick Tests

### 1. Health Check
```bash
curl http://localhost:5000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-30T...",
  "service": "SmartSafety.API"
}
```

---

### 2. System Status
```bash
curl http://localhost:5000/api/system/status
```

**Expected Response:**
```json
{
  "llmAvailable": true,
  "llmProvider": "OpenAI gpt-4o-mini",
  "cctvAvailable": true,
  "version": "1.0.0",
  "environment": "Production",
  "timestamp": "2025-12-30T..."
}
```

---

### 3. Chat Endpoint (with OpenAI)
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "ما هي أهم 3 إجراءات سلامة في موقع بناء؟",
    "sessionId": "test_session_123"
  }'
```

**Expected Response:**
```json
{
  "id": "chat_000001",
  "sessionId": "test_session_123",
  "userMessage": "ما هي أهم 3 إجراءات سلامة في موقع بناء؟",
  "assistantResponse": "1. ارتداء معدات الحماية الشخصية...",
  "sources": ["OpenAI gpt-4o-mini"],
  "confidence": 0.9,
  "timestamp": "2025-12-30T..."
}
```

---

### 4. CCTV Cameras List
```bash
curl http://localhost:5000/api/cctv/cameras
```

**Expected Response:**
```json
[
  {
    "id": 1,
    "name": "كاميرا المدخل الرئيسي",
    "url": "rtsp://demo-camera-1",
    "location": "المدخل الرئيسي",
    "isActive": true,
    "createdAt": "2025-12-30T..."
  }
]
```

---

### 5. Error Handling Test (Invalid Request)
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "",
    "sessionId": "test"
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "type": "https://tools.ietf.org/html/rfc7231#section-6.5.1",
  "title": "Invalid Request",
  "status": 400,
  "detail": "Message is required and cannot be empty",
  "instance": "/api/chat"
}
```

---

## Environment Setup

### Set OpenAI API Key

**Option 1: Environment Variable**
```bash
export OPENAI_API_KEY="sk-..."
dotnet run
```

**Option 2: appsettings.json**
```json
{
  "AI": {
    "OpenAIApiKey": "sk-...",
    "Provider": "openai"
  }
}
```

**Option 3: User Secrets (Development)**
```bash
dotnet user-secrets set "AI:OpenAIApiKey" "sk-..."
```

---

## Full Test Suite

```bash
#!/bin/bash

echo "🧪 Testing Smart Safety API"
echo ""

# 1. Health Check
echo "1️⃣ Health Check:"
curl -s http://localhost:5000/health | jq
echo ""

# 2. System Status
echo "2️⃣ System Status:"
curl -s http://localhost:5000/api/system/status | jq
echo ""

# 3. Chat
echo "3️⃣ Chat Test:"
curl -s -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello, are you working?","sessionId":"test123"}' | jq
echo ""

# 4. Cameras
echo "4️⃣ Cameras List:"
curl -s http://localhost:5000/api/cctv/cameras | jq
echo ""

# 5. Error Test
echo "5️⃣ Error Handling:"
curl -s -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"","sessionId":"test"}' | jq
echo ""

echo "✅ All tests completed!"
```

**Save as `test-api.sh` and run:**
```bash
chmod +x test-api.sh
./test-api.sh
```

---

## CORS Test (from Frontend)

**In Browser Console:**
```javascript
fetch('http://localhost:5000/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error);
```

**Should work without CORS errors from:**
- http://localhost:8080
- http://localhost:3000

---

## Performance Test

```bash
# Using Apache Bench
ab -n 100 -c 10 http://localhost:5000/health

# Using wrk
wrk -t4 -c100 -d30s http://localhost:5000/health
```

---

## Troubleshooting

### Issue: CORS Error
**Solution:** Check allowed origins in Program.cs
```csharp
.WithOrigins("http://localhost:8080", "http://localhost:3000")
```

### Issue: 500 Internal Server Error
**Solution:** Check logs:
```bash
dotnet run --verbosity detailed
```

### Issue: OpenAI API Error
**Solution:** Verify API key:
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

---

## Production Checklist

- [ ] CORS origins updated for production domains
- [ ] OpenAI API key in environment variable
- [ ] Database connection string configured
- [ ] HTTPS enabled
- [ ] Logging configured
- [ ] Health checks working
- [ ] Error handling returns JSON only
- [ ] API documentation (Swagger) accessible

---

**🎉 API is production-ready when all tests pass!**
