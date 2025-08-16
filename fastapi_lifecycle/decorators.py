"""Decorator functions for marking API endpoint lifecycle status."""

import inspect
from functools import wraps
from typing import Callable, Any

from .schemas import LifecycleConfig
from .utils import validate_config, inject_headers, get_endpoint_configs


def _create_lifecycle_decorator(config_attr: str):
    """
    Factory function to create lifecycle decorators.

    Args:
        config_attr: Name of the attribute to store config on the function

    Returns:
        Decorator function
    """

    def decorator(config: LifecycleConfig):
        def wrapper(func: Callable) -> Callable:
            # Validate configuration
            validate_config(config)

            # Store metadata on the function
            setattr(func, config_attr, config)

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                result = await func(*args, **kwargs)
                return _handle_response_headers(result, args, kwargs, func)

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                result = func(*args, **kwargs)
                return _handle_response_headers(result, args, kwargs, func)

            # Return appropriate wrapper based on function type
            return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper

        return wrapper

    return decorator


def _handle_response_headers(
    result: Any, args: tuple, kwargs: dict, func: Callable
) -> Any:
    """Handle header injection for decorated endpoints."""
    # Find Response object in args/kwargs
    response = _find_response_object(args, kwargs)

    if response is not None:
        # Get all configs from the function and inject headers
        configs = get_endpoint_configs(func)
        for config in configs.values():
            inject_headers(response, config)

    return result


def _find_response_object(args: tuple, kwargs: dict):
    """Find FastAPI Response object in function arguments."""
    from fastapi import Response
    from starlette.responses import Response as StarletteResponse

    # Check args
    for arg in args:
        if isinstance(arg, (Response, StarletteResponse)):
            return arg

    # Check kwargs
    for value in kwargs.values():
        if isinstance(value, (Response, StarletteResponse)):
            return value

    return None


def deprecated(config: LifecycleConfig):
    """
    Mark an endpoint as deprecated.

    Args:
        config: Configuration dictionary with keys:
            - deprecated_at (str | datetime): When endpoint was deprecated
            - sunset_at (str | datetime, optional): When endpoint will be removed
            - migration_url (str, optional): URL to migration documentation
            - replacement (str, optional): Description of replacement endpoint
            - reason (str, optional): Explanation for deprecation
            - version (str, optional): Current API version

    Example:
        @deprecated({
            'deprecated_at': '2024-01-15T00:00:00Z',
            'sunset_at': '2024-06-15T00:00:00Z',
            'migration_url': 'https://api.example.com/docs/migration',
            'replacement': 'GET /v2/users',
            'reason': 'Moving to v2 API with enhanced user profiles'
        })
        async def get_users_v1():
            return {"users": []}
    """
    return _create_lifecycle_decorator("_deprecated_config")(config)


def sunset(config: LifecycleConfig):
    """
    Mark an endpoint with a sunset date (removal date).

    Args:
        config: Configuration dictionary with keys:
            - sunset_at (str | datetime): When endpoint will be removed
            - migration_url (str, optional): URL to migration documentation
            - replacement (str, optional): Description of replacement endpoint
            - reason (str, optional): Explanation for removal

    Example:
        @sunset({
            'sunset_at': '2024-06-15T00:00:00Z',
            'migration_url': 'https://api.example.com/docs/migration',
            'replacement': 'GET /v2/endpoint',
            'reason': 'Consolidating endpoints for better performance'
        })
        async def old_endpoint():
            return {"data": "will be removed"}
    """
    return _create_lifecycle_decorator("_sunset_config")(config)


def versioned(config: LifecycleConfig):
    """
    Mark an endpoint with comprehensive version information.

    Args:
        config: Configuration dictionary with keys:
            - version (str): API version
            - deprecated_at (str | datetime, optional): When deprecated
            - sunset_at (str | datetime, optional): When will be removed
            - migration_url (str, optional): URL to migration documentation
            - replacement (str, optional): Description of replacement endpoint
            - reason (str, optional): Explanation for version changes

    Example:
        @versioned({
            'version': '1.0',
            'deprecated_at': '2024-01-15T00:00:00Z',
            'sunset_at': '2024-06-15T00:00:00Z',
            'migration_url': 'https://api.example.com/docs/migration',
            'replacement': 'GET /v2/endpoint',
            'reason': 'Enhanced functionality in v2'
        })
        async def versioned_endpoint():
            return {"version": "1.0", "data": "value"}
    """
    return _create_lifecycle_decorator("_versioned_config")(config)
