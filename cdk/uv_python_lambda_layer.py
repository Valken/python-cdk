from pathlib import Path
from aws_cdk import aws_lambda as _lambda, DockerImage
from constructs import Construct


class UVPythonLambdaLayer(Construct):
    def __init__(
        self, scope: Construct, id: str, root_path: Path, python_version: str = "3.13"
    ) -> None:
        super().__init__(scope, id)

        # Create the Docker image
        self.docker_image = DockerImage.from_build(
            str(root_path / "cdk" / "resources"),
            build_args={"PYTHON_VERSION": python_version, "PLATFORM": "linux/amd64"},
        )

        # Create the Lambda Layer
        self.layer = _lambda.LayerVersion(
            self,
            "UVPythonLambdaLayer",
            code=_lambda.Code.from_asset(
                str(root_path / "layer"),
                bundling={
                    "image": self.docker_image,
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
