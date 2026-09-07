from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem

from ssh_gui.config import Config, Tunnel, load_config, save_config
from ssh_gui.ssh_runner import SSHRunner
from ssh_gui.ui import AddTunnelDialog, MainWindow


class App:
    config: Config
    ssh: SSHRunner
    ui: MainWindow
    _timer: QTimer
    _was_running: bool

    def __init__(self) -> None:
        self.config = load_config()
        self.ssh = SSHRunner()
        self.ui = MainWindow()
        self._was_running = False
        self._bind_events()
        self._load_to_ui()
        self._update_run_button_state()
        self._was_running = self.ssh.is_running()

        self._timer = QTimer(self.ui)
        self._timer.setInterval(1000)
        _ = self._timer.timeout.connect(self._check_ssh_status)
        self._timer.start()

    def _bind_events(self) -> None:
        _ = self.ui.btn_save.clicked.connect(self.save_data)
        _ = self.ui.btn_add.clicked.connect(self.show_add_dialog)
        _ = self.ui.btn_delete.clicked.connect(self.delete_selected)
        _ = self.ui.btn_run.clicked.connect(self.toggle_ssh)

    def _load_to_ui(self) -> None:
        self.ui.ent_server.setText(self.config.server)
        self.ui.ent_user.setText(self.config.user)
        self.ui.ent_key.setText(self.config.key_path)

        self.ui.table.setRowCount(0)
        for t in self.config.tunnels:
            row = self.ui.table.rowCount()
            self.ui.table.insertRow(row)
            self.ui.table.setItem(row, 0, QTableWidgetItem(t.comment))
            self.ui.table.setItem(row, 1, QTableWidgetItem(t.remote_host))
            self.ui.table.setItem(row, 2, QTableWidgetItem(str(t.remote_port)))
            self.ui.table.setItem(row, 3, QTableWidgetItem(str(t.local_port)))
            for col in range(4):
                item = self.ui.table.item(row, col)
                if item is not None:
                    item.setTextAlignment(int(item.textAlignment()) | 0)
            # center ports
            for col in (2, 3):
                item = self.ui.table.item(row, col)
                if item is not None:
                    item.setTextAlignment(int(Qt.AlignmentFlag.AlignCenter))

    def save_data(self) -> None:
        self.config.server = self.ui.ent_server.text().strip()
        self.config.user = self.ui.ent_user.text().strip()
        self.config.key_path = self.ui.ent_key.text().strip()

        self.config.tunnels = []
        for row in range(self.ui.table.rowCount()):
            comment_item = self.ui.table.item(row, 0)
            rhost_item = self.ui.table.item(row, 1)
            rport_item = self.ui.table.item(row, 2)
            lport_item = self.ui.table.item(row, 3)
            if (
                comment_item is None
                or rhost_item is None
                or rport_item is None
                or lport_item is None
            ):
                continue
            assert comment_item is not None  # noqa: S101
            assert rhost_item is not None  # noqa: S101
            assert rport_item is not None  # noqa: S101
            assert lport_item is not None  # noqa: S101
            comment = comment_item.text()
            rhost = rhost_item.text()
            try:
                rport = int(rport_item.text())
                lport = int(lport_item.text())
            except ValueError:
                continue
            self.config.tunnels.append(
                Tunnel(
                    comment=comment,
                    remote_host=rhost,
                    remote_port=rport,
                    local_port=lport,
                )
            )
        save_config(self.config)
        _ = QMessageBox.information(self.ui, "Сохранение", "Настройки успешно сохранены!")

    def show_add_dialog(self) -> None:
        def on_add(comment: str, rhost: str, rport: int, lport: int) -> None:
            row = self.ui.table.rowCount()
            self.ui.table.insertRow(row)
            self.ui.table.setItem(row, 0, QTableWidgetItem(comment))
            self.ui.table.setItem(row, 1, QTableWidgetItem(rhost))
            rport_item = QTableWidgetItem(str(rport))
            rport_item.setTextAlignment(int(Qt.AlignmentFlag.AlignCenter))
            self.ui.table.setItem(row, 2, rport_item)
            lport_item = QTableWidgetItem(str(lport))
            lport_item.setTextAlignment(int(Qt.AlignmentFlag.AlignCenter))
            self.ui.table.setItem(row, 3, lport_item)

        dlg = AddTunnelDialog(self.ui, on_add)
        _ = dlg.exec()

    def delete_selected(self) -> None:
        selected = self.ui.table.currentRow()
        if selected < 0:
            # try selected ranges
            ranges = self.ui.table.selectedRanges()
            if not ranges:
                return
            selected = ranges[0].topRow()
        self.ui.table.removeRow(selected)

    def toggle_ssh(self) -> None:
        if self.ssh.is_running():
            self.ssh.stop()
            self._update_run_button_state()
        else:
            server = self.ui.ent_server.text().strip()
            user = self.ui.ent_user.text().strip()
            if not server or not user:
                _ = QMessageBox.critical(
                    self.ui, "Ошибка", "Заполните поля 'Сервер' и 'Пользователь'."
                )
                return

            self.save_data()
            try:
                self.ssh.start(self.config)
                self._update_run_button_state()
            except Exception as e:
                _ = QMessageBox.critical(self.ui, "Ошибка", f"Ошибка запуска SSH: {e}")

    def _update_run_button_state(self) -> None:
        running = self.ssh.is_running()
        self.ui.set_running_state(running=running)
        self._was_running = running

    def _check_ssh_status(self) -> None:
        running = self.ssh.is_running()
        if self._was_running and not running:
            self._update_run_button_state()
            _ = QMessageBox.warning(self.ui, "Внимание", "Процесс SSH был непредвиденно завершен.")
        elif self._was_running != running:
            self._update_run_button_state()
        self._was_running = running

    def run(self) -> None:
        self.ui.show()
        # Stop SSH when window closes is handled via timer parent; ensure cleanup
        # Caller should exec QApplication

    def stop(self) -> None:
        self._timer.stop()
        self.ssh.stop()
