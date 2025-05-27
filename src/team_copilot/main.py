"""Team Copilot - Main."""

from os.path import abspath, dirname, join
from contextlib import asynccontextmanager

from starlette.exceptions import HTTPException as StHttpException

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

from team_copilot.core.config import settings
from team_copilot.db.setup import setup
from team_copilot.routers import health, auth, users, documents, chat, ui
from team_copilot.models.data import Error
from team_copilot.models.response import Response, ErrorResponse


# Absolute path to the directory containing this file
BASE_DIR = dirname(abspath(__file__))

# Absolute path to the "static" directory
STATIC_DIR = join(BASE_DIR, "static")

# Descriptions and messages
AUTHENTICATION_ERR = "Authentication error."
AUTHORIZATION_ERR = "Authorization error."
ERROR = "Error."
GET_WEL_MSG_DESC = "Get a welcome message."
GET_WEL_MSG_SUM = "Get a welcome message"
INT_SER_ERR_1 = "Internal server error"
INT_SER_ERR_2 = "Internal server error."
VAL_ERR = "Validation error."
WELCOME = f"Welcome to {settings.app_name}!"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan.

    Args:
        app (FastAPI): FastAPI application
    """
    # Set up the database on startup
    setup(settings.db_url)
    yield
    # Any logic to run on shutdown would go here


# Application object
app = FastAPI(
    debug=settings.debug,
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": INT_SER_ERR_1,
            "model": ErrorResponse,
        },
    },
)

# Routers
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(ui.router, prefix="/ui", tags=["ui"], include_in_schema=False)

# Static files
app.mount("/ui/static", StaticFiles(directory=STATIC_DIR), name="static")


def openapi() -> dict:
    """Get OpenAPI schema.

    This is a reimplementation of the `FastAPI.openapi` method of the `app` object to
    rename some schemas that have generic names (see the
    `team_copilot.routers.documents` module).

    The first time this function is called, it will generate the OpenAPI schema and
    store it in the `app.openapi_schema` attribute. On subsequent calls, it will just
    return the stored schema.

    Returns:
        dict: OpenAPI schema.
    """

    def rename_schema(schemas: dict, old_name: str, new_name: str):
        # Copy the old schema with the new name
        schemas[new_name] = schemas[old_name]
        schemas[new_name]["title"] = new_name

        # Remove the old schema
        del schemas[old_name]

    def update_refs(openapi_schema: dict, old_name: str, new_name: str):
        base_ref = "#/components/schemas/"

        for path in openapi_schema["paths"].values():
            for method in path.values():
                if (req_body := method.get("requestBody")) and (
                    content := req_body.get("content")
                ):
                    for content_type in content.values():
                        if (
                            (schema := content_type.get("schema"))
                            and (ref := schema.get("$ref"))
                            and (ref == f"{base_ref}{old_name}")
                        ):
                            # Update the reference to the new schema
                            schema["$ref"] = f"{base_ref}{new_name}"

    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    if (components := openapi_schema.get("components")) and (
        schemas := components.get("schemas")
    ):
        # Get all the schemas to rename
        schema_names = auth.SCHEMA_NAMES | documents.SCHEMA_NAMES

        for old_name, new_name in schema_names.items():
            if old_name in schemas:
                # Rename the schema
                rename_schema(schemas, old_name, new_name)

                # Update all the references to the old schema
                update_refs(openapi_schema, old_name, new_name)

        # Sort the schemas by name
        components["schemas"] = dict(sorted(schemas.items()))

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Override the "openapi" method of the application object
app.openapi = openapi


@app.exception_handler(StHttpException)
@app.exception_handler(HTTPException)
async def handle_http_error(
    request: Request,
    exc: StHttpException | HTTPException,
) -> JSONResponse:
    """Handle low-level Starlette HTTPException exceptions and FastAPI HTTPException
    exceptions.

    Args:
        request (Request): Request.
        exc (StHttpException | HTTPException): Exception.

    Returns:
        JSONResponse: Error message.
    """
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        id = "authentication"
        message = AUTHENTICATION_ERR
    elif exc.status_code == status.HTTP_403_FORBIDDEN:
        id = "authorization"
        message = AUTHORIZATION_ERR
    else:
        id = "error"
        message = ERROR

    errors = [Error(id=id, message=exc.detail)]
    res = ErrorResponse.create(message=message, errors=errors)

    return JSONResponse(status_code=exc.status_code, content=res.model_dump())


@app.exception_handler(RequestValidationError)
async def handle_reqval_error(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Handle RequestValidationError exceptions.

    Args:
        request (Request): Request.
        exc (RequestValidationError): Exception.

    Returns:
        JSONResponse: Error message.
    """

    def get_error(e: dict) -> Error:
        if len(e["loc"]) > 1 and isinstance(e["loc"][1], str):
            return Error(id=e["loc"][1], message=e["msg"])
        else:
            return Error(id=e["loc"][0], message=e["msg"])

    errors = list(map(get_error, exc.errors()))
    res = ErrorResponse.create(message=VAL_ERR, errors=errors)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=res.model_dump(),
    )


@app.exception_handler(Exception)
async def handle_error(request: Request, exc: Exception) -> JSONResponse:
    """Handle Exception exceptions.

    Args:
        request (Request): Request.
        exc (Exception): Exception.

    Returns:
        JSONResponse: Error message.
    """
    errors = [Error(id="internal_server_error", message=INT_SER_ERR_2)]
    res = ErrorResponse.create(message=INT_SER_ERR_2, errors=errors)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=res.model_dump(),
    )


@app.get(
    "/api",
    operation_id="get_welcome_message",
    summary=GET_WEL_MSG_SUM,
    description=GET_WEL_MSG_DESC,
    response_model=Response,
)
def get_welcome_message() -> Response:
    """Get a welcome message.

    Returns:
        Response: Welcome message.
    """
    return Response(message=WELCOME)
