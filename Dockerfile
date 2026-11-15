FROM node:24-bookworm-slim AS web
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN VITE_SHOWCASE_ONLY=false npm run build

FROM python:3.14-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 \
    TIMESCOPE_DATA_DIR=/app/data PORT=8000 HOME=/home/timescope
WORKDIR /app
COPY requirements-resolved.txt ./
RUN pip install --no-cache-dir -r requirements-resolved.txt \
    && useradd --create-home --uid 10001 timescope
COPY backend/ ./backend/
COPY --from=web /build/dist ./frontend/dist
RUN mkdir -p /app/data && chown timescope:timescope /app/data
USER timescope
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.getenv('PORT','8000')+'/api/health',timeout=3)"
CMD ["python", "-m", "backend"]
