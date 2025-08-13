from typing import Any

from aws_lambda_powertools.event_handler.router import Router
from aws_lambda_powertools.utilities import parameters

from api.schemas import Model
from api.shared import logger, tracer

router = Router()
ssm_provider = parameters.SSMProvider()


@router.get("/")
@tracer.capture_method
def get_threedos() -> dict[str, Any]:
    something_param: Any = ssm_provider.get("/hello-world/something")
    logger.info("Fetched parameter: %s", something_param)
    return {"hello": something_param}


@router.post("/pets")
@tracer.capture_method
def post_pets(model: Model) -> dict[str, Model]:
    logger.info(model)
    return {"message": model}


@router.get("/<thing_id>")
def get_thing(thing_id: str) -> dict[str, str]:
    logger.info(f"Fetching thing with ID: {thing_id}")
    return {"thing_id": thing_id, "message": "Thing fetched successfully"}
