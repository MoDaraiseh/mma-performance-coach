# Build recipe only: execute and scan in authorized staging before production use.
# Original (Debian) staging recipe. Its base images carry the findings triaged in
# docs/PHASE24_TRIAGE.md; deploy/Dockerfile.candidate is the remediated recipe.
# Digests are the exact inputs recorded for original staging in docs/PHASE21_STAGING_RESULTS.md
# (node:24-bookworm-slim, python:3.14-slim-bookworm), so rebuilds cannot drift silently.
ARG NODE_IMAGE=node@sha256:c86ecead9e55a5210ac1727de38a4ca840bf03dcaf34dc9749addbf383b1920c
ARG PYTHON_IMAGE=python@sha256:516b51cb9db2ef061e465c803e50f64361b82cefd91e525b889b967b83e83527
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
RUN pip install --no-cache-dir -r requirements.lock.txt \
    && python -m pip check \
    && python -m pip uninstall --yes pip \
    && python -c "import shutil,sysconfig; shutil.rmtree(sysconfig.get_path('stdlib') + '/ensurepip')" \
    && useradd --uid 10001 --create-home mma
COPY backend/ ./
COPY --from=frontend /build/dist /app/frontend/dist
USER 10001
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 CMD python -c "import os,urllib.request,urllib.parse; host=urllib.parse.urlsplit(os.getenv('PUBLIC_ORIGIN','')).netloc or '127.0.0.1'; req=urllib.request.Request('http://127.0.0.1:8000/api/ready',headers={'Host':host,'X-Forwarded-Proto':'https'}); urllib.request.urlopen(req,timeout=4)"
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--no-access-log", "--limit-concurrency", "100", "--timeout-keep-alive", "5"]
