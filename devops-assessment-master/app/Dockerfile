# ---- Builder stage: install dependencies into an isolated prefix ----
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Runtime stage: minimal image, non-root user ----
FROM python:3.12-slim

# Create a non-root user to run the application.
RUN useradd --create-home --uid 10001 appuser

WORKDIR /app

# Copy installed dependencies and application source.
COPY --from=builder /install /usr/local
COPY main.py .

ENV PYTHONUNBUFFERED=1 \
    ENVIRONMENT=dev

EXPOSE 8080

USER appuser

# NOTE: container health is handled at the Kubernetes level via the pod's
# startup/liveness/readiness probes (see helm/templates/deployment.yaml).
# A Docker HEALTHCHECK is intentionally omitted because the kubelet ignores it.

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

