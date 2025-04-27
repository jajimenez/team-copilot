"""Team Copilot - Main."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.openapi.utils import get_openapi

from team_copilot.db.setup import setup
from team_copilot.routers import health, auth, users, documents, chat

from team_copilot.models.response import MessageResponse
from team_copilot.core.config import settings


# Descriptions and messages
INTERNAL_SERVER_ERROR = "Internal server error"
APP_WELCOME = f"Welcome to {settings.app_name}!"
APP_OK = "The application is running."
APP_ISE = "Internal server error."
APP_INV_CRED = "Invalid credentials"
DB_OK = "The database is available."
DB_ERROR_MESSAGE = "The database is not available."
GET_WEL_MSG_SUM = "Get a welcome message"
GET_WEL_MSG_DESC = f"{GET_WEL_MSG_SUM}."


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
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": INTERNAL_SERVER_ERROR,
            "model": MessageResponse,
        },
    },
)

# Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(documents.router)
app.include_router(chat.router)


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
    msg = [i["msg"] for i in exc.errors()]
    msg = ", ".join(msg)

    msg_res = MessageResponse(message=msg)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=msg_res.model_dump(),
    )


@app.exception_handler(HTTPException)
async def handle_http_error(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTPException exceptions.

    Args:
        request (Request): Request.
        exc (HTTPException): Exception.

    Returns:
        JSONResponse: Error message.
    """
    msg_res = MessageResponse(message=exc.detail)
    return JSONResponse(status_code=exc.status_code, content=msg_res.model_dump())


@app.exception_handler(Exception)
async def handle_error(request: Request, exc: Exception) -> JSONResponse:
    """Handle Exception exceptions.

    Args:
        request (Request): Request.
        exc (Exception): Exception.

    Returns:
        JSONResponse: Error message.
    """
    msg_res = MessageResponse(message=APP_ISE)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=msg_res.model_dump(),
    )


@app.get(
    "/",
    operation_id="get_welcome_message",
    summary=GET_WEL_MSG_SUM,
    description=GET_WEL_MSG_DESC,
    response_model=MessageResponse,
)
def get_welcome_message() -> MessageResponse:
    """Get a welcome message.

    Returns:
        MessageResponse: Welcome message.
    """
    return MessageResponse(message=APP_WELCOME)
