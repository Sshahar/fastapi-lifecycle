"""Example usage of fastapi-lifecycle package."""

if __name__ == "__main__":
    from fastapi import FastAPI
    import uvicorn

    from fastapi_lifecycle import deprecated, sunset, versioned, setup_versioning

    # Create FastAPI app
    app = FastAPI(title="FastAPI Lifecycle Example")

    # Setup lifecycle management (using middleware approach)
    setup_versioning(app)

    @app.get("/")
    async def root():
        """Root endpoint with no lifecycle information."""
        return {"message": "Hello World"}

    @app.get("/deprecated-endpoint")
    @deprecated(
        {
            "deprecated_at": "2024-01-15T00:00:00Z",
            "sunset_at": "2024-06-15T00:00:00Z",
            "migration_url": "https://api.example.com/docs/migration#users-v2",
            "replacement": "GET /v2/users",
            "reason": "Moving to v2 API with enhanced user profiles",
        }
    )
    async def deprecated_endpoint():
        """Example of a deprecated endpoint."""
        return {"message": "This endpoint is deprecated"}

    @app.get("/sunset-endpoint")
    @sunset(
        {
            "sunset_at": "2024-06-15T00:00:00Z",
            "migration_url": "https://api.example.com/docs/migration",
            "replacement": "GET /v2/endpoint",
            "reason": "Consolidating endpoints for better performance",
        }
    )
    async def sunset_endpoint():
        """Example of an endpoint with sunset date."""
        return {"message": "This endpoint will be removed"}

    @app.get("/versioned-endpoint")
    @versioned(
        {
            "version": "1.0",
            "deprecated_at": "2024-01-15T00:00:00Z",
            "sunset_at": "2024-06-15T00:00:00Z",
            "migration_url": "https://api.example.com/docs/migration",
            "replacement": "GET /v2/endpoint",
            "reason": "Enhanced functionality in v2",
        }
    )
    async def versioned_endpoint():
        """Example of a comprehensively versioned endpoint."""
        return {"message": "This is a versioned endpoint", "version": "1.0"}

    print("Starting server...")
    print("Test endpoints:")
    print("  curl -I http://localhost:8000/deprecated-endpoint")
    print("  curl -I http://localhost:8000/versioned-endpoint")

    uvicorn.run(app, host="0.0.0.0", port=8000)
