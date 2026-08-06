import subprocess
import sys

from .config import Config


class SSHRunner:
    def __init__(self) -> None:
        self.process: subprocess.Popen[bytes] | None = None

    def start(self, config: Config) -> None:
        if self.is_running():
            return

        cmd: list[str] = ["ssh", "-N", "-o", "ExitOnForwardFailure=yes"]

        if config.key_path:
            cmd.extend(["-i", config.key_path])

        for t in config.tunnels:
            cmd.extend(["-L", f"{t.local_port}:{t.remote_host}:{t.remote_port}"])

        cmd.append(f"{config.user}@{config.server}")

        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NO_WINDOW

        self.process = subprocess.Popen(  # noqa: S603
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )

    def stop(self) -> None:
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

    def is_running(self) -> bool:
        if not self.process:
            return False
        return self.process.poll() is None
