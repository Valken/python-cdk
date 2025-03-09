from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_lambda_python_alpha as python_lambda,
    aws_apigatewayv2 as apigateway,
    aws_apigatewayv2_integrations as integrations,
    aws_ssm as ssm
)
from constructs import Construct

class PythonCdkSamStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        hello_world_function = python_lambda.PythonFunction(
            self,
            "HelloWorldFunction",
            entry="api",
            runtime=_lambda.Runtime.PYTHON_3_9,
            index="handler.py",
            handler="lambda_handler"
            )

        api = apigateway.HttpApi(
            self,
            "Endpoint"
        )

        lambda_integration = integrations.HttpLambdaIntegration(
            "LambdaIntegration",
            handler=hello_world_function,
        )

        api.add_routes(
            path="/{proxy+}",
            methods=[apigateway.HttpMethod.ANY],
            integration=lambda_integration,
        )

        ssm.StringParameter(
            self,
            "HelloWorldApiUrl",
            parameter_name="/hello-world/url",
            string_value=api.url,
        )

