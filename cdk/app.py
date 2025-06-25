#!/usr/bin/env python3

from aws_cdk import App

from api_stack import ApiStack
from ecr_stack import EcrStack

# sys.path.append(str(Path(__file__).resolve().parent.parent))

app = App()
stack_name: str = app.node.try_get_context("stackName") or "PythonCdkSamStack"
ApiStack(
    app,
    "PythonCdkSamStack",
    stack_name=stack_name,
    # If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
    # but a single synthesized template can be deployed anywhere.
    # Uncomment the next line to specialize this stack for the AWS Account
    # and Region that are implied by the current CLI configuration.
    # env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
    # Uncomment the next line if you know exactly what Account and Region you
    # want to deploy the stack to. */
    # env=cdk.Environment(account='123456789012', region='us-east-1'),
    # For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html
)

EcrStack(app, "EcrStack", app_name="ecr-repository")

app.synth()
