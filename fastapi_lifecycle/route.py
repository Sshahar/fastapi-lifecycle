"""Custom APIRoute implementation for lifecycle header injection."""

from typing import Callable

from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.requests import Request
from starlette.responses import Response as StarletteResponse

from .utils import inject_headers, get_endpoint_configs


class LifecycleAPIRoute(APIRoute):
    """
    Custom APIRoute that automatically handles lifecycle headers.

    This approach provides the best performance as headers are injected
    directly during route handling without additional middleware overhead.
    """

    def get_route_handler(self) -> Callable:
        """
        Get route handler with automatic header injection.

        Returns:
            Wrapped route handler function
        """
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> StarletteResponse:
            """Custom route handler with header injection."""
            response = await original_route_handler(request)

            # Inject headers based on endpoint lifecycle configurations
            endpoint = self.endpoint
            configs = get_endpoint_configs(endpoint)
            for config in configs.values():
                inject_headers(response, config)

            return response

        return custom_route_handler


def setup_versioning_with_route_class(app: FastAPI) -> None:
    """
    Setup lifecycle management using custom APIRoute class.

    This is the most performant approach as it avoids middleware overhead.

    Args:
        app: FastAPI application instance
    """
    app.router.route_class = LifecycleAPIRoute
