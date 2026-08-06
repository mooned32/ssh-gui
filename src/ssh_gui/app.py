from tkinter import messagebox
from typing import cast

from ssh_gui.config import Config, Tunnel, load_config, save_config
from ssh_gui.ssh_runner import SSHRunner
from ssh_gui.ui import AddTunnelDialog, MainWindow


class App:
    config: Config
    ssh: SSHRunner
    ui: MainWindow

    def __init__(self) -> None:
        self.config = load_config()
        self.ssh = SSHRunner()
        self.ui = MainWindow()
        self._bind_events()
        self._load_to_ui()
        self._check_ssh_status()

    def _bind_events(self) -> None:
        self.ui.btn_save.config(command=self.save_data)
        self.ui.btn_add.config(command=self.show_add_dialog)
        self.ui.btn_delete.config(command=self.delete_selected)
        self.ui.btn_run.config(command=self.toggle_ssh)

    def _load_to_ui(self) -> None:
        self.ui.ent_server.delete(0, "end")
        self.ui.ent_server.insert(0, self.config.server)

        self.ui.ent_user.delete(0, "end")
        self.ui.ent_user.insert(0, self.config.user)

        self.ui.ent_key.delete(0, "end")
        self.ui.ent_key.insert(0, self.config.key_path)

        for item in self.ui.tree.get_children():
            self.ui.tree.delete(item)

        for i, t in enumerate(self.config.tunnels):
            tag = "even" if i % 2 == 0 else "odd"
            self.ui.tree.insert(
                "",
                "end",
                values=(t.comment, t.remote_host, t.remote_port, t.local_port),
                tags=(tag,),
            )
        self.ui.refresh_tree_tags()

    def save_data(self) -> None:
        self.config.server = self.ui.ent_server.get().strip()
        self.config.user = self.ui.ent_user.get().strip()
        self.config.key_path = self.ui.ent_key.get().strip()

        self.config.tunnels = []
        for item in self.ui.tree.get_children():
            raw_item = self.ui.tree.item(item, "values")
            if isinstance(raw_item, (list, tuple)) and len(raw_item) >= 4:
                item_tuple = cast(tuple[object, object, object, object], raw_item)
                comment = str(item_tuple[0])
                rhost = str(item_tuple[1])
                rport = int(str(item_tuple[2]))
                lport = int(str(item_tuple[3]))
                self.config.tunnels.append(
                    Tunnel(
                        comment=comment,
                        remote_host=rhost,
                        remote_port=rport,
                        local_port=lport,
                    )
                )
        save_config(self.config)
        messagebox.showinfo("Сохранение", "Настройки успешно сохранены!", parent=self.ui)

    def show_add_dialog(self) -> None:
        def on_add(comment: str, rhost: str, rport: int, lport: int) -> None:
            count = len(self.ui.tree.get_children())
            tag = "even" if count % 2 == 0 else "odd"
            self.ui.tree.insert("", "end", values=(comment, rhost, rport, lport), tags=(tag,))

        AddTunnelDialog(self.ui, on_add)

    def delete_selected(self) -> None:
        selected = self.ui.tree.selection()
        if not selected:
            return
        for item in selected:
            self.ui.tree.delete(item)

        for i, item in enumerate(self.ui.tree.get_children()):
            tag = "even" if i % 2 == 0 else "odd"
            self.ui.tree.item(item, tags=(tag,))

    def toggle_ssh(self) -> None:
        if self.ssh.is_running():
            self.ssh.stop()
            self._update_run_button_state()
        else:
            server = self.ui.ent_server.get().strip()
            user = self.ui.ent_user.get().strip()
            if not server or not user:
                messagebox.showerror(
                    "Ошибка", "Заполните поля 'Сервер' и 'Пользователь'.", parent=self.ui
                )
                return

            self.save_data()
            try:
                self.ssh.start(self.config)
                self._update_run_button_state()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка запуска SSH: {e}", parent=self.ui)

    def _update_run_button_state(self) -> None:
        if self.ssh.is_running():
            self.ui.btn_run.config(text="⏹", style="Run.danger.TButton")
            self.ui.ent_server.config(state="disabled")
            self.ui.ent_user.config(state="disabled")
            self.ui.ent_key.config(state="disabled")
            self.ui.btn_browse.config(state="disabled")
        else:
            self.ui.btn_run.config(text="▶", style="Run.dark.TButton")
            self.ui.ent_server.config(state="normal")
            self.ui.ent_user.config(state="normal")
            self.ui.ent_key.config(state="normal")
            self.ui.btn_browse.config(state="normal")

    def _check_ssh_status(self) -> None:
        btn_text = str(self.ui.btn_run.cget("text"))

        if btn_text == "⏹" and not self.ssh.is_running():
            self._update_run_button_state()
            messagebox.showwarning(
                "Внимание", "Процесс SSH был непредвиденно завершен.", parent=self.ui
            )

        self.ui.after(1000, self._check_ssh_status)

    def run(self) -> None:
        self.ui.mainloop()
        self.ssh.stop()
