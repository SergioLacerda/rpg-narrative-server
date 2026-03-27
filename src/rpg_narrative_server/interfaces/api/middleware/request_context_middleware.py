import time
import uuid
import logging

from fastapi import Request

from rpg_narrative_server.shared.logging.context import set_request_id


logger = logging.getLogger("rpg_narrative_server.api")


async def request_context_middleware(request: Request, call_next):

    request_id = str(uuid.uuid4())

    # 🔥 injeta contexto global (contextvars)
    set_request_id(request_id)

    start = time.time()

    logger.info(
        "request start method=%s path=%s",
        request.method,
        request.url.path,
    )

    try:
        response = await call_next(request)

        duration = int((time.time() - start) * 1000)

        logger.info(
            "request end status=%s duration_ms=%s",
            response.status_code,
            duration,
        )

        return response

    except Exception:
        logger.exception("request failed")
        raise