FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV LOG_LEVEL=INFO
ENV LOG_FILE_PATH=logs/app.log
ENV LOG_MAX_BYTES=1048576
ENV LOG_BACKUP_COUNT=5

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
