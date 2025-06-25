FROM python:3.11-slim
WORKDIR /app

# ── 시스템 라이브러리 (mysqlclient 등 C 확장 필요 시)
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libc-dev pkg-config libmariadb-dev-compat libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/server/static/uploads

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
