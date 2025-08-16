"""Utility functions for header injection and configuration validation."""

from typing import Union, Dict, Any

from fastapi import Response
from starlette.responses import Response as StarletteResponse

from .headers import VersioningHeaders
from .schemas import LifecycleConfig, ConfigKeys


def inject_headers(
    response: Union[Response, StarletteResponse], config: LifecycleConfig
) -> None:
    """
    Inject lifecycle headers into HTTP response.

    Args:
        response: FastAPI or Starlette response object
        config: Configuration dictionary with lifecycle metadata
    """
    if not config:
        return

    # Add deprecation header (RFC 8594)
    if config.get(ConfigKeys.DEPRECATED_AT):
        response.headers["Deprecation"] = VersioningHeaders.format_http_date(
            config[ConfigKeys.DEPRECATED_AT]
        )

    # Add sunset header (RFC 8594)
    if config.get(ConfigKeys.SUNSET_AT):
        response.headers["Sunset"] = VersioningHeaders.format_http_date(
            config[ConfigKeys.SUNSET_AT]
        )

    # Add migration link (RFC 8288)
    if config.get(ConfigKeys.MIGRATION_URL):
        response.headers["Link"] = VersioningHeaders.create_link_header(
            config[ConfigKeys.MIGRATION_URL]
        )

    # Add custom headers for additional metadata
    if config.get(ConfigKeys.VERSION):
        response.headers["X-API-Version"] = str(config[ConfigKeys.VERSION])

    if config.get(ConfigKeys.REPLACEMENT):
        response.headers["X-API-Replacement"] = str(config[ConfigKeys.REPLACEMENT])

    if config.get(ConfigKeys.REASON):
        response.headers["X-API-Deprecation-Reason"] = str(config[ConfigKeys.REASON])


def get_endpoint_configs(endpoint) -> Dict[str, LifecycleConfig]:
    """
    Extract all lifecycle configurations from an endpoint function.

    Args:
        endpoint: FastAPI endpoint function

    Returns:
        Dictionary mapping config types to their configurations
    """
    configs = {}

    config_attrs = {
        "deprecated": "_deprecated_config",
        "sunset": "_sunset_config",
        "versioned": "_versioned_config",
    }

    for config_type, attr_name in config_attrs.items():
        if hasattr(endpoint, attr_name):
            configs[config_type] = getattr(endpoint, attr_name)

    return configs


def validate_config(config: LifecycleConfig) -> None:
    """
    Validate lifecycle configuration dictionary.

    Args:
        config: Configuration to validate

    Raises:
        ValueError: If configuration is invalid
    """
    if not isinstance(config, dict):
        raise ValueError("Configuration must be a dictionary")

    # Validate date fields if present
    date_fields = [ConfigKeys.DEPRECATED_AT, ConfigKeys.SUNSET_AT]
    for field in date_fields:
        if field in config and config[field] is not None:
            try:
                VersioningHeaders.format_http_date(config[field])
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid date format for {field}: {e}")
