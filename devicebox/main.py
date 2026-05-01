import argparse
import sys

try:
    from . import store
except ImportError:
    import store  # type: ignore[no-redef]


def cmd_add(args: argparse.Namespace) -> None:
    try:
        store.add(args.shortname, args.address)
        print(f"Added: {args.shortname} -> {args.address}")
    except KeyError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_get(args: argparse.Namespace) -> None:
    try:
        print(store.get_device(args.shortname))
    except KeyError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_list(args: argparse.Namespace) -> None:
    devices = store.list_all()
    if not devices:
        print("No devices registered.")
        return
    width = max(len(alias) for alias in devices)
    for alias, info in sorted(devices.items()):
        hostname = info.get("hostname", "")
        print(f"{alias:<{width}}  {hostname}")


def cmd_update(args: argparse.Namespace) -> None:
    try:
        store.update(args.shortname, args.address)
        print(f"Updated: {args.shortname} -> {args.address}")
    except KeyError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def cmd_delete(args: argparse.Namespace) -> None:
    try:
        store.delete(args.shortname)
        print(f"Deleted: {args.shortname}")
    except KeyError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="devicebox",
        description="Manage device alias-to-hostname mappings.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="command")

    p_add = subparsers.add_parser("add", help="Register a new device alias")
    p_add.add_argument("-s", "--shortname", help="Short alias for the device", required=True)
    p_add.add_argument("-a", "--address", help="Real address or hostname (e.g. foobar.myorg.com)", required=True)
    p_add.set_defaults(func=cmd_add)

    p_get = subparsers.add_parser("get", help="Print the hostname for an alias")
    p_get.add_argument("-s", "--shortname", help="The hostname alias to get", required=True)
    p_get.set_defaults(func=cmd_get)

    p_list = subparsers.add_parser("list", help="List all registered devices")
    p_list.set_defaults(func=cmd_list)

    p_update = subparsers.add_parser("update", help="Update the hostname for an alias")
    p_update.add_argument("-s", "--shortname", help="Short alias for the device")
    p_update.add_argument("-a", "--address", help="Real address or hostname (e.g. foobar.myorg.com)", required=True)
    p_update.set_defaults(func=cmd_update)

    p_delete = subparsers.add_parser("delete", help="Remove a device alias")
    p_delete.add_argument("-s", "--shortname", help="Short alias of the device to delete.", required=True)
    p_delete.set_defaults(func=cmd_delete)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
