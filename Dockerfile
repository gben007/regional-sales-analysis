# ── Stage 1: dependency layer (cached until requirements.txt changes) ──────────
FROM python:3.12-slim AS base

WORKDIR /app

# System deps for openpyxl / matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 2: project files ─────────────────────────────────────────────────────
FROM base AS app

COPY src/       ./src/
COPY data/      ./data/
COPY notebooks/ ./notebooks/
COPY tests/     ./tests/
COPY pytest.ini .

# Jupyter Lab on 8888 (no token for local use)
EXPOSE 8888

CMD ["jupyter", "lab", \
     "--ip=0.0.0.0", "--port=8888", \
     "--no-browser", "--allow-root", \
     "--ServerApp.token=''", "--ServerApp.password=''", \
     "--notebook-dir=/app/notebooks"]
