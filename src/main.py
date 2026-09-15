import sys

from PyQt6.QtWidgets import QApplication

from app import App
from signals import connect_signal


def main() -> int:
    app = QApplication(sys.argv)
    _ = app.setStyle("windowsvista")

    controller = App()
    controller.ui.show()

    # Ensure SSH is stopped on exit
    connect_signal(app.aboutToQuit, controller.ssh.stop)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
