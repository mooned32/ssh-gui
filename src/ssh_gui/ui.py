# mypy: disable-error-code="no-untyped-call"
import tkinter as tk
from collections.abc import Callable
from tkinter import filedialog, messagebox

import ttkbootstrap as tb


class AddTunnelDialog(tb.Toplevel):
    on_add: Callable[[str, str, int, int], None]
    ent_comment: tb.Entry
    ent_rhost: tb.Entry
    ent_rport: tb.Entry
    ent_lport: tb.Entry

    def __init__(
        self, parent: tk.Tk | tk.Toplevel | None, on_add: Callable[[str, str, int, int], None]
    ) -> None:
        super().__init__(master=parent, title="Добавить туннель")
        self.geometry("440x360")
        self.minsize(400, 340)
        self.resizable(False, False)
        self.on_add = on_add

        if parent is not None:
            self.transient(parent)
            self.grab_set()

        btn_frame = tb.Frame(self)
        btn_frame.pack(side="bottom", fill="x", pady=15, padx=20)

        btn_add = tb.Button(
            btn_frame,
            text="Добавить",
            bootstyle="dark",
            command=self._submit,
            width=12,
        )
        btn_add.pack(side="right", padx=(10, 0))

        btn_cancel = tb.Button(
            btn_frame,
            text="Отмена",
            bootstyle="secondary",
            command=self.destroy,
            width=12,
        )
        btn_cancel.pack(side="right")

        form_frame = tb.Frame(self)
        form_frame.pack(side="top", fill="both", expand=True, padx=20, pady=(15, 0))

        lbl_comment = tb.Label(form_frame, text="Комментарий:")
        lbl_comment.pack(pady=(5, 2), anchor="w")
        self.ent_comment = tb.Entry(form_frame, font=("Sans", 10))
        self.ent_comment.pack(fill="x", pady=(0, 8))

        lbl_rhost = tb.Label(form_frame, text="Адрес Ресурса:")
        lbl_rhost.pack(pady=(0, 2), anchor="w")
        self.ent_rhost = tb.Entry(form_frame, font=("Sans", 10))
        self.ent_rhost.pack(fill="x", pady=(0, 8))

        lbl_rport = tb.Label(form_frame, text="Порт Ресурса:")
        lbl_rport.pack(pady=(0, 2), anchor="w")
        self.ent_rport = tb.Entry(form_frame, font=("Sans", 10))
        self.ent_rport.pack(fill="x", pady=(0, 8))

        lbl_lport = tb.Label(form_frame, text="Порт точки входа (наш порт):")
        lbl_lport.pack(pady=(0, 2), anchor="w")
        self.ent_lport = tb.Entry(form_frame, font=("Sans", 10))
        self.ent_lport.pack(fill="x", pady=(0, 8))

        self.ent_comment.focus_set()

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


