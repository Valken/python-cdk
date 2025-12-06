import os

from aws_lambda_powertools import Logger
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

logger = Logger()

# Only enable tracer in actual Lambda environment (check for Lambda-specific env var)
# Not just AWS_EXECUTION_ENV which we might set locally
if os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
    from aws_lambda_powertools import Tracer

    tracer = Tracer()
else:
    # In local development, use a mock tracer that does nothing
    class MockTracer:
        """Mock tracer for local development."""

        def capture_lambda_handler(self, func):
            return func

        def capture_method(self, func):
            return func

        def put_annotation(self, key, value):
            pass

        def put_metadata(self, key, value):
            pass

    tracer = MockTracer()


# From https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/programming-with-python.html
def dynamo_to_python(dynamo_object: dict) -> dict:
    """Convert DynamoDB JSON format to Python dict."""
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in dynamo_object.items()}


def python_to_dynamo(python_object: dict) -> dict:
    """Convert Python dict to DynamoDB JSON format."""
    serializer = TypeSerializer()
    return {k: serializer.serialize(v) for k, v in python_object.items()}
