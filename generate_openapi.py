from aws_lambda_powertools.event_handler import APIGatewayHttpResolver

from api.post_routes import router as post_router
from api.thing_routes import router as thing_router


def main():
    app = APIGatewayHttpResolver(enable_validation=True)
    app.include_router(thing_router)
    app.include_router(post_router)

    openapi_schema = app.get_openapi_json_schema()

    with open("openapi.json", "w") as f:
        f.write(openapi_schema)


if __name__ == "__main__":
    main()

# ⬇️ Trying out dynamic import of all `_routes.py` files in a directory with Copilot's help! ⬇️
#
# import glob
# import importlib
# import os
# from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
#
# def import_and_include_routes(directory: str):
#     app = APIGatewayHttpResolver(enable_validation=True)
#
#     # Find all `_routes.py` files in the directory and subdirectories
#     route_files = glob.glob(os.path.join(directory, "**/*_routes.py"), recursive=True)
#
#     for route_file in route_files:
#         # Skip files or directories containing "test"
#         if "test" in route_file:
#             continue
#
#         # Extract the module name (e.g., `api.subdir.post_routes` from `api/subdir/post_routes.py`)
#         module_name = os.path.splitext(os.path.relpath(route_file, directory))[0].replace(os.sep, ".")
#
#         # Dynamically import the module
#         module = importlib.import_module(module_name)
#
#         # Include the router from the module
#         if hasattr(module, "router"):
#             app.include_router(module.router)
#
#     # Generate OpenAPI schema for all routes
#     openapi_schema = app.get_openapi_json_schema(
#         title="My Lambda Powertools App",
#         version="1.0.0",
#         description="OpenAPI schema for all routes",
#     )
#
#     # Write the schema to a file
#     with open("openapi2.json", "w") as f:
#         f.write(openapi_schema)
#
# if __name__ == "__main__":
#     import_and_include_routes("api")
