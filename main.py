from fastapi import FastAPI, Request, Body
from typing import Any
import logging
import os
import json
from datetime import datetime

# Configure logging to see the captured data
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

LOG_DIR = "response_logs"

def save_response_to_file(data: dict):
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    date_str = datetime.now().strftime("%Y_%m_%d")
    filename = f"response_log_{date_str}.txt"
    filepath = os.path.join(LOG_DIR, filename)

    try:
        with open(filepath, "a") as f:
            f.write(json.dumps(data) + "\n")
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
                payload = await request.body()
                if isinstance(payload, bytes):
                    payload = payload.decode(errors='replace')
        except Exception as e:
            logger.error(f"Error capturing payload: {e}")
            # Final fallback to raw body if parsing failed
            payload = await request.body()
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
