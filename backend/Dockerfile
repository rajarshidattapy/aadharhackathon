FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps needed by catboost (and common wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy backend source
COPY . /app

EXPOSE 8001

# Render provides $PORT; locally default to 8001
CMD ["sh", "-c", "hypercorn backend.app.main:app --bind 0.0.0.0:${PORT:-8000}"]

