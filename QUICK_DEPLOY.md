# Quick Deployment Guide - Hazm Tuwaiq

## 30-Second Render Deploy

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Create Render Service**
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Select your GitHub repo
   - Runtime: **Docker**
   - Name: `hazm-backend`
   - Click "Create Web Service"

3. **Add Environment Variables** (in Render dashboard)
   ```
   YOLO_MODEL=yolov8n.pt
   YOLO_CONF=0.25
   TORCH_DEVICE=cpu
   REPORT_RISK_THRESHOLD=0.3
   CORS_ORIGINS=your-frontend-url.com
   ```

4. **Wait & Test** (5 min build)
   ```bash
   curl https://your-domain-xxx.onrender.com/health
   # Should return: {"status":"ok",...}
   ```

## For Railway Deploy

1. Push to GitHub (same as above)
2. Go to https://railway.app
3. Click "Create Project" → "Deploy from GitHub repo"
4. Select your repo
5. Set environment variables (same as above)
6. Click "Deploy"

## Environment Variables Reference

| Variable | Default | Notes |
|----------|---------|-------|
| `CORS_ORIGINS` | `*` | **SET THIS TO YOUR FRONTEND URL** |
| `YOLO_CONF` | `0.25` | Detection sensitivity (higher = fewer false positives) |
| `TORCH_DEVICE` | `cpu` | Keep as `cpu` unless you have GPU |
| `REPORT_RISK_THRESHOLD` | `0.3` | Auto-report score threshold |

## Common Env Var Values

```bash
# Development (localhost)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Production (Vercel frontend)
CORS_ORIGINS=https://hazm-frontend.vercel.app

# Open to all (testing only!)
CORS_ORIGINS=*
```

## Test Your Deployment

After deployment, visit:
- **Health Check**: `https://your-domain/health`
- **API Docs**: `https://your-domain/docs`
- **API Redoc**: `https://your-domain/redoc`

Send test detection:
```bash
curl -X POST https://your-domain/detect \
  -H "Content-Type: application/json" \
  -d '{"frame_data":"iVBORw0KGgo="}'  # Minimal PNG
```

## If Something Fails

**Common Issues:**

1. **Build fails with "ultralytics not found"**
   - This is normal! The app has a mock fallback.
   - Check "Deploy" tab → logs for errors
   - Usually succeeds anyway

2. **CORS Error**
   - Set `CORS_ORIGINS` to your frontend URL
   - Don't use `*` in production

3. **First request is slow (~10s)**
   - YOLOv8 model is loading
   - Subsequent requests are fast
   - This is normal

4. **"Out of memory"**
   - Free tier has limited RAM
   - Either upgrade to paid
   - Or reduce YOLO_MODEL to a smaller variant

## Next: Connect Frontend

Once backend is deployed, update your frontend:

```javascript
// In frontend/.env
VITE_API_URL=https://your-domain-xxx.onrender.com
```

Then deploy frontend to Vercel/Netlify, and you're done! 🎉

---

**Need help?** Check DEPLOYMENT.md or DEPLOYMENT_CHECKLIST.md for detailed guides.
