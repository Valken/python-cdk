# AWS Lambda Powertools Python Best Practices

Apply these patterns when building serverless APIs with AWS Lambda Powertools for Python.

## Core Principles

- Use Python 3.11+ syntax
- Follow PEP8 style guidelines
- Use type hints for all functions
- Prefer absolute imports
- Organize routes by REST resource (noun), not verb

## Project Structure

```
api/
├── __init__.py
├── handler.py           # Main Lambda handler with app
├── shared.py            # Logger, Tracer, shared utilities
├── schemas.py           # Pydantic models
├── thing_routes.py      # Routes for /thing resource
├── post_routes.py       # Routes for /post resource
├── user_routes.py       # Routes for /user resource
└── tests/
    ├── test_thing_routes.py
    └── test_post_routes.py
```

## Router Pattern

### Define Router per Resource

In each `<noun>_routes.py` file, define a `router = Router()` and use it for all route decorators.

**Example: `thing_routes.py`**

```python
from aws_lambda_powertools.event_handler.router import Router
from pydantic import BaseModel

from api.shared import logger, tracer

router = Router()

class Thing(BaseModel):
    name: str
    size: int

@router.post("/thing/<name>")
@tracer.capture_method
def create_thing(name: str, body: Thing) -> dict:
    logger.info("Creating thing", extra={"name": name, "size": body.size})
    return {"message": "Thing created", "data": body.model_dump()}

@router.get("/thing/<thing_id>")
@tracer.capture_method
def get_thing(thing_id: str) -> dict:
    logger.info("Fetching thing", extra={"thing_id": thing_id})
    return {"thing_id": thing_id}
```

### Include Routers in Main Handler

**Example: `handler.py`**

```python
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.utilities.typing import LambdaContext

from api.thing_routes import router as thing_router
from api.post_routes import router as post_router
from api.shared import logger, tracer

app = APIGatewayHttpResolver(enable_validation=True)
app.include_router(thing_router, prefix="/stuff")
app.include_router(post_router)

@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_HTTP)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
```

## Path Parameters

- Use angle brackets: `/thing/<thing_id>`
- NOT curly braces (FastAPI style): `/thing/{thing_id}`
- Parameters are injected as function arguments

```python
@router.get("/posts/<post_id>")
def get_post(post_id: str) -> dict:
    return {"post_id": post_id}
```

## Request Body Validation

Inject Pydantic models as function parameters instead of manually parsing `current_event.json_body`.

**Preferred:**

```python
@router.post("/thing/<name>")
def create_thing(name: str, body: Thing) -> dict:
    # `body` is already a validated Thing instance
    logger.info("Creating thing", extra={"name": name})
    return {"data": body.model_dump()}
```

**Avoid:**

```python
@router.post("/thing/<name>")
def create_thing(name: str) -> dict:
    body = app.current_event.json_body
    thing = Thing(**body)  # Manual parsing
    return {"data": thing.model_dump()}
```

## Query Parameters with Annotated

```python
from typing import Annotated
from aws_lambda_powertools.event_handler.openapi.params import Query, Path

@router.get("/items/<item_id>")
def get_item(
    item_id: Annotated[str, Path()],
    limit: Annotated[int, Query()] = 10,
    filter: Annotated[str | None, Query()] = None
) -> dict:
    logger.info("Fetching items", extra={"limit": limit, "filter": filter})
    return {"items": []}
```

## Pydantic Models

### Basic Models

```python
from pydantic import BaseModel, Field

class Thing(BaseModel):
    name: str
    size: int
    description: str | None = None
```

### Discriminated Unions

```python
from typing import Literal
from pydantic import BaseModel, Field

class Cat(BaseModel):
    pet_type: Literal["cat"]
    meows: int

class Dog(BaseModel):
    pet_type: Literal["dog"]
    barks: float

class Pet(BaseModel):
    pet: Cat | Dog = Field(discriminator="pet_type")
    name: str
```

### Field Aliases for DynamoDB

```python
from datetime import datetime
from pydantic import BaseModel, Field

class Post(BaseModel):
    topic: str | None = Field(alias="PkTopic", default=None)
    content: str = Field(alias="Content")
    post_time: datetime = Field(alias="Sk")
```

