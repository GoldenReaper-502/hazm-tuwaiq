# السلامة الذكية - Smart Safety Platform
## ASP.NET Core Implementation

### 🎯 نظرة عامة

تطبيق ASP.NET Core كامل لإدارة السلامة باستخدام الذكاء الاصطناعي.

### 📁 هيكل المشروع

```
AspNetCore/
└── SmartSafety.API/
    ├── Controllers/         # API Controllers
    │   ├── ChatController.cs
    │   ├── CCTVController.cs
    │   ├── DetectionController.cs
    │   ├── IncidentsController.cs
    │   └── SystemController.cs
    ├── Models/             # Data Models
    │   └── Models.cs
    ├── Services/           # Business Logic
    │   ├── Interfaces.cs
    │   ├── AIService.cs
    │   ├── CCTVService.cs
    │   └── DetectionService.cs
    ├── Data/              # Database Context
    │   └── AppDbContext.cs
    ├── Program.cs         # App Startup
    ├── appsettings.json  # Configuration
    └── SmartSafety.API.csproj
```

### 🚀 التشغيل

#### المتطلبات:
- .NET 8.0 SDK
- SQLite (مدمج)

#### خطوات التشغيل:

```bash
cd AspNetCore/SmartSafety.API

# استعادة الحزم
dotnet restore

# تشغيل المشروع
dotnet run
```

التطبيق سيعمل على:
- **HTTP**: http://localhost:5000
- **HTTPS**: https://localhost:5001
- **Swagger UI**: http://localhost:5000

### 📡 API Endpoints

#### 1. Chat (المساعد الذكي)
```http
POST /api/chat
Content-Type: application/json

{
  "message": "ما هي إجراءات السلامة الأساسية؟",
  "sessionId": "session_123"
}
```

#### 2. CCTV (الكاميرات)
```http
GET /api/cctv/cameras
POST /api/cctv/cameras
DELETE /api/cctv/cameras/{id}
```

#### 3. Detection (الكشف)
```http
POST /api/detection/detect
Content-Type: multipart/form-data
file: [image file]
```

#### 4. Incidents (الحوادث)
```http
GET /api/incidents
POST /api/incidents
PUT /api/incidents/{id}
```

#### 5. System Status
```http
GET /api/system/status
```

### ⚙️ التكوين

افتح `appsettings.json` وأضف مفاتيح API:

```json
{
  "AI": {
    "GeminiApiKey": "AIza...your-key",
    "GeminiModel": "gemini-2.0-flash-exp",
    "OpenAIApiKey": "sk-...your-key",
    "OpenAIModel": "gpt-4o-mini",
    "Provider": "gemini"
  }
}
```

### 🗄️ قاعدة البيانات

- **النوع**: SQLite
- **الملف**: `smartsafety.db`
- **يُنشأ تلقائياً** عند أول تشغيل

#### الجداول:
- `Cameras` - الكاميرات
- `Incidents` - الحوادث
- `Detections` - الكشوفات
- `ChatMessages` - المحادثات
- `RiskAssessments` - تقييم المخاطر
- `Inspections` - التفتيش

### 📦 الحزم المستخدمة

- `Microsoft.AspNetCore.OpenApi` - Swagger/OpenAPI
- `Microsoft.EntityFrameworkCore.Sqlite` - Database
- `Azure.AI.OpenAI` - OpenAI Integration
- `Google.Cloud.AIPlatform.V1` - Gemini Integration
- `Swashbuckle.AspNetCore` - Swagger UI

### 🧪 الاختبار

#### عبر Swagger:
1. افتح http://localhost:5000
2. جرب أي endpoint
3. شاهد الردود مباشرة

#### عبر cURL:
```bash
# Chat
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"ما هي إجراءات السلامة؟","sessionId":"test"}'

# Cameras
curl http://localhost:5000/api/cctv/cameras

# System Status
curl http://localhost:5000/api/system/status
```

### 🔧 التطوير

#### إضافة Controller جديد:
```csharp
[ApiController]
[Route("api/[controller]")]
public class MyController : ControllerBase
{
    [HttpGet]
    public IActionResult Get()
    {
        return Ok("Hello!");
    }
}
```

#### إضافة Service جديد:
```csharp
public interface IMyService
{
    Task<string> DoSomethingAsync();
}

public class MyService : IMyService
{
    public async Task<string> DoSomethingAsync()
    {
        return await Task.FromResult("Done!");
    }
}

// في Program.cs:
builder.Services.AddScoped<IMyService, MyService>();
```

### 🎨 Frontend

Frontend موجود في:
```
/workspaces/hazm-tuwaiq/frontend/
- index.html
- styles.css
- app.js
```

لربط Frontend مع ASP.NET API:
```javascript
const CONFIG = {
    API_BASE_URL: 'http://localhost:5000/api'
};
```

### 📝 الملاحظات

1. ✅ Backend جاهز بالكامل
2. ✅ Database يُنشأ تلقائياً
3. ✅ Swagger UI للاختبار
4. ⚠️ AI Integration تحتاج API Keys
5. ⚠️ Object Detection يحتاج تطبيق YOLO

### 🚀 النشر

#### على Azure:
```bash
dotnet publish -c Release
# ارفع المخرجات إلى Azure App Service
```

#### على Docker:
```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0
COPY ./bin/Release/net8.0/publish/ /app
WORKDIR /app
ENTRYPOINT ["dotnet", "SmartSafety.API.dll"]
```

### 📞 الدعم

للمساعدة:
- افتح Swagger: http://localhost:5000
- راجع Logs في Console
- تحقق من `appsettings.json`

---

**🎉 المشروع جاهز! جرّب `dotnet run` الآن!**
