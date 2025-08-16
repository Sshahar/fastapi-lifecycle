"""
FastAPI Versioning Library

A decorator-based library for adding API versioning headers to FastAPI endpoints.
Supports deprecation warnings, sunset dates, and migration links with a clean dictionary syntax.
"""

from datetime import datetime
from typing import Optional, Callable, Any, Dict, Union
from functools import wraps
import inspect
from dateutil import parser

from fastapi import Response
from fastapi.routing import APIRoute
from fastapi.dependencies.utils import get_dependant
from starlette.responses import Response as StarletteResponse


class VersioningHeaders:
    """Utility class for managing versioning headers."""
    
    @staticmethod
    def format_http_date(dt: Union[datetime, str]) -> str:
        """Format datetime to HTTP date format."""
        if isinstance(dt, str):
            dt = parser.isoparse(dt.replace('Z', '+00:00'))
        return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    @staticmethod
    def create_link_header(url: str, rel: str = "deprecation") -> str:
        """Create a Link header value."""
        return f'<{url}>; rel="{rel}"'


def deprecated(config: Dict[str, Any]):
    """
    Mark an endpoint as deprecated with comprehensive configuration.
    
    Args:
        config: Dictionary with the following optional keys:
            - deprecated_at: ISO 8601 string or datetime when endpoint was deprecated
            - sunset_at: ISO 8601 string or datetime when endpoint will be removed
            - migration_url: URL for migration documentation
            - replacement: String describing the replacement endpoint
            - reason: String explaining why the endpoint is deprecated
            - version: Current API version
    
    Example:
        @deprecated({
            'deprecated_at': '2024-01-15T00:00:00Z',
            'sunset_at': '2024-06-15T00:00:00Z',
            'migration_url': 'https://api.example.com/docs/migration#users-v2',
            'replacement': 'GET /v2/users',
            'reason': 'Moving to v2 API with enhanced user profiles'
        })
    """
    def decorator(func: Callable) -> Callable:
        # Store metadata on the function
        func._deprecated_config = config
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get the response from the original function
            result = await func(*args, **kwargs)
            return _add_headers_to_response(result, args, kwargs, config)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Get the response from the original function
            result = func(*args, **kwargs)
            return _add_headers_to_response(result, args, kwargs, config)
        
        # Return the appropriate wrapper based on whether the function is async
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def sunset(config: Dict[str, Any]):
    """
    Mark an endpoint with a sunset date (when it will be removed).
    
    Args:
        config: Dictionary with the following keys:
            - sunset_at: ISO 8601 string or datetime when endpoint will be removed
            - migration_url: Optional URL for migration documentation
            - replacement: Optional string describing the replacement endpoint
            - reason: Optional string explaining the sunset
    
    Example:
        @sunset({
            'sunset_at': '2024-06-15T00:00:00Z',
            'migration_url': 'https://api.example.com/docs/migration',
            'replacement': 'GET /v2/endpoint',
            'reason': 'Consolidating endpoints for better performance'
        })
    """
    def decorator(func: Callable) -> Callable:
        # Store metadata on the function
        func._sunset_config = config
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get the response from the original function
            result = await func(*args, **kwargs)
            return _add_headers_to_response(result, args, kwargs, config)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Get the response from the original function
            result = func(*args, **kwargs)
            return _add_headers_to_response(result, args, kwargs, config)
        
        # Return the appropriate wrapper based on whether the function is async
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def versioned(config: Dict[str, Any]):
    """
    Mark an endpoint with comprehensive version information.
    
    Args:
        config: Dictionary with the following keys:
            - version: API version string
            - deprecated_at: Optional ISO 8601 string or datetime when deprecated
            - sunset_at: Optional ISO 8601 string or datetime when will be removed
            - migration_url: Optional URL for migration documentation
            - replacement: Optional string describing the replacement endpoint
            - reason: Optional string explaining version changes
    
    Example:
        @versioned({
            'version': '1.0',
            'deprecated_at': '2024-01-15T00:00:00Z',
            'sunset_at': '2024-06-15T00:00:00Z',
            'migration_url': 'https://api.example.com/docs/migration',
            'replacement': 'GET /v2/endpoint',
            'reason': 'Enhanced functionality in v2'
        })
    """
    def decorator(func: Callable) -> Callable:
        # Store metadata on the function
        func._versioned_config = config
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get the response from the original function
            result = await func(*args, **kwargs)
            return _add_headers_to_response(result, args, kwargs, config)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Get the response from the original function
            result = func(*args, **kwargs)
            return _add_headers_to_response(result, args, kwargs, config)
        
        # Return the appropriate wrapper based on whether the function is async
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def _add_headers_to_response(result: Any, args: tuple, kwargs: dict, config: Dict[str, Any]) -> Any:
    """Helper function to add headers to response objects."""
    # Find the Response object in args/kwargs
    response = None
    for arg in args:
        if isinstance(arg, (Response, StarletteResponse)):
            response = arg
            break
    
    if response is None:
        for value in kwargs.values():
            if isinstance(value, (Response, StarletteResponse)):
                response = value
                break
    
    if response is not None:
        _inject_headers(response, config)
    
    return result


