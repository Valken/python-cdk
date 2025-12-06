# AWS CDK Python Best Practices

Apply these best practices when working with AWS CDK in Python for serverless infrastructure.

## Project Structure

- Use Python 3.11+ syntax and type hints
- Follow PEP8 style guidelines
- Organize CDK code in `cdk/` directory
- Separate application code from infrastructure

## Stack Organization

- Inherit from `Stack` for each logical grouping
- Use meaningful construct IDs
- Pass `**kwargs` to parent Stack constructor
- Use `CfnParameter` for runtime configuration
- Import existing resources with `.from_*` methods

## Lambda Functions

### Docker-based Deployments

```python
from aws_cdk import aws_lambda as _lambda
from aws_cdk.aws_ecr_assets import Platform
from aws_cdk.aws_lambda import Tracing

function = _lambda.Function(
    self,
    "ApiFunction",
    code=_lambda.Code.from_asset_image(
        str(root_path),
        file="api/Dockerfile",
        platform=Platform.LINUX_AMD64,
    ),
    handler=_lambda.Handler.FROM_IMAGE,
    runtime=_lambda.Runtime.FROM_IMAGE,
    environment={
        "POWERTOOLS_SERVICE_NAME": "my-api",
        "ENVIRONMENT": environment,
    },
    timeout=Duration.seconds(30),
    tracing=Tracing.ACTIVE,
    logging_format=_lambda.LoggingFormat.JSON,
    memory_size=256,
)
```

### Configuration Best Practices

- Always enable X-Ray tracing: `tracing=Tracing.ACTIVE`
- Use JSON logging: `logging_format=_lambda.LoggingFormat.JSON`
- Set explicit timeouts: `timeout=Duration.seconds(30)`
- Right-size memory: Start at 256MB, tune based on metrics
- Use environment variables for configuration
- Consider provisioned concurrency for production

## IAM & Security

### Least Privilege Permissions

```python
from aws_cdk import aws_iam as iam

# Grant specific permissions
function.role.add_to_policy(
    iam.PolicyStatement(
        actions=["ssm:GetParameter", "ssm:GetParametersByPath"],
        resources=[
            f"arn:aws:ssm:{self.region}:{self.account}:parameter/my-app/*"
        ],
    )
)

# Use grant methods when available
table.grant_read_data(function)
```

### DynamoDB Permissions

```python
# Grant read access to table
table.grant_read_data(function)

# Grant access to specific indexes
function.add_to_role_policy(
    iam.PolicyStatement(
        effect=iam.Effect.ALLOW,
        actions=["dynamodb:Query"],
        resources=[
            f"{table.table_arn}/index/TopicIndex",
            f"{table.table_arn}/index/DateIndex",
        ],
    )
)
```

## API Gateway (HTTP API)

```python
from aws_cdk import aws_apigatewayv2 as apigateway
from aws_cdk import aws_apigatewayv2_integrations as integrations

http_api = apigateway.HttpApi(
    self,
    "HttpApi",
    default_integration=integrations.HttpLambdaIntegration(
        "DefaultIntegration",
        function,
    ),
    cors_preflight=apigateway.CorsPreflightOptions(
        allow_origins=["*"],
        allow_methods=[apigateway.CorsHttpMethod.ANY],
        allow_headers=["*"],
    ),
)
```

## SSM Parameter Store

```python
from aws_cdk import aws_ssm as ssm

# Import existing parameter
table_name = ssm.StringParameter.value_for_string_parameter(
    self, "/my-app/dynamodb/table-name"
)

# Create new parameter
ssm.StringParameter(
    self,
    "ApiEndpoint",
    parameter_name="/my-app/api/endpoint",
    string_value=http_api.url,
)
```

## DynamoDB

```python
from aws_cdk import aws_dynamodb as dynamodb

# Import existing table
table = dynamodb.Table.from_table_name(
    self,
    "Table",
    table_name=table_name,
)

# Create new table
table = dynamodb.Table(
    self,
    "Table",
    partition_key=dynamodb.Attribute(
        name="Pk",
        type=dynamodb.AttributeType.STRING,
    ),
    sort_key=dynamodb.Attribute(
        name="Sk",
        type=dynamodb.AttributeType.STRING,
    ),
    billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
)
```

## Environment Management

```python
from aws_cdk import CfnParameter

environment = CfnParameter(
    self,
    "Environment",
    type="String",
    description="Deployment environment",
    default="dev",
    allowed_values=["dev", "staging", "prod"],
)

# Use in resources
function.add_environment("ENVIRONMENT", environment.value_as_string)
```

## Typing and Imports

```python
from pathlib import Path
from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_apigatewayv2 as apigateway,
)
from constructs import Construct

# Use Path for file paths
root_path = Path(__file__).parent.parent
```

## Common Patterns

### Lambda Alias with Provisioned Concurrency

```python
# Only create alias if provisioned concurrency > 0
provisioned_concurrency = 2
function_alias = (
    None
    if provisioned_concurrency <= 0
    else function.current_version.add_alias(
        "live",
        provisioned_concurrent_executions=provisioned_concurrency,
    )
)
```

### Resource Naming

```python
# Use construct_id for logical naming
function = _lambda.Function(
    self,
    "ApiFunction",  # CloudFormation logical ID
    function_name=f"my-app-{environment}-api",  # AWS resource name
    ...
)
```

## Observability

- Enable X-Ray tracing on all Lambdas
- Use JSON logging format
- Configure CloudWatch log retention
- Add custom metrics and alarms
- Tag resources for cost tracking

## Cost Optimization

- Start with 256MB Lambda memory, tune based on metrics
- Use provisioned concurrency sparingly (high cost)
- Use on-demand billing for DynamoDB unless predictable load
- Implement appropriate timeouts to avoid long-running costs
- Use reserved capacity only for stable workloads

## Deployment

```python
# CDK app entry point (app.py)
from aws_cdk import App
from api_stack import ApiStack

app = App()
ApiStack(app, "MyApiStack")
app.synth()
```

## Testing

- Write unit tests for stack synthesis
- Use snapshot tests to detect changes
- Validate IAM policies and permissions
- Test Lambda functions independently
