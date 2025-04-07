from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_lambda_python_alpha as python_lambda,
    aws_apigatewayv2 as apigateway,
    aws_apigatewayv2_integrations as integrations,
    aws_ssm as ssm,
    CfnOutput as Cfnoutput,
)
from constructs import Construct


class ApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        hello_world_function = python_lambda.PythonFunction(
            self,
            "HelloWorldFunction",
            entry="api",
            index="handler.py",
            runtime=_lambda.Runtime.PYTHON_3_13,
            handler="lambda_handler",
        )

        provisioned_concurrency = 0
        hello_world_function_alias = (
            None
            if provisioned_concurrency <= 0
            else hello_world_function.current_version.add_alias(
                "live",
                provisioned_concurrent_executions=2,
            )
        )

        api = apigateway.HttpApi(self, "Endpoint")

        lambda_integration = integrations.HttpLambdaIntegration(
            "LambdaIntegration",
            handler=hello_world_function_alias
            if hello_world_function_alias
            else hello_world_function,
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

        Cfnoutput(self, "Url", value=api.url)
