"""Team Copilot - Main."""

from argparse import ArgumentParser, Namespace

from team_copilot.api import run


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000

PROG_USAGE = "python -m team_copilot"
PROG_DESC = "Run the Team Copilot API."
HOST_HELP = f"Host (default: {DEFAULT_HOST})."
PORT_HELP = f"Port (default: {DEFAULT_PORT})."


def get_args() -> Namespace:
    """Get command line arguments.

    :return: Command line arguments ("--host" and "--port").
    :rtype: Namespace
    """
    parser = ArgumentParser(PROG_USAGE, description=PROG_DESC)

    parser.add_argument(
        "--host",
        type=str,
        default=DEFAULT_HOST,
        help=HOST_HELP,
    )

    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=PORT_HELP,
    )

    return parser.parse_args()


def main():
    # Get command line arguments
    args = get_args()

    host = args.host
    port = args.port

    # Run the API
    run(host, port)


if __name__ == "__main__":
    main()
