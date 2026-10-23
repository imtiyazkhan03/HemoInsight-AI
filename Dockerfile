# =====================================================================
# Stage 1: Build Frontend (Vite + React + Tailwind CSS)
# =====================================================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# =====================================================================
# Stage 2: Production Python Backend & Unified Server
# =====================================================================
FROM python:3.11-slim AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=10000

WORKDIR /app

# Install minimal OS dependencies for OCR, OpenCV, ONNX runtime, and PDF rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    tesseract-ocr \
    tesseract-ocr-eng \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r ./backend/requirements.txt

# Copy backend application code
COPY backend/ ./backend/

# Copy compiled frontend from Stage 1 into frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose server port (10000 is default for Render and cloud container runtimes)
EXPOSE 10000

# Start Uvicorn bound to 0.0.0.0 and dynamic $PORT
CMD ["sh", "-c", "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
