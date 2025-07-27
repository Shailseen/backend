import logging
import time
import uuid
from typing import Any, Dict

from fastapi import FastAPI, Request
from pydantic import BaseModel

from .log_config import configure_logging, mask_sensitive

app = FastAPI(title="POST API server", version="1.0.0")

configure_logging()

logger = logging.getLogger("app")

class Payload(BaseModel):
    message: str
    metadata: Dict[str, Any] | None = None

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()

    body_bytes = await request.body()
    try:
        body_str = body_bytes.decode("utf-8")
    except Exception:
        body_str = "<non-text body>"

    logger.info(
        "request_id=%s method=%s path=%s headers=%s body=%s",
        request_id,
        request.method,
        request.url.path,
        dict(request.headers),
        mask_sensitive(body_str),
    )

    response = await call_next(request)

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "request_id=%s status=%s duration_ms=%.2f",
        request_id,
        response.status_code,
        duration_ms,
    )
    # Optionally add request_id header to responses
    response.headers["X-Request-ID"] = request_id
    return response


@app.post("/jira/webhook")
async def echo(payload: Payload, request: Request):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    logger.info("request_id=%s payload=%s", request_id, mask_sensitive(payload.model_dump_json()))
    return {"request_id": request_id, "received": payload}
