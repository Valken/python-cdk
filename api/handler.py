from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

from api.post_routes import router as post_router
from api.shared import logger, tracer
from api.thing_routes import router as thing_router

app = APIGatewayHttpResolver(enable_validation=True)
app.include_router(thing_router)
app.include_router(post_router)


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_HTTP)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)


# def another_handler(event: dict, context: LambdaContext) -> dict:
#     logger.info("Another handler invoked")
#     return {"statusCode": 200, "body": "This is another handler response"}
