import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Callable, Optional

class AddTunnelDialog(tk.Toplevel):
    on_add: Callable[[str, str, int, int], None]
    ent_comment: ttk.Entry
    ent_rhost: ttk.Entry
    ent_rport: ttk.Entry
    ent_lport: ttk.Entry

    def __init__(
        self, parent: Optional[tk.Misc], on_add: Callable[[str, str, int, int], None]
    ) -> None:
        super().__init__(parent)
        self.title("Добавить туннель")
        self.geometry("380x300")
        self.resizable(False, False)
        self.configure(bg="#f8f9fa")
        self.on_add = on_add

        if parent is not None:
            self.transient(parent)
            self.grab_set()

        lbl_comment = ttk.Label(self, text="Комментарий:", style="Main.TLabel")
        lbl_comment.pack(pady=(12, 2), padx=15, anchor="w")
        self.ent_comment = ttk.Entry(self, font=("Sans", 10))
        self.ent_comment.pack(fill="x", padx=15)

        lbl_rhost = ttk.Label(self, text="Адрес Ресурса:", style="Main.TLabel")
        lbl_rhost.pack(pady=(8, 2), padx=15, anchor="w")
        self.ent_rhost = ttk.Entry(self, font=("Sans", 10))
        self.ent_rhost.pack(fill="x", padx=15)

        lbl_rport = ttk.Label(self, text="Порт Ресурса:", style="Main.TLabel")
        lbl_rport.pack(pady=(8, 2), padx=15, anchor="w")
        self.ent_rport = ttk.Entry(self, font=("Sans", 10))
        self.ent_rport.pack(fill="x", padx=15)

        lbl_lport = ttk.Label(self, text="Наш порт (точка входа):", style="Main.TLabel")
        lbl_lport.pack(pady=(8, 2), padx=15, anchor="w")
        self.ent_lport = ttk.Entry(self, font=("Sans", 10))
        self.ent_lport.pack(fill="x", padx=15)

        btn_frame = ttk.Frame(self, style="Main.TFrame")
        btn_frame.pack(fill="x", pady=20, padx=15)

        btn_add = ttk.Button(
            btn_frame, text="Добавить", style="Success.TButton", command=self._submit
        )
        btn_add.pack(side="right", padx=(5, 0))

        btn_cancel = ttk.Button(
            btn_frame, text="Отмена", style="Secondary.TButton", command=self.destroy
        )
        btn_cancel.pack(side="right")

    def _submit(self) -> None:
        try:
            comment = self.ent_comment.get().strip()
            rhost = self.ent_rhost.get().strip()
            rport = int(self.ent_rport.get().strip())
            lport = int(self.ent_lport.get().strip())
            if not comment or not rhost:
                raise ValueError("Заполните текстовые поля")
            self.on_add(comment, rhost, rport, lport)
            self.destroy()
        except ValueError:
            messagebox.showerror(
                "Ошибка",
                "Проверьте правильность введенных данных (порты должны быть числами).",
                parent=self,
            )

class MainWindow(tk.Tk):
    ent_server: ttk.Entry
    ent_user: ttk.Entry
    ent_key: ttk.Entry
    btn_browse: ttk.Button
    btn_run: ttk.Button
    tree: ttk.Treeview
    btn_save: ttk.Button
    btn_add: ttk.Button
    btn_delete: ttk.Button

    def __init__(self) -> None:
        super().__init__()
        self.title("SSH GUI Tunnel Manager")
        self.geometry("820x560")
        self.minsize(700, 480)
        self.configure(bg="#f8f9fa")

        self._setup_styles()

        # Верхняя панель
        top_frame = ttk.Frame(self, style="Main.TFrame")
        top_frame.pack(fill="x", padx=15, pady=15)

        fields_frame = ttk.Frame(top_frame, style="Main.TFrame")
        fields_frame.pack(side="left", fill="x", expand=True)
        fields_frame.columnconfigure(0, weight=0, minsize=130)
        fields_frame.columnconfigure(1, weight=1, minsize=200)
        fields_frame.columnconfigure(2, weight=0, minsize=40)

        lbl_server = ttk.Label(fields_frame, text="Сервер:", style="Main.TLabel")
        lbl_server.grid(row=0, column=0, padx=(0, 10), pady=6, sticky="e")
        self.ent_server = ttk.Entry(fields_frame, font=("Sans", 10))
        self.ent_server.grid(row=0, column=1, columnspan=2, sticky="ew", pady=6)

        lbl_user = ttk.Label(fields_frame, text="Пользователь:", style="Main.TLabel")
        lbl_user.grid(row=1, column=0, padx=(0, 10), pady=6, sticky="e")
        self.ent_user = ttk.Entry(fields_frame, font=("Sans", 10))
        self.ent_user.grid(row=1, column=1, columnspan=2, sticky="ew", pady=6)

        lbl_key = ttk.Label(fields_frame, text="Ключ:", style="Main.TLabel")
        lbl_key.grid(row=2, column=0, padx=(0, 10), pady=6, sticky="e")
        self.ent_key = ttk.Entry(fields_frame, font=("Sans", 10))
        self.ent_key.grid(row=2, column=1, sticky="ew", pady=6)

        self.btn_browse = ttk.Button(
            fields_frame,
            text="...",
            style="Secondary.TButton",
            command=self._browse_key,
            width=4,
        )
        self.btn_browse.grid(row=2, column=2, padx=(6, 0), pady=6)

        # Кнопка Запуск
        run_frame = ttk.Frame(top_frame, style="Main.TFrame")
        run_frame.pack(side="right", padx=(20, 0), fill="y")

        self.btn_run = ttk.Button(
            run_frame,
            text="▶ Запуск",
            style="Success.TButton",
            width=12,
        )
        self.btn_run.pack(fill="both", expand=True, pady=6)

        # Таблица
        table_frame = ttk.Frame(self, style="Main.TFrame")
        table_frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = ("comment", "rhost", "rport", "lport")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=10,
        )
        self.tree.heading("comment", text="Комментарий", anchor="w")
        self.tree.heading("rhost", text="Адрес Ресурса", anchor="w")
        self.tree.heading("rport", text="Порт Ресурса", anchor="center")
        self.tree.heading("lport", text="Порт точки входа", anchor="center")

        self.tree.column("comment", width=220, minwidth=120, stretch=True)
        self.tree.column("rhost", width=200, minwidth=120, stretch=True)
        self.tree.column("rport", width=110, minwidth=80, stretch=False, anchor="center")
        self.tree.column("lport", width=120, minwidth=80, stretch=False, anchor="center")

        def _on_scroll(*args: object) -> None:
            self.tree.yview(*args)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=_on_scroll)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Нижняя панель
        bottom_frame = ttk.Frame(self, style="Main.TFrame")
        bottom_frame.pack(fill="x", padx=15, pady=15)

        self.btn_save = ttk.Button(
            bottom_frame, text="Сохранить", style="Primary.TButton", width=14
        )
        self.btn_save.pack(side="left")

        self.btn_add = ttk.Button(
            bottom_frame, text="Добавить", style="Success.TButton", width=14
        )
        self.btn_add.pack(side="right", padx=(10, 0))

        self.btn_delete = ttk.Button(
            bottom_frame, text="Удалить", style="Danger.TButton", width=14
        )
        self.btn_delete.pack(side="right")

    def _setup_styles(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Main.TFrame", background="#f8f9fa")
        style.configure
