import os
from typing import Any

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from aws_lambda_powertools.event_handler.router import Router
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities import parameters

# from models.model import Model
from api.models.model import Model

tracer = Tracer()
logger = Logger()
app = APIGatewayHttpResolver(enable_validation=True)
router = Router()
ssm_provider = parameters.SSMProvider()


@router.get("/")
@tracer.capture_method
def get_todos():
    logger.info("Hello World")
    return {"message": "Hello World"}


@router.get("/hello")
@tracer.capture_method
def get_threedos():
    something_param: Any = ssm_provider.get("/hello-world/something")
    logger.info(os.environ["PYTHONPATH"])
    return {"hello": something_param}


@router.post("/pets")
@tracer.capture_method
def post_pets(model: Model):
    logger.info(model)
    return {"message": "Hello World"}


app.include_router(router)


# You can continue to use other utilities just as before
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_HTTP)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
