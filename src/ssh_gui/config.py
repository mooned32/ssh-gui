import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast


@dataclass
class Tunnel:
    comment: str
    remote_host: str
    remote_port: int
    local_port: int


@dataclass
class Config:
    server: str = ""
    user: str = ""
    key_path: str = ""
    tunnels: list[Tunnel] = field(default_factory=list)


def get_config_path() -> Path:
    config_dir = Path.home() / ".ssh-gui"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "config.json"


def load_config() -> Config:
    path = get_config_path()
    if not path.exists():
        return Config()

    try:
        with open(path, encoding="utf-8") as f:
            data_raw: object = cast(object, json.load(f))

        if not isinstance(data_raw, dict):
            return Config()

        data = cast(dict[str, object], data_raw)

        server_obj = data.get("server", "")
        server = str(server_obj) if isinstance(server_obj, str) else ""

        user_obj = data.get("user", "")
        user = str(user_obj) if isinstance(user_obj, str) else ""

        key_obj = data.get("key_path", "")
        key_path = str(key_obj) if isinstance(key_obj, str) else ""

        tunnels: list[Tunnel] = []
        raw_tunnels = data.get("tunnels")
        if isinstance(raw_tunnels, list):
            raw_list = cast(list[object], raw_tunnels)
            for item in raw_list:
                if isinstance(item, dict):
                    t_dict = cast(dict[str, object], item)
                    c_obj = t_dict.get("comment", "")
                    rh_obj = t_dict.get("remote_host", "")
                    rp_obj = t_dict.get("remote_port", 0)
                    lp_obj = t_dict.get("local_port", 0)

                    comment = str(c_obj) if isinstance(c_obj, str) else ""
                    rhost = str(rh_obj) if isinstance(rh_obj, str) else ""
                    rport = int(str(rp_obj)) if isinstance(rp_obj, (int, str)) else 0
                    lport = int(str(lp_obj)) if isinstance(lp_obj, (int, str)) else 0

                    tunnels.append(
                        Tunnel(
                            comment=comment,
                            remote_host=rhost,
                            remote_port=rport,
                            local_port=lport,
                        )
                    )

        return Config(
            server=server,
            user=user,
            key_path=key_path,
            tunnels=tunnels,
        )
    except Exception:
        return Config()


def save_config(config: Config) -> None:
    path = get_config_path()
    data: dict[str, object] = {
        "server": config.server,
        "user": config.user,
        "key_path": config.key_path,
        "tunnels": [
            {
                "comment": t.comment,
                "remote_host": t.remote_host,
                "remote_port": t.remote_port,
                "local_port": t.local_port,
            }
            for t in config.tunnels
        ],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
