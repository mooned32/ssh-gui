import PyInstaller.__main__  # type: ignore[import-untyped]


def build() -> None:
    args = [
        "src/ssh_gui/__init__.py",
        "--name=ssh-gui",
        "--onefile",
        "--noconsole",
        "--clean",
    ]
    PyInstaller.__main__.run(args)


if __name__ == "__main__":
    build()
