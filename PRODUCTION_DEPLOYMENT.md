# HAZM TUWAIQ - Production Deployment Guide

## 🚀 نشر سريع (Quick Deploy)

### المتطلبات الأساسية

```bash
# Docker & Docker Compose
docker --version  # >= 24.0
docker-compose --version  # >= 2.20

# Git
git --version

# Python (للتطوير المحلي)
python --version  # >= 3.11
```

---

## 📦 النشر باستخدام Docker Compose

### 1. استنساخ المشروع

```bash
git clone https://github.com/YOUR_ORG/hazm-tuwaiq.git
cd hazm-tuwaiq
```

### 2. تهيئة البيئة

```bash
# إنشاء ملف البيئة
cp .env.example .env

# تحرير المتغيرات
nano .env
```

### 3. تنزيل النماذج

```bash
# تنزيل YOLOv8 models
python download_yolo_model.py
```

### 4. إنشاء شهادات SSL (للإنتاج)

```bash
# شهادات ذاتية التوقيع للاختبار
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/C=SA/ST=Riyadh/L=Riyadh/O=HAZM/CN=hazm-tuwaiq.sa"

# للإنتاج: استخدم Let's Encrypt
# certbot certonly --webroot -w /var/www/certbot \
#   -d hazm-tuwaiq.sa -d www.hazm-tuwaiq.sa
```

### 5. البناء والتشغيل

```bash
# بناء الحاويات
docker-compose -f docker-compose.production.yml build

# تشغيل النظام
docker-compose -f docker-compose.production.yml up -d

# مراقبة السجلات
docker-compose -f docker-compose.production.yml logs -f hazm-backend
```

### 6. التحقق من الحالة

```bash
# فحص الصحة
curl http://localhost/health

# فحص API
curl http://localhost/api/

# واجهة Swagger
open http://localhost/docs
```

---

## ☸️ النشر على Kubernetes

### 1. إنشاء Namespace

```bash
kubectl create namespace hazm-tuwaiq
```

### 2. إنشاء Secrets

```bash
# Docker registry credentials
kubectl create secret docker-registry regcred \
  --docker-server=YOUR_REGISTRY \
  --docker-username=YOUR_USERNAME \
  --docker-password=YOUR_PASSWORD \
  --docker-email=YOUR_EMAIL \
  -n hazm-tuwaiq

# Application secrets
kubectl create secret generic hazm-secrets \
  --from-literal=jwt-secret=YOUR_JWT_SECRET \
  --from-literal=api-key=YOUR_API_KEY \
  -n hazm-tuwaiq
```

### 3. إنشاء Persistent Volumes

```bash
kubectl apply -f k8s/pvc.yaml
```

### 4. نشر التطبيق

```bash
# Deploy backend
kubectl apply -f k8s/deployment.yaml

# Deploy ingress
kubectl apply -f k8s/ingress.yaml

# Verify deployment
kubectl get pods -n hazm-tuwaiq
kubectl get svc -n hazm-tuwaiq
```

### 5. مراقبة النشر

```bash
# Watch rollout
kubectl rollout status deployment/hazm-backend -n hazm-tuwaiq

# Check logs
kubectl logs -f deployment/hazm-backend -n hazm-tuwaiq

# Get service URL
kubectl get ingress -n hazm-tuwaiq
```

---

## ☁️ النشر السحابي

### AWS (Elastic Container Service)

```bash
# 1. Build and push to ECR
aws ecr get-login-password --region sa-east-1 | \
  docker login --username AWS --password-stdin \
  YOUR_ACCOUNT.dkr.ecr.sa-east-1.amazonaws.com

docker tag hazm-tuwaiq:latest \
  YOUR_ACCOUNT.dkr.ecr.sa-east-1.amazonaws.com/hazm-tuwaiq:latest

docker push YOUR_ACCOUNT.dkr.ecr.sa-east-1.amazonaws.com/hazm-tuwaiq:latest

# 2. Deploy to ECS
aws ecs update-service \
  --cluster hazm-cluster \
  --service hazm-backend \
  --force-new-deployment
```

### Azure (Container Instances)

