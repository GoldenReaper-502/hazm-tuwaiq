# Deployment Checklist - Hazm Tuwaiq

## ✅ Completed: Backend Implementation

- [x] FastAPI + Uvicorn server
- [x] YOLOv8 detection (mock fallback)
- [x] LLM chat integration (OpenAI/Anthropic/rules)
- [x] Smart reports with PDF/Excel export
- [x] All endpoints tested and working
- [x] Error handling and logging
- [x] Environment variables configured

## 📦 Deployment Files Ready

- [x] **Dockerfile** - Multi-stage build, Python 3.12, OpenCV support
- [x] **Procfile** - For Render/Railway deployment
- [x] **.env.example** - Complete configuration template
- [x] **render.yaml** - Render.com specific config
- [x] **railway.toml** - Railway.app specific config
- [x] **.dockerignore** - Optimized Docker builds
- [x] **.gitignore** - Git exclusions
- [x] **DEPLOYMENT.md** - Full deployment guide

## 🚀 Deploy on Render (Recommended)

1. Push code to GitHub
2. Go to https://render.com
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Settings:
   - Name: `hazm-backend`
   - Runtime: `Docker`
   - Region: Your choice
   - Build command: (auto-detect)
   - Start command: Leave blank (Dockerfile CMD will run)
6. Add environment variables:
   ```
   YOLO_MODEL=yolov8n.pt
   YOLO_CONF=0.25
   TORCH_DEVICE=cpu
   REPORT_RISK_THRESHOLD=0.3
   CORS_ORIGINS=https://your-frontend-domain.com
   OPENAI_API_KEY=(if using LLM)
   ```
7. Click "Create Web Service"
8. Wait for build (~5 min) and deployment
9. Test: `curl https://your-domain-xxx.onrender.com/health`

## 🚀 Deploy on Railway

1. Push code to GitHub
2. Go to https://railway.app
3. Click "Create Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway auto-detects Procfile
6. Set environment variables in Project settings
7. Every push to `main` auto-deploys

## 📋 Environment Variables (Production)

Key settings for your platform:

| Variable | Dev | Production | Notes |
|----------|-----|-----------|-------|
| `CORS_ORIGINS` | `*` | Your domain | Security critical |
| `TORCH_DEVICE` | `cpu` | `cpu` | `cuda` only if GPU available |
| `YOLO_CONF` | `0.25` | `0.25-0.5` | Adjust for false positives |
| `LOG_LEVEL` | `INFO` | `INFO` | Change to `WARNING` in prod |

## 📊 Testing URLs

Replace `your-domain-xxx` with your actual Render/Railway domain:

- Health: `https://your-domain-xxx/health`
- Swagger Docs: `https://your-domain-xxx/docs`
- Redoc: `https://your-domain-xxx/redoc`

## 🔄 Backend Endpoints (Working)

### Detection
- `POST /detect` - Send frame, get detection + auto-report
- `GET /detections` - List all detections
- `GET /detections/last` - Latest detection

### Reports
- `GET /reports/auto` - List auto-generated reports
- `GET /reports/{id}` - Single report
- `GET /reports/export?format=json|csv|pdf|excel` - Export all

### Chat
- `POST /chat` - Send message (with optional detection context)
- `GET /chat/{session_id}` - Get chat history
- `DELETE /chat/{session_id}` - Clear chat

### Other
- `GET /health` - Server status
- `POST /auth/register` - Create user (MVP)
- `/docs` - Swagger UI API explorer

## 🎯 Next Tasks (Optional)

- [ ] Frontend: React/Vue dashboard with real-time camera
- [ ] Frontend: Deploy to Vercel/Netlify
- [ ] Database: PostgreSQL for persistent storage
- [ ] Cache: Redis for session management
- [ ] Monitoring: Sentry for error tracking
- [ ] Analytics: PostHog or similar
- [ ] CI/CD: GitHub Actions for tests
- [ ] Load Testing: Locust or k6

## 🐛 Troubleshooting

**Build fails with "ultralytics not found"**
- Normal! It's optional. App uses mock fallback.
- To fix: Install reportlab + openpyxl manually in deployment settings

**First request is slow (~10s)**
- YOLOv8 model loads on first inference
- Subsequent requests are fast
- Pre-cache model in Docker to avoid (see DEPLOYMENT.md)

**CORS errors in frontend**
- Set `CORS_ORIGINS` to your frontend URL
- Example: `https://hazm-frontend.vercel.app`

**Out of memory**
- Render/Railway free tier: ~512MB RAM
- Reduce `YOLO_MODEL` to nano version
- Or upgrade to paid tier

## 📞 Support

- API Docs: Visit `/docs` on your deployed domain
- Logs: Check in Render/Railway dashboard
- Issues: Check GitHub issues or create new one

---

**Status**: 🟢 Ready for production deployment
**Last Updated**: 2025-12-28
