# Build recipe only: execute and scan in authorized staging before production use.
ARG NODE_IMAGE=node:24-bookworm-slim
ARG PYTHON_IMAGE=python:3.14-slim-bookworm
FROM ${NODE_IMAGE} AS frontend
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM ${PYTHON_IMAGE}
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app/backend
COPY backend/requirements.lock.txt ./
RUN pip install --no-cache-dir -r requirements.lock.txt && useradd --uid 10001 --create-home mma
COPY backend/ ./
COPY --from=frontend /build/dist /app/frontend/dist
USER 10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 CMD python -c "import os,urllib.request,urllib.parse; host=urllib.parse.urlsplit(os.getenv('PUBLIC_ORIGIN','')).netloc or '127.0.0.1'; req=urllib.request.Request('http://127.0.0.1:8000/api/ready',headers={'Host':host,'X-Forwarded-Proto':'https'}); urllib.request.urlopen(req,timeout=4)"
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--no-access-log", "--limit-concurrency", "100", "--timeout-keep-alive", "5"]
