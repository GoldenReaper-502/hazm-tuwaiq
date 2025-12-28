# Deployment Guide - Hazm Tuwaiq

This guide covers deploying Hazm Tuwaiq backend to Render, Railway, and other platforms.

## 📋 Prerequisites

- Git repository with code pushed to GitHub
- Docker (for local testing)
- Account on deployment platform (Render.com or Railway.app)

## 🚀 Quick Deploy

### Option 1: Render.com (Recommended)

1. **Sign up** at https://render.com
2. **Connect GitHub repository**
3. **Create new Web Service**
   - Select your repo
   - Runtime: `Docker`
   - Build command: (auto-detected)
   - Start command: `cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables** in Render dashboard:
   ```
   YOLO_MODEL=yolov8n.pt
   YOLO_CONF=0.25
   TORCH_DEVICE=cpu
   REPORT_RISK_THRESHOLD=0.3
   CORS_ORIGINS=https://your-frontend-domain.com
   ```

5. **Deploy**: Click Deploy button
   - Build time: ~5 minutes (downloads YOLOv8 model)
   - First inference: ~10 seconds (model loads on first request)

### Option 2: Railway.app

1. **Sign up** at https://railway.app
2. **Create new Project**
3. **Add from GitHub**
   - Select your repo
   - Railway auto-detects `Procfile`

4. **Set Environment Variables** in Railway dashboard:
   ```
   PYTHONUNBUFFERED=1
   YOLO_MODEL=yolov8n.pt
   TORCH_DEVICE=cpu
   ```

5. **Deploy**: Automatic on push to `main` branch

### Option 3: Docker (Local Testing)

```bash
# Build image
docker build -t hazm-backend .

# Run container
docker run -p 8000:8000 \
  -e YOLO_CONF=0.25 \
  -e CORS_ORIGINS=http://localhost:3000 \
  hazm-backend

# Test health endpoint
curl http://localhost:8000/health
```

## 🔧 Configuration

### Environment Variables

Key variables for production:

| Variable | Default | Notes |
|----------|---------|-------|
| `PORT` | 8000 | Render/Railway auto-set this |
| `YOLO_MODEL` | yolov8n.pt | Model size: n=nano, s=small, m=medium |
| `YOLO_CONF` | 0.25 | Detection confidence (0.0-1.0) |
| `TORCH_DEVICE` | cpu | Use `cpu` for free tier (CUDA needs GPU) |
| `REPORT_RISK_THRESHOLD` | 0.3 | Auto-report score threshold |
| `CORS_ORIGINS` | * | Set to frontend domain in production |
| `OPENAI_API_KEY` | (empty) | Optional: for LLM chat |
| `ANTHROPIC_API_KEY` | (empty) | Optional: for Claude chat |

### Model Caching

YOLOv8 model (280MB) downloads on first inference, taking ~10 seconds.

**To pre-cache in Docker image** (faster startup):
1. Uncomment in Dockerfile stage 1:
   ```dockerfile
   RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
   ```
2. Rebuild image (adds ~300MB to image size)

## 📊 Performance

### Inference Speed (Mock Fallback)
- Detection: ~50ms (model) or instant (mock)
- Report generation: ~20ms
- PDF export: ~500ms
- Excel export: ~300ms

### Scaling
- **Free tier**: ~100 requests/minute
- **Paid tier**: Limited by CPU/memory, typically 1000+ req/min
- **For 1000+ concurrent users**: Consider adding load balancer

## 🔐 Security

### Production Checklist

- [ ] Set `CORS_ORIGINS` to your frontend domain
- [ ] Set `HAZM_API_KEY` if you want API protection
- [ ] Use HTTPS (auto-enabled on Render/Railway)
- [ ] Keep dependencies updated: `pip install --upgrade -r requirements.txt`
- [ ] Limit `YOLO_CONF` to reduce false positives
- [ ] Monitor logs for errors

## 🐛 Troubleshooting

### Build Fails: "ultralytics not found"
- Normal! ultralytics is optional. App uses mock fallback.

### Slow First Detection (~10s)
- YOLOv8 model loading. Subsequent requests are fast.
- Pre-cache model in Docker image to avoid.

### CORS Error in Frontend
- Set `CORS_ORIGINS` to match frontend URL
- In dev: `http://localhost:3000`
- In production: `https://your-frontend.vercel.app`

## 📚 API Documentation

Once deployed, visit:
- **API Docs**: `https://your-domain.com/docs`
- **Health Check**: `https://your-domain.com/health`

## 💰 Cost Estimate

- **Render Free**: $0/month (limited, sleeps after 15 min)
- **Railway Free**: $5 credit/month
- **Production**: $10-50/month

## 📝 Next Steps

1. Push code to GitHub
2. Create deployment on Render/Railway
3. Set environment variables
4. Deploy and test
5. Connect frontend
6. Monitor and scale as needed
