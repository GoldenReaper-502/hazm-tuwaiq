# Multi-stage Dockerfile for Hazm Tuwaiq Backend
# Stage 1: Builder - compile dependencies and download YOLO model
FROM python:3.12-slim as builder

WORKDIR /app

# Install system dependencies for building + OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir \
        ultralytics \
        reportlab \
        openpyxl \
        opencv-python-headless \
        pillow \
        numpy \
    || echo "⚠ Optional AI/Export dependencies skipped (will use mock/fallback)"

# Pre-download YOLOv8 model to cache (optional - saves 2-3 min at startup)
# RUN python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')" || echo "YOLOv8 model download skipped"

# Stage 2: Runtime - lean image for production
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies (OpenCV libs required)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY backend/ .

# Set environment variables for production
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV TORCH_DEVICE=cpu
ENV YOLO_MODEL=yolov8n.pt
ENV YOLO_CONF=0.25
ENV REPORT_RISK_THRESHOLD=0.3
ENV CORS_ORIGINS=*

# Expose port
EXPOSE 8000

# Health check via HTTP
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run uvicorn with production settings
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--log-level", "info"]
