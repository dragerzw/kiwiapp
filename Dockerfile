# ──────────────────────────────────────────────
# KiwiApp Flask API — Production Image
# ──────────────────────────────────────────────
FROM python:3.14-slim AS base

# Prevent Python from writing .pyc files and enable unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install OS-level dependencies required by cryptography / cffi
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# ── Dependencies layer (cached unless requirements.txt changes) ──
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt gunicorn

# ── Application code ──
COPY app/ app/
COPY run.py .

# Non-root user for security
RUN addgroup --system kiwi && adduser --system --ingroup kiwi kiwi
USER kiwi

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/')" || exit 1

# Use Gunicorn for production; override with CMD for dev
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "run:app"]
