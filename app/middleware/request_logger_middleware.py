import logging
from typing import Callable
from urllib import response
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

logger = logging.getLogger("api")


class RequestLoggerMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: Callable) -> Response:

        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        logger.info(
            f"ID:[{request_id}] {request.method} {request.url.path} - "
            f"Status: {response.status_code} "
        )
        return response
