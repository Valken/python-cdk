import os
from typing import Any

from fastapi import APIRouter

from api.schemas import Model
from api.shared import logger, tracer

router = APIRouter()


def get_ssm_parameter(name: str) -> Any:
    """Get parameter from SSM Parameter Store, with fallback for local development."""
    # Only import parameters when actually needed (avoid import-time issues)
    if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        # In Lambda, use Powertools parameters utility
        from aws_lambda_powertools.utilities import parameters

        return parameters.get_parameter(name)
    else:
        # In local development, return a mock value
        logger.warning(f"Local mode: returning mock value for parameter {name}")
        return f"mock-value-for-{name}"


@router.get("/")
@tracer.capture_method
def get_threedos() -> dict[str, Any]:
    """Get a parameter from SSM and return it."""
    something_param: Any = get_ssm_parameter("/hello-world/something")
    logger.info("Fetched parameter", extra={"parameter": something_param})
    return {"hello": something_param}


@router.post("/pets")
@tracer.capture_method
def post_pets(model: Model) -> dict[str, Model]:
    """Create a new pet."""
    logger.info("Received pet", extra={"pet": model})
    return {"message": model}


@router.get("/{thing_id}")
@tracer.capture_method
def get_thing(thing_id: str) -> dict[str, str]:
    """Get a specific thing by ID."""
    logger.info("Fetching thing", extra={"thing_id": thing_id})
    return {"thing_id": thing_id, "message": "Thing fetched successfully"}
