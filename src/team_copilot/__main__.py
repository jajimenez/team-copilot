"""Team Copilot - Main."""

from argparse import ArgumentParser, Namespace

from uvicorn import run

from team_copilot import app


HOST_DEFAULT = "127.0.0.1"
PORT_DEFAULT = 8000

PROG_USAGE = "python -m team_copilot"
PROG_DESC = "Run the Team Copilot API."
HOST_HELP = f"Host (default: {HOST_DEFAULT})."
PORT_HELP = f"Port (default: {PORT_DEFAULT})."


def get_args() -> Namespace:
    """Get command line arguments.

    :return: Command line arguments ("--host" and "--port").
    :rtype: Namespace
    """
    parser = ArgumentParser(PROG_USAGE, description=PROG_DESC)

    parser.add_argument(
        "--host",
        type=str,
        default=HOST_DEFAULT,
        help=HOST_HELP,
    )

    parser.add_argument(
        "--port",
        type=int,
        default=PORT_DEFAULT,
        help=PORT_HELP,
    )

    return parser.parse_args()


def main():
    """Run the API."""
    # Get command line arguments
    args = get_args()

    host = args.host
    port = args.port

    # Run the API
    run(app, host=host, port=port)


if __name__ == "__main__":
    main()
