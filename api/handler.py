import os

from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext
from boto3 import client
from datetime import datetime
from dateutil.relativedelta import relativedelta


from api.shared import logger, tracer, dynamo_to_python
from api.routes import router
from api.schemas import Post
from api.partition_generators import get_year_month_range

app = APIGatewayHttpResolver(enable_validation=True)
app.include_router(router)

dynamodb = client("dynamodb", region_name="eu-west-1")
table_name = os.environ.get("TABLE_NAME")


@app.get("/")
@tracer.capture_method
def get_todos():
    logger.info("Hello World")
    return {"message": "Hello World"}


def query_posts_by_date_range(from_date, to_date):
    posts = []
    for year_month in get_year_month_range(from_date, to_date):
        partition_key = f"Post#{year_month}"
        logger.info(f"Querying posts for partition key: {partition_key}")
        response = dynamodb.query(
            TableName=table_name,
            KeyConditionExpression="Pk = :pk",
            ExpressionAttributeValues={
                ":pk": {"S": partition_key},
            },
        )
        logger.info(f"Response from DynamoDB: {response}")
        posts.extend([Post(**dynamo_to_python(item)) for item in response["Items"]])
    return posts


@app.get("/posts")
def get_posts():
    # items = dynamodb.scan(
    #     TableName=table_name,
    #     FilterExpression="begins_with(Pk, :pk_begin)",
    #     ExpressionAttributeValues={
    #         ":pk_begin": {"S": "Post#"},
    #     },
    # )["Items"]
    to_date = datetime.now()
    from_date = to_date - relativedelta(months=6)
    logger.info(f"Querying posts from {from_date} to {to_date}")
    queried_posts = query_posts_by_date_range(from_date, to_date)
    logger.info(f"Queried {len(queried_posts)} posts")
    return [Post(**item) for item in queried_posts]


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_HTTP)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
