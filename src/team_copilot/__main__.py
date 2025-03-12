"""Team Copilot - Main."""

from argparse import ArgumentParser, Namespace

from team_copilot.api import run


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000

PROG_USAGE = "python -m team_copilot"
PROG_DESC = "Run the Team Copilot API."
OP_TITLE = "operation"
OP_DESC = "Operation to perform."
RUN_DESC = "Run the API."
HOST_DESC = f"Host (default: {DEFAULT_HOST})."
PORT_DESC = f"Port (default: {DEFAULT_PORT})."
SETUP_DB_DESC = "Set up the database."


def get_args() -> Namespace:
    """Get command line arguments.

    Returns:
        :return (Namespace): Command line arguments.
    """
    parser = ArgumentParser(PROG_USAGE, description=PROG_DESC)

    # Operation subparsers
    subparsers = parser.add_subparsers(
        dest=OP_TITLE,
        help=OP_DESC,
        required=True,
    )

    # "Run" operation
    run_parser = subparsers.add_parser("run", help=RUN_DESC)

    # Host
    run_parser.add_argument(
        "--host",
        type=str,
        default=DEFAULT_HOST,
        help=HOST_DESC,
    )

    # Port
    run_parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=PORT_DESC,
    )

    # "Set Up Database" operation
    subparsers.add_parser("setup-db", help=SETUP_DB_DESC)

    return parser.parse_args()


def main():
    """Run the API."""

    # Get command line arguments
    args = get_args()

    if args.operation == "run":
        # Run the API
        host = args.host
        port = args.port

        run(host, port)
    elif args.operation == "setup-db":
        # Set up the database
        # TODO: Set up the database
        pass


if __name__ == "__main__":
    main()
