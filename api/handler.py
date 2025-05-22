from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

from api.shared import logger, tracer
from api.routes import router


app = APIGatewayHttpResolver(enable_validation=True)
app.include_router(router)


@app.get("/")
@tracer.capture_method
def get_todos():
    logger.info("Hello World")
    return {"message": "Hello World"}


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_HTTP)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
