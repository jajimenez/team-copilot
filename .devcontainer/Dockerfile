FROM mcr.microsoft.com/devcontainers/python:1-3.12-bullseye

# Create a directory as the workspace inside the user's home directory.
# Install Poetry.
# Configure Poetry to create the Python virtual environment in the project directory.
RUN mkdir -p /home/vscode/team-copilot && \
    pip install --root-user-action ignore --upgrade pip && \
    pip install --root-user-action ignore poetry
