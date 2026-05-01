from confbox import ConfBox

_config = ConfBox("devicebox", config_filename="devicebox.yaml", auto_save=True)


def add(alias: str, hostname: str) -> None:
    if _config.get(f"devices.{alias}") is not None:
        raise KeyError(f"Device '{alias}' already exists")
    _config.set(f"devices.{alias}.hostname", hostname)


def get(alias: str) -> dict | None:
    return _config.get(f"devices.{alias}")


def list_all() -> dict:
    return _config.get("devices") or {}


def update(alias: str, hostname: str) -> None:
    if _config.get(f"devices.{alias}") is None:
        raise KeyError(f"Device '{alias}' not found")
    _config.set(f"devices.{alias}.hostname", hostname)


def delete(alias: str) -> None:
    if _config.get(f"devices.{alias}") is None:
        raise KeyError(f"Device '{alias}' not found")
    _config.delete(f"devices.{alias}")


def get_device(alias: str) -> str:
    hostname = _config.get(f"devices.{alias}.hostname")
    if hostname is None:
        raise KeyError(f"Device '{alias}' not found")
    return hostname
