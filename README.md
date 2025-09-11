# Hello API

Simple API project for figuring out things like: AWS CDK, uv, Docker-based lambda functions, Lambda Powertools for Python, Git Actions and so on.

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
