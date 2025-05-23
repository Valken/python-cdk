from pathlib import Path

import boto3
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigatewayv2 as apigateway,
    aws_apigatewayv2_integrations as integrations,
    aws_ssm as ssm,
    aws_iam as iam,
    CfnOutput as Cfnoutput,
    Duration,
    aws_dynamodb as dynamodb,
)
from constructs import Construct
from uv_python_lambda import PythonFunction

from uv_python_lambda_layer import UVPythonLambdaLayer

root_path = Path(__file__).parent.parent


class ApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        uv_layer = UVPythonLambdaLayer(
            self,
            "UVPythonLambdaLayerConstruct",
            root_path=root_path,
        )

        ssm_client = boto3.client("ssm", region_name="eu-west-1")
        response = ssm_client.get_parameter(
            Name="/somethingsomething/api/blog-api-dev/blogtable",
            WithDecryption=True,  # Set to True if the parameter is encrypted
        )
        table_name = response["Parameter"]["Value"]

        hello_world_function = PythonFunction(
            self,
            "HelloWorldFunction",
            index="api/handler.py",
            root_dir=str(root_path),
            workspace_package="api",  # Use a workspace package as the top-level Lambda entry point.
            handler="lambda_handler",
            runtime=_lambda.Runtime.PYTHON_3_13,
            architecture=_lambda.Architecture.X86_64,
            layers=[uv_layer.layer],
            environment={
                # "PYTHONPATH": "/var/runtime:/var/task:var/task/api:/opt/python"
                "TABLE_NAME": table_name,
            },
            bundling={
                "asset_excludes": [
                    ".venv/",
                    "node_modules/",
                    "cdk/",
                    ".git/",
                    ".idea/",
                    "dist/",
                    "layer/",
                    "tests/",
                    "*.yaml",
                    "*.bat",
                    ".python-version",
                    ".gitignore",
                    "*.md",
                ]
            },
            timeout=Duration.seconds(30),
        )
        hello_world_function.role.add_to_policy(
            iam.PolicyStatement(
                actions=["ssm:GetParameter", "ssm:GetParametersByPath"],
                resources=[
                    f"arn:aws:ssm:{self.region}:{self.account}:parameter/hello-world*"
                ],
            )
        )
        table = dynamodb.Table.from_table_name(
            self,
            "Table",
            table_name=table_name,
        )
        table.grant_read_data(hello_world_function)

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
            handler=(
                hello_world_function_alias
                if hello_world_function_alias
                else hello_world_function
            ),
        )

        api.add_routes(
            path="/{proxy+}",
            methods=[apigateway.HttpMethod.ANY],
            integration=lambda_integration,
        )

        api.add_routes(
            path="/hello",
            methods=[apigateway.HttpMethod.GET],
            integration=lambda_integration,
        )

        ssm.StringParameter(
            self,
            "HelloWorldApiUrl",
            parameter_name="/hello-world/url",
            string_value=api.url,
        )
        ssm.StringParameter(
            self,
            "SomthingElse",
            parameter_name="/hello-world/something",
            string_value="something",
        )

        Cfnoutput(self, "Url", value=api.url)
