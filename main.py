from fastapi import FastAPI, Request, Body
from typing import Any
import logging
import os
import json
from datetime import datetime
import pytz

# Configure logging to see the captured data
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

LOG_DIR = "response_logs"

def save_response_to_file(data: dict):
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Use CST timezone (Central Standard Time)
    # Note: CST can refer to Central Standard Time (UTC-6) or China Standard Time (UTC+8).
    # Based on the user's example "2026-01-20T21:50:23 CST", usually this implies US Central Time.
    cst = pytz.timezone('America/Chicago')
    now = datetime.now(cst)

    date_str = now.strftime("%Y_%m_%d")
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S") + " CST"

    filename = f"response_log_{date_str}.txt"
    filepath = os.path.join(LOG_DIR, filename)

    try:
        with open(filepath, "a") as f:
            f.write(f"{timestamp} | {json.dumps(data)}\n")
    except Exception as e:
        logger.error(f"Failed to save response to file: {e}")

@app.post("/sailthru_postback")
async def sailthru_postback(request: Request, payload: Any = Body(None)):
    # Capture client IP
    client_host = request.client.host

    # Capture all headers
    headers = dict(request.headers)

    # Capture query parameters
    query_params = dict(request.query_params)

    # If payload is already captured by FastAPI (e.g. JSON in Swagger)
    # we use it. Otherwise, we try to capture it manually for other types.
    if payload is None:
        content_type = request.headers.get("Content-Type", "")
        try:
            if "application/json" in content_type:
                payload = await request.json()
            elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
                form_data = await request.form()
                payload = dict(form_data)
            else:
                # Fallback to raw body for other content types
                raw_payload = await request.body()
                if isinstance(raw_payload, bytes):
                    payload = raw_payload.decode(errors='replace')
                else:
                    payload = raw_payload
        except Exception as e:
            logger.error(f"Error capturing payload: {e}")
            # Final fallback to raw body if parsing failed
            raw_payload = await request.body()
            if isinstance(raw_payload, bytes):
                payload = raw_payload.decode(errors='replace')
            else:
                payload = raw_payload
    
    # Ensure payload is serializable if it's still bytes for some reason
    if isinstance(payload, bytes):
        payload = payload.decode(errors='replace')

    # Log the captured data
    logger.info(f"Received postback from {client_host}")
    logger.info(f"Headers: {headers}")
    logger.info(f"Query Params: {query_params}")
    logger.info(f"Payload: {payload}")

    response_data = {
        "status": "success",
        "captured": {
            "ip": client_host,
            "headers": headers,
            "query_params": query_params,
            "payload": payload
        }
    }

    # Save the response to a file
    save_response_to_file(response_data)

    return response_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8909)
