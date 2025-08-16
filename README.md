# FastAPI Lifecycle

A clean, decorator-based library for managing API endpoint lifecycle in FastAPI applications. Easily mark endpoints as deprecated, set sunset dates, and provide migration information with automatic HTTP header injection.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com/)

## Features

- 🏷️ **Clean decorator syntax** with dictionary configuration
- 📅 **RFC-compliant headers** (`Deprecation`, `Sunset`, `Link`)
- 🔄 **Automatic header injection** via middleware or decorators
- 📝 **Rich metadata support** (migration URLs, replacement endpoints, reasons)
- ⚡ **Zero performance overhead** when not using versioning
- 🎯 **Type hints** and IDE support throughout

## Installation

```bash
pip install fastapi-lifecycle
```

## Quick Start

```python
from fastapi import FastAPI
from fastapi_lifecycle import deprecated, setup_versioning

app = FastAPI()
setup_versioning(app)  # Add the middleware

@app.get("/users")
@deprecated({
    'deprecated_at': '2024-01-15T00:00:00Z',
    'sunset_at': '2024-06-15T00:00:00Z',
    'migration_url': 'https://api.example.com/docs/migration#users-v2',
    'replacement': 'GET /v2/users',
    'reason': 'Moving to v2 API with enhanced user profiles'
})
async def get_users():
    return {"users": []}
```

**Response headers:**
```http
Deprecation: Mon, 15 Jan 2024 00:00:00 GMT
Sunset: Sat, 15 Jun 2024 00:00:00 GMT
Link: <https://api.example.com/docs/migration#users-v2>; rel="deprecation"
X-API-Replacement: GET /v2/users
X-API-Deprecation-Reason: Moving to v2 API with enhanced user profiles
```

## API Reference

### `@deprecated(config)`

Mark an endpoint as deprecated with comprehensive configuration.

**Configuration options:**
- `deprecated_at` (str | datetime): When the endpoint was deprecated
- `sunset_at` (str | datetime): When the endpoint will be removed
- `migration_url` (str): URL to migration documentation
- `replacement` (str): Description of replacement endpoint
- `reason` (str): Explanation for deprecation
- `version` (str): Current API version

```python
@deprecated({
    'deprecated_at': '2024-01-15T00:00:00Z',
    'reason': 'Use /v2/endpoint instead'
})
async def old_endpoint():
    return {"message": "deprecated"}
```

### `@sunset(config)`

Mark an endpoint with a removal date.

**Configuration options:**
- `sunset_at` (str | datetime): When endpoint will be removed *(required)*
- `migration_url` (str): URL to migration documentation
- `replacement` (str): Description of replacement endpoint
- `reason` (str): Explanation for removal

```python
@sunset({
    'sunset_at': '2024-12-31T23:59:59Z',
    'migration_url': 'https://docs.api.com/migration',
    'replacement': 'GET /v3/data'
})
async def ending_endpoint():
    return {"data": "will be removed"}
```

### `@versioned(config)`

Comprehensive version management with deprecation and sunset support.

**Configuration options:**
- `version` (str): API version *(required)*
- `deprecated_at` (str | datetime): When deprecated
- `sunset_at` (str | datetime): When will be removed
- `migration_url` (str): Migration documentation URL
- `replacement` (str): Replacement endpoint description
- `reason` (str): Version change explanation

```python
@versioned({
    'version': '1.2',
    'deprecated_at': '2024-03-01T00:00:00Z',
    'sunset_at': '2024-09-01T00:00:00Z',
    'migration_url': 'https://docs.api.com/v2-migration'
})
async def versioned_endpoint():
    return {"version": "1.2"}
```

## Date Formats

The library accepts dates in multiple formats:

```python
# ISO 8601 strings (recommended)
'deprecated_at': '2024-01-15T00:00:00Z'
'deprecated_at': '2024-01-15T10:30:00+02:00'

# Python datetime objects
from datetime import datetime
'deprecated_at': datetime(2024, 1, 15)
```

## HTTP Headers Generated

| Header | Description | Example |
|--------|-------------|---------|
| `Deprecation` | RFC 8594 deprecation date | `Mon, 15 Jan 2024 00:00:00 GMT` |
| `Sunset` | RFC 8594 sunset date | `Sat, 15 Jun 2024 00:00:00 GMT` |
| `Link` | RFC 8288 link to documentation | `<https://docs.api.com/migration>; rel="deprecation"` |
| `X-API-Version` | Current API version | `1.2` |
| `X-API-Replacement` | Replacement endpoint info | `GET /v2/users` |
| `X-API-Deprecation-Reason` | Human-readable reason | `Enhanced functionality in v2` |

## Advanced Usage

### Multiple Decorators

Stack decorators for complex scenarios:

```python
@versioned({'version': '1.0'})
@deprecated({
    'deprecated_at': '2024-01-15T00:00:00Z',
    'reason': 'Migrating to GraphQL'
})
async def complex_endpoint():
    return {"data": "complex"}
```

### With Explicit Response Objects

Works seamlessly with FastAPI's Response dependency:

```python
from fastapi import Response

@deprecated({'deprecated_at': '2024-01-15T00:00:00Z'})
async def endpoint_with_response(response: Response):
    response.status_code = 200
    return {"message": "Custom response handling"}
```

### Conditional Versioning

Apply versioning based on conditions:

```python
from fastapi_lifecycle import deprecated

def get_endpoint_config():
    if FEATURE_FLAG_V2_MIGRATION:
        return {
            'deprecated_at': '2024-01-15T00:00:00Z',
            'sunset_at': '2024-06-15T00:00:00Z',
            'replacement': 'GET /v2/endpoint'
        }
    return {}

@deprecated(get_endpoint_config())
async def conditional_endpoint():
    return {"data": "conditional"}
```

## Requirements

- Python 3.8+
- FastAPI 0.68+
- python-dateutil

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Related Standards

This library implements headers according to:

- [RFC 8594](https://tools.ietf.org/html/rfc8594) - The Sunset HTTP Header Field
- [RFC 8288](https://tools.ietf.org/html/rfc8288) - Web Linking (Link header)
- [Internet-Draft](https://tools.ietf.org/html/draft-dalal-deprecation-header) - The Deprecation HTTP Header Field

## Examples

Check out the `examples/` directory for more comprehensive usage examples including:

- Basic deprecation scenarios
- Complex migration workflows
- Integration with API documentation
- Custom middleware configurations