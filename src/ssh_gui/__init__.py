import sys

from PyQt6.QtWidgets import QApplication

from ssh_gui.app import App


def main() -> None:
    app = QApplication(sys.argv)
    _ = app.setStyle("windowsvista")

    controller = App()
    controller.ui.show()

    # Ensure SSH is stopped on exit
    _ = app.aboutToQuit.connect(controller.ssh.stop)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
