#!/usr/bin/env python
"""
Local development server for the FastAPI application.

This script runs the API locally using uvicorn for development and testing.
It disables Lambda Powertools features that require AWS Lambda context.
"""

import os

# IMPORTANT: Set these BEFORE importing anything from api package
# Disable Lambda Powertools features that require Lambda context
os.environ["POWERTOOLS_DEV"] = "1"
os.environ["POWERTOOLS_TRACE_DISABLED"] = "1"
os.environ["POWERTOOLS_METRICS_NAMESPACE"] = "local"
os.environ["AWS_EXECUTION_ENV"] = "AWS_Lambda_python3.13"  # Pretend to be in Lambda
os.environ["_X_AMZN_TRACE_ID"] = (
    "Root=1-00000000-000000000000000000000000"  # Mock trace ID
)

# Set mock values for required environment variables
os.environ.setdefault("TABLE_NAME", "mock-table")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("POWERTOOLS_SERVICE_NAME", "hello-api-local")

if __name__ == "__main__":
    import uvicorn

    # Import the FastAPI app (not the lambda_handler)
    from api.handler import app

    print("🚀 Starting local development server...")
    print("📖 API documentation available at:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("\n⚠️  Note: Running in local development mode")
    print("⚠️  Note: X-Ray tracing will create local segments only")
    print("⚠️  Note: SSM parameter lookups require AWS credentials\n")

    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
