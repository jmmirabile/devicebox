import argparse
import devicebox


def do_deploy(hostname: str) -> None:
    print(f"Deploying to {hostname} ...")


def do_restart(hostname: str) -> None:
    print(f"Restarting service on {hostname} ...")


def do_status(hostname: str) -> None:
    print(f"Checking status on {hostname} ...")


ACTIONS = {
    "deploy": do_deploy,
    "restart": do_restart,
    "status": do_status,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Example script using devicebox.")
    parser.add_argument("action", choices=ACTIONS, help="Action to perform on the device")
    devicebox.add_device_argument(parser)

    args = parser.parse_args()
    hostname = devicebox.get_device(args.device)

    print(f"Device : {args.device}")
    print(f"Address: {hostname}")
    print()
    ACTIONS[args.action](hostname)


if __name__ == "__main__":
    main()