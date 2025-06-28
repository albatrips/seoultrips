FROM python:3.11-slim

WORKDIR /app

# requirements만 먼저 복사 → 의존성 캐시 활용
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 나머지 소스 복사
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
