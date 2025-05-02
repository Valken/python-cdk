from pathlib import Path

from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigatewayv2 as apigateway,
    aws_apigatewayv2_integrations as integrations,
    aws_ssm as ssm,
    aws_iam as iam,
    CfnOutput as Cfnoutput,
    Duration,
    ILocalBundling,
    BundlingOptions,
    DockerImage,
)
from constructs import Construct
from uv_python_lambda import PythonFunction
from jsii import implements, member
import subprocess

root_path = Path(__file__).parent.parent


@implements(ILocalBundling)
class MyLocalBundler:
    @member(jsii_name="tryBundle")
    def try_bundle(self, output_dir: str, options: BundlingOptions) -> bool:
        try:
            # Run local commands to bundle the layer
            subprocess.run(
                [
                    "bash",
                    "-c",
                    "cd ../layer && "
                    "uv export --frozen --no-dev --no-editable -o requirements.txt && "
                    "uv pip install --no-installer-metadata --no-compile-bytecode --prefix packages -r requirements.txt && ",
                    f"mkdir {output_dir}/python && cp -r packages/lib {output_dir}/python/",
                ],
                check=True,
            )
            return True
        except subprocess.CalledProcessError:
            return False


class ApiStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        docker_image = DockerImage.from_build(
            str(root_path / "cdk" / "resources"),
            # build_args={
            #     "PYTHON_VERSION": "3.13",
            #     "LAMBDA_RUNTIME": _lambda.Runtime.PYTHON_3_13.name,
            # },
        )

        layer = _lambda.LayerVersion(
            self,
            "LambdaLayer",
            code=_lambda.Code.from_asset(
                str(root_path / "layer"),
                exclude=[".venv", ".git", ".idea", "node_modules"],
                bundling={
                    "image": docker_image,
                    "command": [
                        "bash",
                        "-c",
                        "rsync -rLv /asset-input/ /asset-output && "
                        "cd /asset-output && "
                        "uv sync --python-preference=only-system --link-mode=copy && "
                        "uv export --frozen --no-dev --no-editable -o requirements.txt && "
                        "uv pip install --reinstall --no-compile-bytecode --prefix packages --link-mode=copy -r requirements.txt && "
                        "cp -r packages/lib/*/site-packages /asset-output/python/ && "
                        "rm -rf packages .venv && "
                        "mv *.{py,toml,txt,lock} /asset-output/python/",
                    ],
                },
            ),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_13],
        )

        # hello_world_function = (
        #     PythonFunction(
        #         self,
        #         "HelloWorldFunction",
        #         entry="../api",
        #         index="handler.py",
        #         runtime=_lambda.Runtime.PYTHON_3_13,
        #         handler="lambda_handler",
        #     )
        # )

        hello_world_function = PythonFunction(
            self,
            "HelloWorldFunction",
            index="api/handler.py",
            root_dir=str(root_path),
            workspace_package="api",  # Use a workspace package as the top-level Lambda entry point.
            handler="lambda_handler",
            runtime=_lambda.Runtime.PYTHON_3_13,
            architecture=_lambda.Architecture.X86_64,
            layers=[layer],
            bundling={
                "asset_excludes": [
                    ".venv/",
                    "node_modules/",
                    "cdk/",
                    ".git/",
                    ".idea/",
                    "dist/",
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
        ssm.StringParameter(
            self,
            "SomthingElse",
            parameter_name="/hello-world/something",
            string_value="something",
        )

        Cfnoutput(self, "Url", value=api.url)

    def _build_bundle_commands(self):
        commands = [
            "pip install uv",
            "uv export --frozen --no-dev --no-editable -o requirements.txt",
            "pip install -r requirements.txt -t /asset-output/python",
            "cp -au . /asset-output/python",
        ]
        return " && ".join(commands)
