from aws_lambda_powertools import Logger, Tracer
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

logger = Logger()
tracer = Tracer()


# From https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/programming-with-python.html
def dynamo_to_python(dynamo_object: dict) -> dict:
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in dynamo_object.items()}


def python_to_dynamo(python_object: dict) -> dict:
    serializer = TypeSerializer()
    return {k: serializer.serialize(v) for k, v in python_object.items()}
