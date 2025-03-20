"""Team Copilot - Main."""

from argparse import ArgumentParser, Namespace

from team_copilot.app import run
from team_copilot.core.db import setup_db
from team_copilot.config import settings


PROG_USAGE = "python -m team_copilot"
PROG_DESC = "Run the Team Copilot application."
OP_TITLE = "operation"
OP_DESC = "Operation to perform."
RUN_DESC = "Run the application."
SETUP_DB_DESC = "Set up the database."


def get_args() -> Namespace:
    """Get command line arguments.

    Returns:
        Namespace: Command line arguments.
    """
    parser = ArgumentParser(PROG_USAGE, description=PROG_DESC)

    # Operation subparsers
    subparsers = parser.add_subparsers(
        dest=OP_TITLE,
        help=OP_DESC,
        required=True,
    )

    # "Run" operation
    subparsers.add_parser("run", help=RUN_DESC)

    # "Set Up Database" operation
    subparsers.add_parser("setup-db", help=SETUP_DB_DESC)

    return parser.parse_args()


def main():
    """Application main function."""
    # Get command line arguments
    args = get_args()

    if args.operation == "run":
        # Run the API
        run(settings.app_host, settings.app_port)
    elif args.operation == "setup-db":
        # Set up the database
        setup_db(settings.db_url)


if __name__ == "__main__":
    main()