class MainWindow(tb.Window):
    ent_server: tb.Entry
    ent_user: tb.Entry
    ent_key: tb.Entry
    btn_browse: tb.Button
    btn_run: tb.Button
    tree: tb.Treeview
    btn_save: tb.Button
    btn_add: tb.Button
    btn_delete: tb.Button

    def __init__(self) -> None:
        super().__init__(title="SSH GUI Tunnel Manager", themename="cosmo")
        self.geometry("860x560")
        self.minsize(720, 480)
        self.resizable(True, True)

        self._configure_styles()

        main_container = tb.Frame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        bottom_frame = tb.Frame(main_container)
        bottom_frame.pack(side="bottom", fill="x", pady=(15, 0))

        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=1)
        bottom_frame.columnconfigure(2, weight=1)

        self.btn_save = tb.Button(bottom_frame, text="Сохранить", bootstyle="dark", width=16)
        self.btn_save.grid(row=0, column=0, sticky="w")

        self.btn_delete = tb.Button(bottom_frame, text="Удалить", bootstyle="dark", width=16)
        self.btn_delete.grid(row=0, column=1)

        self.btn_add = tb.Button(bottom_frame, text="Добавить", bootstyle="dark", width=16)
        self.btn_add.grid(row=0, column=2, sticky="e")

        top_frame = tb.Frame(main_container)
        top_frame.pack(side="top", fill="x", pady=(0, 15))

        fields_frame = tb.Frame(top_frame)
        fields_frame.pack(side="left", fill="x", expand=True)
        fields_frame.columnconfigure(0, weight=0, minsize=110)
        fields_frame.columnconfigure(1, weight=1)
        fields_frame.columnconfigure(2, weight=0)

        lbl_server = tb.Label(fields_frame, text="Сервер:", font=("Sans", 10, "bold"))
        lbl_server.grid(row=0, column=0, padx=(0, 10), pady=4, sticky="e")
        self.ent_server = tb.Entry(fields_frame, font=("Sans", 10))
        self.ent_server.grid(row=0, column=1, columnspan=2, sticky="ew", pady=4)

        lbl_user = tb.Label(fields_frame, text="Пользователь:", font=("Sans", 10, "bold"))
        lbl_user.grid(row=1, column=0, padx=(0, 10), pady=4, sticky="e")
        self.ent_user = tb.Entry(fields_frame, font=("Sans", 10))
        self.ent_user.grid(row=1, column=1, columnspan=2, sticky="ew", pady=4)

        lbl_key = tb.Label(fields_frame, text="Ключ:", font=("Sans", 10, "bold"))
        lbl_key.grid(row=2, column=0, padx=(0, 10), pady=4, sticky="e")
        self.ent_key = tb.Entry(fields_frame, font=("Sans", 10))
        self.ent_key.grid(row=2, column=1, sticky="ew", pady=4)

        self.btn_browse = tb.Button(
            fields_frame,
            text="...",
            bootstyle="secondary",
            command=self._browse_key,
            width=3,
        )
        self.btn_browse.grid(row=2, column=2, padx=(6, 0), pady=4)

        run_frame = tb.Frame(top_frame)
        run_frame.pack(side="right", padx=(15, 0), fill="both")

        self.btn_run = tb.Button(
            run_frame,
            text="▶",
            style="Run.dark.TButton",
            width=5,
        )
        self.btn_run.pack(fill="both", expand=True)

        table_container = tb.Frame(main_container)
        table_container.pack(side="top", fill="both", expand=True)

        columns = ("comment", "rhost", "rport", "lport")
        self.tree = tb.Treeview(
            table_container,
            columns=columns,
            show="headings",
            selectmode="browse",
            bootstyle="dark",
        )
        self.tree.heading("comment", text="Комментарий", anchor="w")
        self.tree.heading("rhost", text="Адрес Ресурса", anchor="w")
        self.tree.heading("rport", text="Порт Ресурса", anchor="center")
        self.tree.heading("lport", text="Порт", anchor="center")

        self.tree.column("comment", width=220, minwidth=120, stretch=True)
        self.tree.column("rhost", width=200, minwidth=120, stretch=True)
        self.tree.column("rport", width=110, minwidth=80, stretch=False, anchor="center")
        self.tree.column("lport", width=120, minwidth=80, stretch=False, anchor="center")

        scrollbar = tb.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _configure_styles(self) -> None:
        style = tb.Style()
        style.configure("Run.dark.TButton", font=("Sans", 22, "bold"))
        style.configure("Run.danger.TButton", font=("Sans", 22, "bold"))

    def refresh_tree_tags(self) -> None:
        self.tree.tag_configure("even", background="#ffffff")
        self.tree.tag_configure("odd", background="#f1f3f5")

    def _browse_key(self) -> None:
        filename = filedialog.askopenfilename(
            title="Выберите файл SSH ключа",
            filetypes=[("SSH Keys / All Files", "*.*")],
            parent=self,
        )
        if filename:
            self.ent_key.delete(0, tk.END)
            self.ent_key.insert(0, filename)
