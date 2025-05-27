# Stage 1 (build stage): Environment used to install build tools and compile dependencies.
FROM python:3.12-slim AS builder

# - Install build dependencies:
#     - curl: To download the Poetry installer.
#     - build-essential: To compile Python packages that require C extensions (Psycopg2,
#                        in this case).
#     - python3-dev: To provide the Python headers needed for compiling C extensions.
#     - libpq-dev: PostgreSQL client library headers needed for compiling packages that
#                  interact with PostgreSQL (Pyscopg2, in this case).
# - Remove the APT cache to reduce the image size.
RUN apt-get update && \
    apt-get install -y curl build-essential python3-dev libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Add the directory where Poetry will be installed to the Path, so that the "poetry"
# command can be found.
ENV PATH="/root/.local/bin:$PATH"

# - Install Poetry using its official installer.
# - Configure Poetry to not create virtual environments.
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry config virtualenvs.create false

# Install application dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-cache --no-interaction

# Stage 2 (production stage): Environment where we copy only the compiled dependencies,
# excluding the build tools.
FROM python:3.12-slim

# - Prevent Python from writing ".pyc" files to disk, which can save space.
# - Ensure that Python output is sent straight to the terminal without being buffered,
#   which is useful for logging.
# - Defining the application directory.
# - Defining the temporary directory where the PDF documents will be uploaded.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TEAM_COPILOT_APP_DIR=/app \
    TEAM_COPILOT_APP_TEMP_DIR=/tmp/team-copilot

# - Install runtime dependencies:
#     - libpq5: PostgreSQL client library needed for Psycopg2 to connect to PostgreSQL
#               databases.
#     - tesseract-ocr-all: Tesseract OCR engine and all its language data files.
# - Remove the APT cache to reduce the image size.
RUN apt-get update && \
    apt-get install -y libpq5 tesseract-ocr-all && \
    rm -rf /var/lib/apt/lists/*

# - Create an "app" user to run the application, instead of running it as the root user.
# - Create the application and temporary directories.
RUN groupadd -r app && useradd -r -g app app && \
    mkdir -p $TEAM_COPILOT_APP_DIR && \
    mkdir -p $TEAM_COPILOT_APP_TEMP_DIR

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Set the working directory to the application directory
WORKDIR $TEAM_COPILOT_APP_DIR

# Copy application files
COPY src/ $TEAM_COPILOT_APP_DIR/

# Set the ownership of the application and temporary directories to the "app" user
RUN chown -R app:app $TEAM_COPILOT_APP_DIR $TEAM_COPILOT_APP_TEMP_DIR

# Switch to the "app" user
USER app

# Expose port
EXPOSE 8000

# Run the application
CMD uvicorn team_copilot.main:app --host ${TEAM_COPILOT_APP_HOST:-0.0.0.0} --port ${TEAM_COPILOT_APP_PORT:-8000}
