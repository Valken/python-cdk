import os
from datetime import datetime
from typing import Annotated, List

from aws_lambda_powertools.event_handler.openapi.params import Query
from aws_lambda_powertools.event_handler.router import Router
from boto3 import client
from dateutil.relativedelta import relativedelta
from mypy_boto3_dynamodb.client import DynamoDBClient

from api.partition_generators import get_year_month_range
from api.schemas import Post
from api.shared import dynamo_to_python, logger, tracer


def get_client() -> DynamoDBClient:
    return client("dynamodb")


dynamodb = get_client()  # client("dynamodb", region_name="eu-west-1")
table_name = os.environ.get("TABLE_NAME")
router = Router()


@tracer.capture_method
def query_posts_by_date_range(from_date: datetime, to_date: datetime) -> List[dict]:
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
            ScanIndexForward=False,
        )
        posts.extend([dynamo_to_python(item) for item in response["Items"]])
    return posts


@router.get("/posts")
@tracer.capture_method
def get_posts(
    # I can't seem to get using a model for query parameters to work like you can in FastAPI?
    from_date: Annotated[datetime, Query()] = datetime.now(),
    to_date: Annotated[datetime, Query()] = datetime.now() - relativedelta(months=6),
) -> List[Post]:
    logger.info(f"Querying posts from {from_date} to {to_date}")
    queried_posts = query_posts_by_date_range(from_date, to_date)
    logger.info(f"Queried {len(queried_posts)} posts")
    return [Post(**item) for item in queried_posts]
