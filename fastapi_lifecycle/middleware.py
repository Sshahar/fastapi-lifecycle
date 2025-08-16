"""Middleware for automatic lifecycle header injection."""

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from .utils import inject_headers, get_endpoint_configs


class VersioningMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically inject lifecycle headers.

    This middleware examines each request's matched route and automatically
    injects appropriate lifecycle headers based on decorator metadata.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Process request and inject lifecycle headers in response.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler in chain

        Returns:
            HTTP response with lifecycle headers injected
        """
        response = await call_next(request)

        # Get the route from request scope (set by FastAPI during routing)
        route = request.scope.get("route")

        if route and hasattr(route, "endpoint"):
            endpoint = route.endpoint

            # Get all lifecycle configurations and inject headers
            configs = get_endpoint_configs(endpoint)
            for config in configs.values():
                inject_headers(response, config)

        return response


def setup_versioning(app: FastAPI, method: str = "middleware") -> None:
    """
    Configure FastAPI app with lifecycle management.

    Args:
        app: FastAPI application instance
        method: Setup method ("middleware", "route_class", or "manual")

    Raises:
        ValueError: If invalid method specified
    """
    if method == "middleware":
        app.add_middleware(VersioningMiddleware)
    elif method == "route_class":
        from .route import LifecycleAPIRoute

        app.router.route_class = LifecycleAPIRoute
    elif method == "manual":
        print("Manual setup - use Depends(inject_lifecycle_headers) in endpoints")
    else:
        raise ValueError(
            f"Invalid method: {method}. Use 'middleware', 'route_class', or 'manual'"
        )
