# api/index.py - Your FastAPI app migrated for Vercel deployment

import logging
import time
import uuid
from typing import Any, Dict
import sys
import os

from fastapi import FastAPI, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add the parent directory to path to import from app folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your existing log configuration
try:
    from app.log_config import configure_logging, mask_sensitive
except ImportError:
    # Fallback if import fails
    def configure_logging():
        logging.basicConfig(level=logging.INFO)


    def mask_sensitive(data):
        return data

# Create FastAPI app with your original configuration
app = FastAPI(title="POST API server", version="1.0.0")
router = APIRouter()

# Add CORS middleware for Vercel deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
configure_logging()
logger = logging.getLogger("app")


# Your original Pydantic model
class Payload(BaseModel):
    message: str
    metadata: Dict[str, Any] | None = None


# Your original middleware for request logging
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


# Health check endpoint for Vercel
@app.get("/")
async def root():
    return {
        "message": "POST API server is running on Vercel!",
        "status": "success",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "POST API server",
        "version": "1.0.0"
    }


# Your original webhook endpoint
@app.post("/jira/webhood")
async def echo(payload: Payload, request: Request):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    logger.info("request_id=%s payload=%s", request_id, mask_sensitive(payload.model_dump_json()))
    return {"request_id": request_id, "received": payload}