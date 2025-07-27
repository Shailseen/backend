# python-post-api-server

A tiny **FastAPI** server exposing a POST endpoint with structured logging of the request payload and headers for debugging.

## Features

- `POST /echo` endpoint that returns what you sent back (plus a generated `request_id`).
- Request/response logging with masking of sensitive fields.
- Rotating file logs in `logs/app.log` (configurable).
- Dockerfile for containerized runs.
- Pytest unit test using `httpx.AsyncClient`.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then test:

```bash
curl -X POST http://127.0.0.1:8000/echo \
  -H "Content-Type: application/json" \
  -d '{"message":"hello","metadata":{"user":"alice","token":"secret-token"}}'
```

## Run with Docker

```bash
docker build -t post-api-server .
docker run --rm -p 8000:8000 post-api-server
```

## Run tests

```bash
pytest -q
```

## Env vars

- `LOG_LEVEL`: default `INFO`
- `LOG_FILE_PATH`: default `logs/app.log`
- `LOG_MAX_BYTES`: default `1048576` (1MB) before rotating
- `LOG_BACKUP_COUNT`: default `5`

