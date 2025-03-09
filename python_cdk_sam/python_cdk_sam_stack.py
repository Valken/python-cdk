from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigatewayv2 as apigateway,
    aws_apigatewayv2_integrations as integrations,
    aws_ssm as ssm
)
from constructs import Construct

class PythonCdkSamStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)



        hello_world_function = _lambda.Function(
            self,
            "HelloWorldFunction",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("api"),  # Points to the lambda directory
            handler="handler.lambda_handler",
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