```bash
# Login to Azure
az login

# Create resource group
az group create --name hazm-rg --location saudiarabia-north

# Deploy container
az container create \
  --resource-group hazm-rg \
  --name hazm-backend \
  --image YOUR_REGISTRY/hazm-tuwaiq:latest \
  --dns-name-label hazm-tuwaiq \
  --ports 8000 \
  --cpu 2 --memory 4
```

### Google Cloud (Cloud Run)

```bash
# Deploy to Cloud Run
gcloud run deploy hazm-backend \
  --image gcr.io/YOUR_PROJECT/hazm-tuwaiq:latest \
  --platform managed \
  --region me-west1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2
```

---

## 📊 المراقبة والتتبع

### Prometheus + Grafana

```bash
# الوصول إلى Prometheus
open http://localhost:9090

# الوصول إلى Grafana
open http://localhost:3000
# Username: admin
# Password: admin
```

### لوحات المعلومات المهمة

1. **System Health**
   - CPU/Memory usage
   - Request rate
   - Error rate
   - Response time

2. **AI Metrics**
   - Model inference time
   - Detection accuracy
   - Processing queue

3. **Exclusive Features**
   - Immune system effectiveness
   - Prediction accuracy
   - Drift detection alerts

---

## 🔒 الأمان

### SSL/TLS

```bash
# Automatic renewal with certbot
certbot renew --dry-run
```

### Firewall

```bash
# UFW rules
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 8000/tcp  # Block direct backend access
sudo ufw enable
```

### Rate Limiting

تم تكوينه في `nginx/nginx.conf`:
- API: 10 requests/second
- General: 30 requests/second

---

## 🔄 التحديثات

### Zero-Downtime Update

```bash
# Rolling update
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d --no-deps --build hazm-backend

# Kubernetes
kubectl set image deployment/hazm-backend \
  hazm-backend=YOUR_REGISTRY/hazm-tuwaiq:NEW_VERSION \
  -n hazm-tuwaiq
```

### Rollback

```bash
# Docker Compose
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d

# Kubernetes
kubectl rollout undo deployment/hazm-backend -n hazm-tuwaiq
```

---

## 🧪 الاختبار

### اختبارات الإنتاج

```bash
# Run production tests
pytest tests/test_production.py -v

# Load testing with Locust
locust -f tests/locustfile.py --host=http://localhost
```

### فحص الصحة

```bash
# Health check script
./scripts/health_check.sh
```

---

## 📝 النسخ الاحتياطي

### قاعدة البيانات

```bash
# Backup volumes
docker run --rm \
  -v hazm-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/data-$(date +%Y%m%d).tar.gz /data
```

### الاستعادة

```bash
# Restore from backup
docker run --rm \
  -v hazm-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/data-20250129.tar.gz -C /
```

---

## 🆘 استكشاف الأخطاء

### المشاكل الشائعة

1. **Container won't start**
   ```bash
   docker-compose logs hazm-backend
   docker inspect hazm-backend
   ```

2. **High memory usage**
   ```bash
   docker stats
   # Adjust resources in docker-compose.yml
   ```

3. **Slow response**
   ```bash
   # Check backend logs
   docker logs hazm-backend --tail=100
   
   # Monitor with Prometheus
   open http://localhost:9090
   ```

### الدعم

- 📧 Email: support@hazm-tuwaiq.sa
- 📚 Documentation: https://docs.hazm-tuwaiq.sa
- 🐛 Issues: https://github.com/YOUR_ORG/hazm-tuwaiq/issues

---

## ✅ قائمة التحقق من الإنتاج

- [ ] SSL certificates configured
- [ ] Environment variables set
- [ ] Models downloaded
- [ ] Database backup configured
- [ ] Monitoring enabled
- [ ] Rate limiting configured
- [ ] Firewall rules set
- [ ] Health checks working
- [ ] Logs centralized
- [ ] Auto-scaling configured
- [ ] Disaster recovery plan
- [ ] Team trained

---

**النشر الناجح يعني:**
✅ Uptime > 99.9%  
✅ Response time < 200ms  
✅ Zero data loss  
✅ Secure by default  
✅ Scalable to 10,000+ users
