import logging
import time
import uuid
from typing import Any, Dict
import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

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

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS

# Configure logging
configure_logging()
logger = logging.getLogger("app")


# Middleware equivalent for request logging
@app.before_request
def log_request():
    request.request_id = str(uuid.uuid4())
    request.start_time = time.perf_counter()

    try:
        body_str = request.get_data(as_text=True)
    except Exception:
        body_str = "<non-text body>"

    logger.info(
        "request_id=%s method=%s path=%s headers=%s body=%s",
        request.request_id,
        request.method,
        request.path,
        dict(request.headers),
        mask_sensitive(body_str),
    )


@app.after_request
def log_response(response):
    duration_ms = (time.perf_counter() - request.start_time) * 1000
    logger.info(
        "request_id=%s status=%s duration_ms=%.2f",
        request.request_id,
        response.status_code,
        duration_ms,
    )
    response.headers["X-Request-ID"] = request.request_id
    return response


# Health check endpoints
@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "message": "POST API server is running on PythonAnywhere!",
        "status": "success",
        "version": "1.0.0"
    })


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "GET API server",
        "version": "1.0.0"
    })


# Your original webhook endpoint
@app.route("/jira/webhook", methods=["POST"])
def echo():
    try:
        payload = request.get_json()
        if not payload:
            return jsonify({"error": "No JSON payload provided"}), 400

        request_id = getattr(request, 'request_id', str(uuid.uuid4()))
        logger.info("request_id=%s payload=%s", request_id, mask_sensitive(str(payload)))

        return jsonify({
            "request_id": request_id,
            "received": payload
        })
    except Exception as e:
        logger.error("Error processing webhook: %s", str(e))
        return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True)