def _inject_headers(response: Union[Response, StarletteResponse], config: Dict[str, Any]):
    """Inject versioning headers into response object."""
    
    # Add deprecation header
    if 'deprecated_at' in config and config['deprecated_at']:
        response.headers["Deprecation"] = VersioningHeaders.format_http_date(config['deprecated_at'])
    
    # Add sunset header
    if 'sunset_at' in config and config['sunset_at']:
        response.headers["Sunset"] = VersioningHeaders.format_http_date(config['sunset_at'])
    
    # Add migration link
    if 'migration_url' in config and config['migration_url']:
        response.headers["Link"] = VersioningHeaders.create_link_header(config['migration_url'])
    
    # Add version header
    if 'version' in config and config['version']:
        response.headers["X-API-Version"] = config['version']
    
    # Add replacement information
    if 'replacement' in config and config['replacement']:
        response.headers["X-API-Replacement"] = config['replacement']
    
    # Add deprecation reason
    if 'reason' in config and config['reason']:
        response.headers["X-API-Deprecation-Reason"] = config['reason']


# FastAPI middleware to automatically inject headers
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as MiddlewareResponse


# FastAPI middleware to automatically inject headers
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as MiddlewareResponse


class VersioningMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically inject versioning headers using request scope."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Get the route from request scope (set by FastAPI during routing)
        route = request.scope.get("route")
        
        if route and hasattr(route, 'endpoint'):
            endpoint = route.endpoint
            
            # Check for versioning configs and inject headers
            for config_attr in ['_deprecated_config', '_sunset_config', '_versioned_config']:
                if hasattr(endpoint, config_attr):
                    config = getattr(endpoint, config_attr)
                    _inject_headers(response, config)
        
        return response


# Alternative: Dependency-based approach (more explicit)
from fastapi import Depends

def inject_lifecycle_headers(response: Response, endpoint_func: Callable = None):
    """Dependency to inject lifecycle headers. More explicit but requires manual addition."""
    if endpoint_func:
        for config_attr in ['_deprecated_config', '_sunset_config', '_versioned_config']:
            if hasattr(endpoint_func, config_attr):
                config = getattr(endpoint_func, config_attr)
                _inject_headers(response, config)


# Alternative: Custom APIRoute class (most performant)
from fastapi.routing import APIRoute
from starlette.requests import Request
from starlette.responses import Response as StarletteResponse

class LifecycleAPIRoute(APIRoute):
    """Custom APIRoute that automatically handles lifecycle headers."""
    
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        
        async def custom_route_handler(request: Request) -> StarletteResponse:
            response = await original_route_handler(request)
            
            # Inject headers if endpoint has lifecycle configs
            endpoint = self.endpoint
            for config_attr in ['_deprecated_config', '_sunset_config', '_versioned_config']:
                if hasattr(endpoint, config_attr):
                    config = getattr(endpoint, config_attr)
                    _inject_headers(response, config)
            
            return response
        
        return custom_route_handler


# Convenience functions for different approaches
def setup_versioning(app: FastAPI, method: str = "middleware"):
    """
    Add versioning to FastAPI app using different methods.
    
    Args:
        app: FastAPI application instance
        method: "middleware" (default), "route_class", or "manual"
    """
    if method == "middleware":
        app.add_middleware(VersioningMiddleware)
    elif method == "route_class":
        app.router.route_class = LifecycleAPIRoute
    else:
        print("Using manual method - add Depends(inject_lifecycle_headers) to endpoints")


def setup_versioning_with_route_class(app: FastAPI):
    """Setup versioning using custom APIRoute class (most performant)."""
    app.router.route_class = LifecycleAPIRoute


# Example usage and testing
if __name__ == "__main__":
    from fastapi import FastAPI
    from datetime import datetime, timedelta
    import uvicorn
    
    app = FastAPI(title="API Versioning Example")
    
    # Setup versioning middleware
    setup_versioning(app)
    
    @app.get("/")
    async def root():
        return {"message": "Hello World"}
    
    @app.get("/deprecated-endpoint")
    @deprecated({
        'deprecated_at': '2024-01-15T00:00:00Z',
        'sunset_at': '2024-06-15T00:00:00Z',
        'migration_url': 'https://api.example.com/docs/migration#users-v2',
        'replacement': 'GET /v2/users',
        'reason': 'Moving to v2 API with enhanced user profiles'
    })
    async def deprecated_endpoint():
        return {"message": "This is a deprecated endpoint"}
    
    @app.get("/sunset-endpoint")
    @sunset({
        'sunset_at': '2024-06-15T00:00:00Z',
        'migration_url': 'https://api.example.com/docs/migration',
        'replacement': 'GET /v2/endpoint',
        'reason': 'Consolidating endpoints for better performance'
    })
    async def sunset_endpoint():
        return {"message": "This endpoint will be sunset"}
    
    @app.get("/versioned-endpoint")
    @versioned({
        'version': '1.0',
        'deprecated_at': '2024-01-15T00:00:00Z',
        'sunset_at': '2024-06-15T00:00:00Z',
        'migration_url': 'https://api.example.com/docs/migration',
        'replacement': 'GET /v2/endpoint',
        'reason': 'Enhanced functionality in v2'
    })
    async def versioned_endpoint():
        return {"message": "This is a versioned endpoint"}
    
    # Example with explicit Response object
    @app.get("/explicit-response")
    @deprecated({
        'deprecated_at': '2024-01-15T00:00:00Z',
        'reason': 'Use the new endpoint instead'
    })
    async def explicit_response_endpoint(response: Response):
        response.status_code = 200
        return {"message": "Endpoint with explicit response"}
    
    @app.get("/test-headers")
    @versioned({
        'version': '1.0',
        'deprecated_at': '2024-01-15T00:00:00Z',
        'sunset_at': '2024-06-15T00:00:00Z',
        'migration_url': 'https://api.example.com/docs/migration',
        'replacement': 'GET /v2/test',
        'reason': 'Testing header injection'
    })
    async def test_headers_endpoint():
        return {"message": "Check the response headers!"}
    
    
    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000)