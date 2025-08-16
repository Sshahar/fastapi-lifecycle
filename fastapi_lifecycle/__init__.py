"""
FastAPI Lifecycle - API endpoint lifecycle management for FastAPI.

This package provides decorators and middleware for managing API endpoint
lifecycle including deprecation, sunset dates, and versioning information.
"""

from .decorators import deprecated, sunset, versioned
from .middleware import VersioningMiddleware, setup_versioning
from .route import LifecycleAPIRoute, setup_versioning_with_route_class
from .headers import VersioningHeaders
from .dependencies import inject_lifecycle_headers

__version__ = "0.1.0"
__author__ = "FastAPI Lifecycle Contributors"
__email__ = "fastapi-lifecycle@example.com"

__all__ = [
    "deprecated",
    "sunset",
    "versioned",
    "VersioningMiddleware",
    "setup_versioning",
    "LifecycleAPIRoute",
    "setup_versioning_with_route_class",
    "VersioningHeaders",
    "inject_lifecycle_headers",
]
