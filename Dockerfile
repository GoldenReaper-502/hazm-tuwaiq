# =========================================
# Multi-stage Dockerfile for Hazm Tuwaiq Backend
# Production-ready (Render compatible)
# =========================================

# -------------------------------
# Stage 1: Builder
# -------------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir \
        ultralytics \
        reportlab \
        openpyxl \
        opencv-python-headless \
        pillow \
        numpy || \
    echo "⚠ Optional AI/Export dependencies skipped (fallback mode enabled)"

# (Optional) Pre-download YOLO model to cache
# RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')" || true


# -------------------------------
# Stage 2: Runtime
# -------------------------------
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy backend application code
COPY backend/ .

# -------------------------------
# Environment configuration
# -------------------------------
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV TORCH_DEVICE=cpu
ENV YOLO_MODEL=yolov8n.pt
ENV YOLO_CONF=0.25
ENV REPORT_RISK_THRESHOLD=0.3
ENV CORS_ORIGINS=*

# -------------------------------
# Network
# -------------------------------
EXPOSE 8000

# -------------------------------
# Health check
# -------------------------------
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# -------------------------------
# Start application
# -------------------------------
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--log-level", "info"]
