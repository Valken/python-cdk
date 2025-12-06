from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from fastapi import FastAPI
from mangum import Mangum

from api.post_routes import router as post_router
from api.shared import tracer
from api.thing_routes import router as thing_router

# Initialize Powertools logger
logger = Logger()

app = FastAPI(title="Hello API", version="0.1.0")

# Include routers
app.include_router(thing_router, prefix="/stuff", tags=["things"])
app.include_router(post_router, tags=["posts"])


@app.get("/")
def root():
    """Root endpoint for health checks."""
    return {"message": "API is running"}


# Create Mangum handler
_mangum_handler = Mangum(app, lifespan="off")


# Wrap with Lambda Powertools decorators
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_HTTP)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    """Lambda handler with Powertools logging and tracing."""
    return _mangum_handler(event, context)


# def another_handler(event: dict, context: LambdaContext) -> dict:
#     logger.info("Another handler invoked")
#     return {"statusCode": 200, "body": "This is another handler response"}
