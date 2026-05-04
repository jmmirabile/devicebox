# devicebox

A Python utility for managing device alias-to-hostname mappings. Register short aliases for your devices and look them 
up by real hostname — from the command line or from within your own scripts.

The core value of this is the shared registry and mnemonic/alias for device names. Instead of typing the full hostname, 
you type an alias or shortname you defined. Any script that uses devicebox will recognize that name. 

This also decouples device names from scripts. Without devicebox, scripts may require the fqdn as an argument or hardcode 
the hostname. 

If the user uses environment names in the shortname/alias, then grep can be used to find all entries for a specific 
environment, for example:

```bash
devicebox list | grep ^prd
```
So, if you add:

```bash
devicebox add -s proddmzfw01 -a plocfwdmz01.int.domain.com
```
Then, if you don't remember the shortname, use grep:
```bash
devicebox list | grep ^prod
```
And you'll find all the entries that start with "prod".

For a script that takes a device name as an argument. You can modify it to use devicebox, then you might type:
```bash
checkuptime -d proddmzfw01 uptime
```
Of course, this would be an example of a script that uses either ssh or the platform API to get the uptime. 


## Installation

```bash
pip install devicebox
```

Or install with user-level permissions (no sudo required):

```bash
pip install --user devicebox
```

## Configuration

devicebox stores its registry in the OS-appropriate config directory using [confbox](https://github.com/jmmirabile/confbox):

| Platform | Config file location |
|----------|----------------------|
| Linux    | `~/.config/devicebox/devicebox.yaml` |
| macOS    | `~/Library/Application Support/devicebox/devicebox.yaml` |
| Windows  | `%LOCALAPPDATA%\Programs\devicebox\devicebox.yaml` |

The registry format is:

```yaml
devices:
  foobar:
    hostname: foobar.myorg.com
  server1:
    hostname: server1.myorg.com
```

---

## CLI Usage

### add

Register a new device alias.

```bash
devicebox add -s <shortname> -a <address>
```

```bash
devicebox add -s foobar -a foobar.myorg.com
# Added: foobar -> foobar.myorg.com
```

| Flag | Description |
|------|-------------|
| `-s`, `--shortname` | Short alias for the device (required) |
| `-a`, `--address` | Real hostname or address (required) |

---

### get

Print the real hostname for an alias.

```bash
devicebox get -s <shortname>
```

```bash
devicebox get -s foobar
# foobar.myorg.com
```

| Flag | Description |
|------|-------------|
| `-s`, `--shortname` | Alias to look up (required) |

---

### list

List all registered devices.

```bash
devicebox list
```

```
foobar   foobar.myorg.com
server1  server1.myorg.com
```

---

### update

Update the address for an existing alias.

```bash
devicebox update -s <shortname> -a <address>
```

```bash
devicebox update -s foobar -a foobar2.myorg.com
# Updated: foobar -> foobar2.myorg.com
```

| Flag | Description |
|------|-------------|
| `-s`, `--shortname` | Alias to update (required) |
| `-a`, `--address` | New hostname or address (required) |

---

### delete

Remove a device alias from the registry.

```bash
devicebox delete -s <shortname>
```

```bash
devicebox delete -s foobar
# Deleted: foobar
```

| Flag | Description |
|------|-------------|
| `-s`, `--shortname` | Alias to remove (required) |

---

## Quick Testing

A quick way to verify a devicebox entry is correct is to use shell command substitution directly on the command line:

```bash
ping `devicebox get -s mysite`
```

This resolves the alias on the fly and passes the real address to the command, without having to look it up separately first.

---

## Library Usage

devicebox can be imported into your own scripts to add device resolution to an existing argparse-based CLI.

### Adding --device to your parser

```python
import argparse
import devicebox

parser = argparse.ArgumentParser()
parser.add_argument("command")
devicebox.add_device_argument(parser)  # injects --device ALIAS

args = parser.parse_args()
hostname = devicebox.get_device(args.device)

print(f"Connecting to {args.device} at {hostname}")
```

A user would invoke your script like:

```bash
python myscript.py deploy --device foobar
# Connecting to foobar at foobar.myorg.com
```

### Using with subparsers

When your script uses subparsers, define `-d`/`--device` at the top-level parser and resolve the hostname before dispatching to the subcommand. Attach the resolved hostname back onto `args` so every subparser function can access it without needing a different signature.

```python
import argparse
import devicebox


def cmd_ltm_list(args):
    client = LtmClient(args.hostname)
    client.list(args.vip)


def cmd_ltm_stats(args):
    client = LtmClient(args.hostname)
    client.stats()


def main():
    parser = argparse.ArgumentParser()
    devicebox.add_device_argument(parser)   # -d / --device at the top level

    subparsers = parser.add_subparsers(dest="command")

    p_list = subparsers.add_parser("list")
    p_list.add_argument("-v", "--vip", required=True)
    p_list.set_defaults(func=cmd_ltm_list)

    p_stats = subparsers.add_parser("stats")
    p_stats.set_defaults(func=cmd_ltm_stats)

    args = parser.parse_args()
    args.hostname = devicebox.get_device(args.device)  # resolve once, attach to args
    args.func(args)                                     # every subcommand gets it


if __name__ == "__main__":
    main()
```

```bash
python f5.py -d foobar-lb list -v myvip
python f5.py -d foobar-lb stats
```

The `-d` flag must come before the subcommand. Once argparse hands off to a subparser, top-level flags are no longer in scope.

---

### API Reference

| Function | Signature | Description |
|----------|-----------|-------------|
| `add_device_argument` | `(parser: ArgumentParser) -> None` | Injects `--device ALIAS` into an existing parser |
| `get_device` | `(alias: str) -> str` | Returns the real hostname for an alias; raises `KeyError` if not found |
| `add` | `(alias: str, hostname: str) -> None` | Registers a new alias; raises `KeyError` if it already exists |
| `get` | `(alias: str) -> dict \| None` | Returns the device entry dict or `None` if not found |
| `list_all` | `() -> dict` | Returns all registered devices as a dict |
| `update` | `(alias: str, hostname: str) -> None` | Updates the hostname for an alias; raises `KeyError` if not found |
| `delete` | `(alias: str) -> None` | Removes an alias; raises `KeyError` if not found |

### Example: full script integration

```python
import argparse
import devicebox

def main():
    parser = argparse.ArgumentParser(description="Deploy to a device")
    parser.add_argument("action", choices=["deploy", "restart", "status"])
    devicebox.add_device_argument(parser)
    args = parser.parse_args()

    hostname = devicebox.get_device(args.device)
    print(f"Running '{args.action}' on {args.device} ({hostname})")

if __name__ == "__main__":
    main()
```

```bash
python deploy.py restart --device server1
# Running 'restart' on server1 (server1.myorg.com)
```

---

## Requirements

- Python 3.10+
- [confbox](https://github.com/jmmirabile/confbox)
