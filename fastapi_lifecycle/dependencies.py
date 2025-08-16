"""FastAPI dependency functions for manual lifecycle management."""

from typing import Callable, Optional

from fastapi import Response

from .utils import inject_headers, get_endpoint_configs


def inject_lifecycle_headers(
    response: Response, endpoint_func: Optional[Callable] = None
) -> None:
    """
    FastAPI dependency to manually inject lifecycle headers.

    This approach gives you explicit control over when headers are injected
    but requires manual addition to each endpoint.

    Args:
        response: FastAPI Response object
        endpoint_func: Endpoint function to extract configs from

    Example:
        @app.get("/endpoint")
        @deprecated({...})
        async def endpoint(
            response: Response = Depends(inject_lifecycle_headers)
        ):
            return {"data": "value"}
    """
    if endpoint_func:
        configs = get_endpoint_configs(endpoint_func)
        for config in configs.values():
            inject_headers(response, config)
