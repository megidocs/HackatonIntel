FROM node:24-bookworm-slim AS browser-assets
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --omit=dev --no-audit --no-fund

FROM python:3.13-slim-bookworm
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PORT=8000
COPY backend/requirements.txt ./backend/requirements.txt
RUN python -m pip install --no-cache-dir -r backend/requirements.txt
COPY backend ./backend
COPY frontend/public ./frontend/public
COPY --from=browser-assets /frontend/node_modules/maplibre-gl/dist ./frontend/node_modules/maplibre-gl/dist
COPY deploy/manhattan.graphml.gz deploy/manhattan.graphml.gz.sha256 ./deploy/
RUN sha256sum --check deploy/manhattan.graphml.gz.sha256 \
    && mkdir -p backend/data \
    && gzip -dc deploy/manhattan.graphml.gz > backend/data/manhattan.graphml
USER 10001
EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn backend.app:app --host 0.0.0.0 --port ${PORT}"]
