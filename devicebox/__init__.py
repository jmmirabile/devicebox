import argparse
from .store import get_device, add, get, list_all, update, delete

__all__ = ["add_device_argument", "get_device", "add", "get", "list_all", "update", "delete"]


def add_device_argument(parser: argparse.ArgumentParser) -> None:
    """Inject --device into an existing ArgumentParser."""
    parser.add_argument( "-d",
        "--device",
        required=True,
        metavar="ALIAS",
        help="Device alias (looked up in the device registry)",
    )
