import os
from datetime import datetime
from typing import Any, List

from boto3 import client
from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, HTTPException, Query
from mypy_boto3_dynamodb.client import DynamoDBClient

from api.partition_generators import get_year_month_range
from api.schemas import Post
from api.shared import dynamo_to_python, logger, tracer


def get_client() -> DynamoDBClient:
    return client("dynamodb")


dynamodb = get_client()  # client("dynamodb", region_name="eu-west-1")
table_name = os.environ.get("TABLE_NAME")
router = APIRouter()


@tracer.capture_method
def query_posts_by_date_range(from_date: datetime, to_date: datetime) -> List[dict]:
    """Query posts within a date range."""
    posts = []
    for year_month in get_year_month_range(from_date, to_date):
        partition_key = f"Post#{year_month}"
        logger.info("Querying posts", extra={"partition_key": partition_key})
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
    """Query posts by topic using GSI."""
    logger.info("Querying posts by topic", extra={"topic": topic})
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
    from_date: datetime = Query(default_factory=datetime.now),
    to_date: datetime = Query(
        default_factory=lambda: datetime.now() - relativedelta(months=6)
    ),
) -> List[Post]:
    """Get posts within a date range."""
    logger.info("Querying posts", extra={"from_date": from_date, "to_date": to_date})
    queried_posts = query_posts_by_date_range(from_date, to_date)
    logger.info("Queried posts", extra={"count": len(queried_posts)})
    return [Post(**item) for item in queried_posts]


@router.get("/topics")
@tracer.capture_method
def get_topics() -> List[str]:
    """Get all available topics."""
    response = dynamodb.query(
        TableName=table_name,
        KeyConditionExpression="Pk = :pk",
        ExpressionAttributeValues={
            ":pk": {"S": "Topic"},
        },
        ProjectionExpression="Sk",
    )
    return [item["Sk"]["S"] for item in response["Items"]]


@router.get("/topics/{topic_name}")
@tracer.capture_method
def get_topic(topic_name: str) -> List[Post]:
    """Get posts for a specific topic."""
    logger.info("Querying posts for topic", extra={"topic": topic_name})
    posts = query_posts_by_topic(topic_name)
    if not posts:
        raise HTTPException(status_code=404, detail=f"Topic '{topic_name}' not found")
    return [Post(**post) for post in posts]


@router.get("/topics/recent")
@tracer.capture_method
def get_recent_topics() -> list[dict[str, Any]]:
    """Get recently updated topics."""
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
