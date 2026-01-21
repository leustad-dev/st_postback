from fastapi import FastAPI, Request, Body
from typing import Any
import logging

# Configure logging to see the captured data
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

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

    return {
        "status": "success",
        "captured": {
            "ip": client_host,
            "headers": headers,
            "query_params": query_params,
            "payload": payload
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8909)
