from typing import Any
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools.event_handler.router import Router

# from models.model import Model
from api.schemas import Model
from api.shared import logger, tracer

router = Router()
ssm_provider = parameters.SSMProvider()


@router.get("/hello")
@tracer.capture_method
def get_threedos():
    something_param: Any = ssm_provider.get("/hello-world/something")
    logger.info("Fetched parameter: %s", something_param)
    return {"hello": something_param}


@router.post("/pets")
@tracer.capture_method
def post_pets(model: Model):
    logger.info(model)
    return {"message": model}