## Observability

### Shared Logger and Tracer

**`shared.py`**

```python
from aws_lambda_powertools import Logger, Tracer

logger = Logger()
tracer = Tracer()
```

### Structured Logging

```python
# Good - structured with extra fields
logger.info("Processing request", extra={
    "thing_id": thing_id,
    "user_id": user_id,
    "action": "create"
})

# Avoid - only string formatting
logger.info(f"Processing thing {thing_id}")
```

### Lambda Handler Decorators

```python
@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_HTTP)
@tracer.capture_lambda_handler
def lambda_handler(event: dict, context: LambdaContext) -> dict:
    return app.resolve(event, context)
```

### Method Tracing

```python
@tracer.capture_method
def process_thing(thing_id: str):
    logger.info("Processing thing", extra={"thing_id": thing_id})
    # Business logic
```

### Manual Subsegments

```python
with tracer.provider.in_subsegment("dynamodb_query"):
    response = dynamodb.query(...)
```

## Error Handling

```python
from aws_lambda_powertools.event_handler.exceptions import (
    NotFoundError,
    BadRequestError,
    InternalServerError
)

@router.get("/thing/<thing_id>")
def get_thing(thing_id: str) -> dict:
    thing = fetch_thing(thing_id)
    if not thing:
        raise NotFoundError(f"Thing {thing_id} not found")
    return thing
```

## SSM Parameter Store

```python
from aws_lambda_powertools.utilities import parameters

ssm_provider = parameters.SSMProvider()

@router.get("/config")
@tracer.capture_method
def get_config() -> dict:
    config_value = ssm_provider.get("/my-app/config/setting")
    logger.info("Fetched config", extra={"config": config_value})
    return {"config": config_value}
```

## DynamoDB Integration

```python
import os
from boto3 import client
from mypy_boto3_dynamodb.client import DynamoDBClient

from api.shared import logger, tracer, dynamo_to_python

def get_client() -> DynamoDBClient:
    return client("dynamodb")

dynamodb = get_client()
table_name = os.environ.get("TABLE_NAME")

@tracer.capture_method
def query_items(partition_key: str) -> list[dict]:
    logger.info("Querying items", extra={"partition_key": partition_key})
    response = dynamodb.query(
        TableName=table_name,
        KeyConditionExpression="Pk = :pk",
        ExpressionAttributeValues={":pk": {"S": partition_key}},
    )
    return [dynamo_to_python(item) for item in response["Items"]]
```

## Testing

```python
import pytest
from api.handler import app

def test_get_thing():
    event = {
        "requestContext": {
            "http": {
                "method": "GET",
                "path": "/thing/123"
            }
        }
    }
    response = app.resolve(event, {})
    assert response["statusCode"] == 200

def test_create_thing():
    event = {
        "requestContext": {
            "http": {
                "method": "POST",
                "path": "/thing/my-thing"
            }
        },
        "body": '{"name": "test", "size": 42}'
    }
    response = app.resolve(event, {})
    assert response["statusCode"] == 200
```

## OpenAPI Schema Generation

Enable automatic OpenAPI schema generation:

```python
app = APIGatewayHttpResolver(enable_validation=True)

# Access the generated schema
schema = app.get_openapi_schema()
```

## Key Differences from FastAPI

| Feature | FastAPI | Lambda Powertools |
|---------|---------|-------------------|
| Path params | `/thing/{id}` | `/thing/<id>` |
| Router | `APIRouter()` | `Router()` |
| App | `FastAPI()` | `APIGatewayHttpResolver()` |
| Handler | `app(request)` | `app.resolve(event, context)` |
| Imports | `from fastapi import` | `from aws_lambda_powertools.event_handler import` |

## Best Practices Summary

1. Organize handler files by REST resource (noun), not verb
2. Define a `router = Router()` in each resource handler file
3. Include routers in `handler.py` with `app.include_router()`
4. Use angle brackets `<param>` for path parameters
5. Inject request bodies as Pydantic model parameters
6. Use `Annotated` for query and path parameters
7. Enable structured logging with `extra` fields
8. Add `@tracer.capture_method` to business logic functions
9. Handle errors with appropriate Lambda Powertools exceptions
10. Write unit tests for all route handlers
