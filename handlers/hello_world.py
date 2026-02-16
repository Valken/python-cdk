import json


def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Hello World!", "event": event}),
    }
