# Hello API

Simple API project for figuring out things like: AWS CDK, uv, Docker-based lambda functions, FastAPI with Mangum for AWS Lambda, Git Actions and so on.

[![CDK](https://github.com/Valken/python-cdk/actions/workflows/cdk-on-main.yml/badge.svg?branch=main)](https://github.com/Valken/python-cdk/actions/workflows/cdk-on-main.yml)

## Prerequisites

- [AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/prerequisites.html)
- [Docker](https://www.docker.com)
- [uv](https://github.com/astral-sh/uv)

## Bootstrapping

```bash
cdk bootstrap aws://$ACCOUNTID/$REGION
uv sync --frozen --all-packages --dev
```

## Local Development

Run the API locally using uvicorn:

```bash
uv run python run_local.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI (Interactive docs)**: http://localhost:8000/docs
- **ReDoc (Alternative docs)**: http://localhost:8000/redoc

**Note**:
- Lambda Powertools tracing is disabled in local mode (uses mock tracer)
- SSM parameter lookups will return mock values unless you have AWS credentials configured
- DynamoDB operations require valid AWS credentials and TABLE_NAME environment variable

## Deploy

```bash
cdk deploy --all
```

## SAM Local

This should work, but sam doesn't work with docker buildkit, even if you set the environment variable DOCKER_BUILDKIT=1

```bash
pushd cdk
cdk synth --no-staging > template.yaml
sam build -t template.yaml
sam local invoke <funcName> -t template.yaml
popd
```

## Building the Docker image and pushing to ECR

Looking at making this a separate step and telling CDK what image tag to use.

```bash
 aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin $ACCOUNTID.dkr.ecr.eu-west-1.amazonaws.com
```

```bash
docker buildx build \
    --push --platform linux/amd64 \
    --provenance=false \
    -f api/Dockerfile . \
    -t  $ACCOUNTID.dkr.ecr.$REGION.amazonaws.com/hello-api:$(git rev-parse --short HEAD)
```
