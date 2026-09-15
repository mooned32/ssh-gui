import sys

from PyQt6.QtWidgets import QApplication

from app import App


def main() -> int:
    app = QApplication(sys.argv)
    _ = app.setStyle("windowsvista")

    controller = App()
    controller.ui.show()

    # Ensure SSH is stopped on exit
    _ = app.aboutToQuit.connect(controller.ssh.stop)

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
