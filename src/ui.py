from collections.abc import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)


class AddTunnelDialog(QDialog):
    on_add: Callable[[str, str, int, int], None]
    ent_comment: QLineEdit
    ent_rhost: QLineEdit
    ent_rport: QLineEdit
    ent_lport: QLineEdit

    def __init__(
        self,
        parent: QWidget | None,
        on_add: Callable[[str, str, int, int], None],
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Добавить туннель")
        self.setMinimumSize(440, 360)
        self.setMaximumSize(440, 360)
        self.setModal(True)
        self.on_add = on_add

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)

        # Form fields
        lbl_comment = QLabel("Комментарий:")
        self.ent_comment = QLineEdit()
        layout.addWidget(lbl_comment)
        layout.addWidget(self.ent_comment)

        lbl_rhost = QLabel("Адрес Ресурса:")
        self.ent_rhost = QLineEdit()
        layout.addWidget(lbl_rhost)
        layout.addWidget(self.ent_rhost)

        lbl_rport = QLabel("Порт Ресурса:")
        self.ent_rport = QLineEdit()
        layout.addWidget(lbl_rport)
        layout.addWidget(self.ent_rport)

        lbl_lport = QLabel("Порт точки входа (наш порт):")
        self.ent_lport = QLineEdit()
        layout.addWidget(lbl_lport)
        layout.addWidget(self.ent_lport)

        layout.addStretch()

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Отмена")
        btn_cancel.setFixedWidth(110)
        _ = btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_add = QPushButton("Добавить")
        btn_add.setFixedWidth(110)
        btn_add.setStyleSheet("font-weight: bold;")
        _ = btn_add.clicked.connect(self._submit)
        btn_layout.addWidget(btn_add)

        layout.addLayout(btn_layout)

        self.ent_comment.setFocus()

    def _submit(self) -> None:
        try:
            comment = self.ent_comment.text().strip()
            rhost = self.ent_rhost.text().strip()
            rport = int(self.ent_rport.text().strip())
            lport = int(self.ent_lport.text().strip())
            if not comment or not rhost:
                raise ValueError("Заполните текстовые поля")
            self.on_add(comment, rhost, rport, lport)
            self.accept()
        except ValueError:
            _ = QMessageBox.critical(
                self,
                "Ошибка",
                "Проверьте правильность введенных данных (порты должны быть числами).",
            )


class MainWindow(QMainWindow):
    ent_server: QLineEdit
    ent_user: QLineEdit
    ent_key: QLineEdit
    btn_browse: QPushButton
    btn_run: QPushButton
    table: QTableWidget
    btn_save: QPushButton
    btn_add: QPushButton
    btn_delete: QPushButton

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SSH GUI Tunnel Manager")
        self.resize(860, 560)
        self.setMinimumSize(720, 480)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Top frame: fields + run button
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(15)

        fields_widget = QWidget()
        fields_layout = QGridLayout(fields_widget)
        fields_layout.setContentsMargins(0, 0, 0, 0)
        fields_layout.setHorizontalSpacing(10)
        fields_layout.setVerticalSpacing(4)
        fields_layout.setColumnStretch(1, 1)

        lbl_server = QLabel("Сервер:")
        lbl_server.setStyleSheet("font-weight: bold;")
        self.ent_server = QLineEdit()
        align = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        fields_layout.addWidget(lbl_server, 0, 0, alignment=align)
        fields_layout.addWidget(self.ent_server, 0, 1, 1, 2)

        lbl_user = QLabel("Пользователь:")
        lbl_user.setStyleSheet("font-weight: bold;")
        self.ent_user = QLineEdit()
        fields_layout.addWidget(lbl_user, 1, 0, alignment=align)
        fields_layout.addWidget(self.ent_user, 1, 1, 1, 2)

        lbl_key = QLabel("Ключ:")
        lbl_key.setStyleSheet("font-weight: bold;")
        self.ent_key = QLineEdit()
        self.btn_browse = QPushButton("...")
        self.btn_browse.setFixedWidth(32)
        _ = self.btn_browse.clicked.connect(self._browse_key)
        fields_layout.addWidget(lbl_key, 2, 0, alignment=align)
        fields_layout.addWidget(self.ent_key, 2, 1)
        fields_layout.addWidget(self.btn_browse, 2, 2)

        top_layout.addWidget(fields_widget, stretch=1)

        # Run button
        self.btn_run = QPushButton("▶")
        self.btn_run.setFixedSize(80, 80)
        self.btn_run.setStyleSheet("font-size: 22px; font-weight: bold;")
        top_layout.addWidget(self.btn_run, alignment=Qt.AlignmentFlag.AlignTop)

        main_layout.addWidget(top_widget)

        # Table
        self.table = QTableWidget(0, 4)
        labels = ["Комментарий", "Адрес Ресурса", "Порт Ресурса", "Порт"]
        self.table.setHorizontalHeaderLabels(labels)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        vheader = self.table.verticalHeader()
        if vheader is not None:
            vheader.setVisible(False)

        header = self.table.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
            self.table.setColumnWidth(2, 110)
            self.table.setColumnWidth(3, 120)

        main_layout.addWidget(self.table, stretch=1)

        # Bottom frame
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_save = QPushButton("Сохранить")
        self.btn_save.setFixedWidth(140)
        self.btn_save.setStyleSheet("font-weight: bold;")

        self.btn_delete = QPushButton("Удалить")
        self.btn_delete.setFixedWidth(140)

        self.btn_add = QPushButton("Добавить")
        self.btn_add.setFixedWidth(140)

        bottom_layout.addWidget(self.btn_save, alignment=Qt.AlignmentFlag.AlignLeft)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_delete)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.btn_add, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addWidget(bottom_widget)

        self._update_run_button_style(running=False)

    def _update_run_button_style(self, *, running: bool) -> None:
        style_running = (
            "font-size: 22px; font-weight: bold; "
            "background-color: #dc3545; color: white; border-radius: 6px;"
        )
        style_stopped = (
            "font-size: 22px; font-weight: bold; "
            "background-color: #343a40; color: white; border-radius: 6px;"
        )
        if running:
            self.btn_run.setText("⏹")
            self.btn_run.setStyleSheet(style_running)
        else:
            self.btn_run.setText("▶")
            self.btn_run.setStyleSheet(style_stopped)

    def set_running_state(self, *, running: bool) -> None:
        self._update_run_button_style(running=running)
        enabled = not running
        self.ent_server.setEnabled(enabled)
        self.ent_user.setEnabled(enabled)
        self.ent_key.setEnabled(enabled)
        self.btn_browse.setEnabled(enabled)

    def _browse_key(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл SSH ключа",
            "",
            "All Files (*.*)",
        )
        if filename:
            self.ent_key.setText(filename)
