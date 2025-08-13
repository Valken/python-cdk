import os
from datetime import datetime
from typing import Annotated, Any, List

from aws_lambda_powertools.event_handler.exceptions import NotFoundError
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


@tracer.capture_method
def query_posts_by_topic(topic: str) -> List[dict]:
    logger.info(f"Querying posts for topic: {topic}")
    response = dynamodb.query(
        TableName=table_name,
        IndexName="TopicIndex",
        KeyConditionExpression="PkTopic = :pk",
        ExpressionAttributeValues={
            ":pk": {"S": topic},
        },
        ScanIndexForward=False,
    )
    return [dynamo_to_python(item) for item in response["Items"]]


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


@router.get("/topics")
@tracer.capture_method
def get_topics() -> List[str]:
    response = dynamodb.query(
        TableName=table_name,
        KeyConditionExpression="Pk = :pk",
        ExpressionAttributeValues={
            ":pk": {"S": "Topic"},
        },
        ProjectionExpression="Sk",
    )
    return [item["Sk"]["S"] for item in response["Items"]]


@router.get("/topics/<topic_name>")
@tracer.capture_method
def get_topic(topic_name: str) -> List[Post]:
    logger.info(f"Querying posts for topic: {topic_name}")
    posts = query_posts_by_topic(topic_name)
    if not posts:
        raise NotFoundError()
    return posts


@router.get("/topics/recent")
@tracer.capture_method
def get_recent_topics() -> list[dict[str, Any]]:
    response = dynamodb.query(
        TableName=table_name,
        IndexName="LastUpdatedTopicIndex",
        KeyConditionExpression="Pk = :pk",
        ExpressionAttributeValues={
            ":pk": {"S": "Topic"},
        },
        ProjectionExpression="Sk, LastUpdated",
        Limit=10,
        ScanIndexForward=False,
    )
    return [
        {"topic": item["Sk"]["S"], "lastUpdated": item["LastUpdated"]["S"]}
        for item in response["Items"]
    ]
