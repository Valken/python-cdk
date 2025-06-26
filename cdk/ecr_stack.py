from aws_cdk import Stack, aws_ecr as ecr, CfnOutput
from constructs import Construct


class EcrStack(Stack):
    def __init__(self, scope: Construct, id: str, app_name: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        ecr_repository = ecr.Repository(
            self, "AppEcrRepository", repository_name=f"{app_name}"
        )

        CfnOutput(self, "EcrRepositoryUri", value=ecr_repository.repository_uri)
