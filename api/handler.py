import os

from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from boto3 import client
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

from api.shared import logger, tracer
from api.routes import router
from api.schemas import Post

app = APIGatewayHttpResolver(enable_validation=True)
app.include_router(router)

dynamodb = client("dynamodb", region_name="eu-west-1")
table_name = os.environ.get("TABLE_NAME")


@app.get("/")
@tracer.capture_method
def get_todos():
    logger.info("Hello World")
    return {"message": "Hello World"}


@app.get("/posts")
def get_posts():
    items = dynamodb.scan(
        TableName=table_name,
        FilterExpression="begins_with(Pk, :pk_begin)",
        ExpressionAttributeValues={
            ":pk_begin": {"S": "Post#"},
        },
    )["Items"]
    return [Post(**dynamo_to_python(item)) for item in items]


# From https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/programming-with-python.html
def dynamo_to_python(dynamo_object: dict) -> dict:
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in dynamo_object.items()}


def python_to_dynamo(python_object: dict) -> dict:
    serializer = TypeSerializer()
    return {k: serializer.serialize(v) for k, v in python_object.items()}


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_HTTP)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
