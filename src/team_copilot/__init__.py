"""Team Copilot."""

from fastapi import FastAPI


__version__ = "0.1.0"

app = FastAPI(title="Team Copilot", version=__version__)


@app.get("/")
def index():
    return {"message": "Welcome to Team Copilot!"}
