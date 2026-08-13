FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    fonts-liberation \
    fontconfig \
    libfreetype6-dev \
    libjpeg-dev \
    zlib1g-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p captchas

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl --fail --silent --show-error http://127.0.0.1:8000/api/health || exit 1

CMD ["python", "-m", "hypercorn", "app:app", "--bind", "0.0.0.0:8000"]
