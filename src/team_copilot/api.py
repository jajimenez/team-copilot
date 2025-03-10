"""Team Copilot - API."""

from fastapi import FastAPI
import uvicorn

from team_copilot import __version__ as version


app = FastAPI(title="Team Copilot", version=version)


@app.get("/")
def index():
    return {"message": "Welcome to Team Copilot!"}


def run(host: str = "127.0.0.1", port: int = 8000):
    """Run the API.
    
    :param host: Host (default: 127.0.0.1).
    :type host: str
    :param port: Port (default: 8000).
    :type port: int
    """
    # Run the API
    uvicorn.run(app, host=host, port=port)
