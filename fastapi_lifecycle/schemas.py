"""Type definitions for the fastapi-lifecycle package."""

from datetime import datetime
from typing import Dict, Any, Union

# Configuration dictionary type for decorators
LifecycleConfig = Dict[str, Any]

# Supported date types
DateType = Union[datetime, str]


# Standard lifecycle configuration keys
class ConfigKeys:
    """Standard configuration keys for lifecycle decorators."""

    DEPRECATED_AT = "deprecated_at"
    SUNSET_AT = "sunset_at"
    MIGRATION_URL = "migration_url"
    REPLACEMENT = "replacement"
    REASON = "reason"
    VERSION = "version"
