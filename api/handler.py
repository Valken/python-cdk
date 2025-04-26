from typing import Any

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities import parameters

tracer = Tracer()
logger = Logger()
app = APIGatewayHttpResolver()
ssm_provider = parameters.SSMProvider()


@app.get("/")
@tracer.capture_method
def get_todos():
    logger.info("Hello World")
    return {"message": "Hello World"}


@app.get("/hello")
@tracer.capture_method
def get_threedos():
    something_param: Any = ssm_provider.get("/hello-world/something")
    return {"hello": something_param}


# You can continue to use other utilities just as before
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_HTTP)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
