import PyInstaller.__main__


def build() -> None:
    args = [
        "src/ssh_gui/__init__.py",
        "--name=ssh-gui",
        "--paths=src",
        "--collect-all=ttkbootstrap",
        "--collect-all=PIL",
        "--hidden-import=PIL._tkinter_finder",
        "--hidden-import=PIL._imagingtk",
        "--onefile",
        "--noconsole",
        "--clean",
    ]
    PyInstaller.__main__.run(args)


if __name__ == "__main__":
    build()
