"""Team Copilot - Routers - User Interface."""

from os.path import abspath, dirname, join

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


# Absolute path to the application directory
BASE_DIR = dirname(dirname(abspath(__file__)))

# Absolute path to the "templates" directory
TEMPLATES_DIR = join(BASE_DIR, "templates")

# Descriptions and messages
HOME_DESC = "Home page of the user interface."
HOME_SUM = "Home page of the user interface"

# Templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Router
router = APIRouter()


@router.get(
    "/",
    operation_id="home",
    summary=HOME_SUM,
    description=HOME_DESC,
    response_class=HTMLResponse,
)
async def home(request: Request) -> HTMLResponse:
    """Get the Home page of the User Interface.

    Returns:
        HTMLResponse: Page HTML content.
    """
    context = {"request": request}
    return templates.TemplateResponse("home.html", context)
