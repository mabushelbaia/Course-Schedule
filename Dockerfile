# ---- Build Stage ----
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---- Runtime Stage ----
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project

COPY . .
RUN uv sync --no-dev

COPY --from=frontend-builder /app/dist /app/frontend/dist

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "course_schedule.web:app", "--host", "0.0.0.0", "--port", "8000"]
