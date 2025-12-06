# Generate Lambda API Route

Generate a new API route handler for an AWS Lambda Powertools API following best practices.

## Instructions

You will create a new route handler file for a REST resource. Follow these guidelines:

1. **Resource Organization**: Create routes organized by resource (noun), not verb
2. **Router Pattern**: Define a `router = Router()` at the top of the file
3. **Observability**: Import and use `logger` and `tracer` from `api.shared`
4. **Validation**: Use Pydantic models for request/response validation
5. **Path Parameters**: Use angle brackets `<param>` syntax
6. **Body Injection**: Inject request bodies as typed Pydantic parameters
7. **Error Handling**: Use Lambda Powertools exceptions

## File Template

Create a new file: `api/<resource>_routes.py`

```python
from typing import Annotated, Any
from aws_lambda_powertools.event_handler.router import Router
from aws_lambda_powertools.event_handler.openapi.params import Query
from aws_lambda_powertools.event_handler.exceptions import NotFoundError, BadRequestError
from pydantic import BaseModel

from api.shared import logger, tracer

router = Router()

# Define your Pydantic models
class <Resource>(BaseModel):
    # Add fields here
    name: str
    value: int

class <Resource>Response(BaseModel):
    # Add response fields
    id: str
    data: <Resource>

# Define your route handlers
@router.get("/<resource>")
@tracer.capture_method
def list_<resource>s(
    limit: Annotated[int, Query()] = 10,
    offset: Annotated[int, Query()] = 0
) -> dict[str, Any]:
    """List all <resource>s with pagination."""
    logger.info("Listing <resource>s", extra={"limit": limit, "offset": offset})
    # TODO: Implement business logic
    return {"items": [], "total": 0}

@router.get("/<resource>/<resource_id>")
@tracer.capture_method
def get_<resource>(resource_id: str) -> <Resource>Response:
    """Get a single <resource> by ID."""
    logger.info("Fetching <resource>", extra={"resource_id": resource_id})
    # TODO: Implement fetch logic
    # if not found:
    #     raise NotFoundError(f"<Resource> {resource_id} not found")
    return <Resource>Response(id=resource_id, data=<Resource>(name="example", value=42))

@router.post("/<resource>")
@tracer.capture_method
def create_<resource>(body: <Resource>) -> <Resource>Response:
    """Create a new <resource>."""
    logger.info("Creating <resource>", extra={"name": body.name})
    # TODO: Implement creation logic
    return <Resource>Response(id="new-id", data=body)

@router.put("/<resource>/<resource_id>")
@tracer.capture_method
def update_<resource>(resource_id: str, body: <Resource>) -> <Resource>Response:
    """Update an existing <resource>."""
    logger.info("Updating <resource>", extra={"resource_id": resource_id})
    # TODO: Implement update logic
    return <Resource>Response(id=resource_id, data=body)

@router.delete("/<resource>/<resource_id>")
@tracer.capture_method
def delete_<resource>(resource_id: str) -> dict[str, str]:
    """Delete a <resource>."""
    logger.info("Deleting <resource>", extra={"resource_id": resource_id})
    # TODO: Implement deletion logic
    return {"message": f"<Resource> {resource_id} deleted"}
```

## Update handler.py

After creating the route file, add it to `api/handler.py`:

```python
from api.<resource>_routes import router as <resource>_router

app.include_router(<resource>_router, prefix="/<prefix>")  # Optional prefix
```

## Create Unit Tests

Create a test file: `api/tests/test_<resource>_routes.py`

```python
import pytest
from api.handler import app

def test_list_<resource>s():
    event = {
        "requestContext": {"http": {"method": "GET", "path": "/<resource>"}},
        "queryStringParameters": {"limit": "5"}
    }
    response = app.resolve(event, {})
    assert response["statusCode"] == 200

def test_get_<resource>():
    event = {
        "requestContext": {"http": {"method": "GET", "path": "/<resource>/123"}}
    }
    response = app.resolve(event, {})
    assert response["statusCode"] == 200

def test_create_<resource>():
    event = {
        "requestContext": {"http": {"method": "POST", "path": "/<resource>"}},
        "body": '{"name": "test", "value": 42}'
    }
    response = app.resolve(event, {})
    assert response["statusCode"] == 200

def test_update_<resource>():
    event = {
        "requestContext": {"http": {"method": "PUT", "path": "/<resource>/123"}},
        "body": '{"name": "updated", "value": 99}'
    }
    response = app.resolve(event, {})
    assert response["statusCode"] == 200

def test_delete_<resource>():
    event = {
        "requestContext": {"http": {"method": "DELETE", "path": "/<resource>/123"}}
    }
    response = app.resolve(event, {})
    assert response["statusCode"] == 200
```

## Usage

When asked to create a new route, provide:
1. **Resource name** (e.g., "user", "product", "order")
2. **HTTP methods needed** (GET, POST, PUT, DELETE, PATCH)
3. **Request/response schemas** (Pydantic models)
4. **Optional prefix** for the router

Example request:
```
Create a route for managing products with GET (list and detail), POST, and DELETE methods.
Include fields: name (str), price (float), category (str), in_stock (bool)
```

## Best Practices

- Use `@tracer.capture_method` on all route handlers
- Log important operations with structured logging (use `extra={}`)
- Validate input with Pydantic models
- Return appropriate HTTP status codes
- Raise Lambda Powertools exceptions (NotFoundError, BadRequestError)
- Write unit tests for each route
- Document each function with docstrings
- Use type hints everywhere

## Common Patterns

### DynamoDB Integration

```python
import os
from boto3 import client

dynamodb = client("dynamodb")
table_name = os.environ.get("TABLE_NAME")

@router.get("/<resource>/<resource_id>")
@tracer.capture_method
def get_<resource>(resource_id: str) -> dict:
    response = dynamodb.get_item(
        TableName=table_name,
        Key={"Pk": {"S": f"<Resource>#{resource_id}"}}
    )
    if "Item" not in response:
        raise NotFoundError(f"<Resource> {resource_id} not found")
    return dynamo_to_python(response["Item"])
```

### Query Parameters with Filters

```python
@router.get("/<resource>")
@tracer.capture_method
def list_<resource>s(
    category: Annotated[str | None, Query()] = None,
    min_price: Annotated[float | None, Query()] = None,
    limit: Annotated[int, Query()] = 10
) -> dict:
    logger.info("Listing <resource>s", extra={
        "category": category,
        "min_price": min_price,
        "limit": limit
    })
    # Filter logic here
    return {"items": [], "total": 0}
```

### Custom Validation

```python
from pydantic import BaseModel, field_validator

class Product(BaseModel):
    name: str
    price: float

    @field_validator('price')
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
```

Now, based on the user's request, generate the appropriate route handler file(s) and update the main handler.
