import json
import time
import typing as T

from contextlib import suppress
from fabric import Connection
from os.path import exists
from pyrsistent import PClass, PMap, PSet, PVector, m, v, field, freeze, thaw
from threading import Thread
from tkinter import Label, StringVar, Tk, messagebox
from tkinter.ttk import Button, Entry, Frame, Progressbar


class Installer(Frame):
    def __init__(self, app: Frame, *a, **kw) -> None:
        super().__init__()

        self._parent = app

        _: Label = Label(app, textvariable=StringVar(app, "INSTALLER"))
        _.grid(column=0, row=0)

        exitcode: int = int(
            self._parent.c.run("which docker > /dev/null;echo $?").stdout
        )

        if 0 < exitcode:
            messagebox.showwarning(
                "Failed", "Docker not found on target, please install docker"
            )
            return

        exitcode = int(self._parent.c.run(f"which wget > /dev/null;echo $?").stdout)

        if 0 < exitcode:
            messagebox.showwarning(
                "Failed",
                "Wget not found on target, please install Wget",
            )

        self.progress: Progressbar = Progressbar(
            app, orient="horizontal", mode="determinate", length=280
        )
        self.progress.grid(column=0, row=1, padx=10, pady=20)
        self.progress.start()

        thread = Thread(target=self.install)
        thread.start()

    def install(self) -> None:
        # pull
        result: str = ""
        try:
            self._parent.c.run("mkdir -p /tmp/opt/cardcraft")

            result = self._parent.c.run(
                f"cd /tmp; curl -s -LO 'https://github.com/licinaluka/cardcraft/releases/download/untagged-5143a0686219ab247129/cardcraft-web-amd64'; mv cardcraft-web-amd64 /tmp/opt/cardcraft/cardcraft-web-amd64"
            ).stdout
            self.progress["value"] = 50

            result = self._parent.c.run(
                f"cd /tmp; curl -s -LO 'https://github.com/licinaluka/cardcraft/releases/download/untagged-5143a0686219ab247129/cardcraft-engine.tar'; sleep 1; tar -xf cardcraft-engine.tar -C /tmp/opt/cardcraft 2>&1"
            ).stdout

            self.progress["value"] = 100
        except Exception as ex:
            messagebox.showwarning("Failed", result or str(ex))

        # start
        result = ""
        try:
            result = self._parent.c.run(
                "cd /tmp/opt/cardcraft; chmod +x cardcraft-web-amd64; ./cardcraft-web-amd64 > /tmp/cardcraft-web.log 2>&1 & echo $! > .pid"
            ).stdout
        except Exception as ex:
            messagebox.showwarning("Failed", result or str(ex))

        try:
            result = self._parent.c.run(
                "cd /tmp/opt/cardcraft/cardcraft-engine; .venv/bin/python3 main.py > /tmp/cardcraft-engine.og 2>&1 & echo $! > .pid"
            ).stdout
        except Exception as ex:
            messagebox.showwarning("Failed", result or str(ex))

        self.progress.stop()


class ControlPanel(Frame):
    def __init__(self, app: Frame, *a, **kw) -> None:
        super().__init__()

        self._parent = app

        _: Label = Label(app, textvariable=StringVar(app, "CONTROL PANEL"))
        _.grid(column=0, row=0)


class Main(Frame):
    def __init__(self, app: Frame, *a, **kw) -> None:
        super().__init__()

        self._parent = app

        _target = _user = ""

        if exists("/tmp/cardcraftsetup.json"):
            with suppress(Exception), open("/tmp/cardcraftsetup.json", "r") as f:
                _ = json.loads(f.read())
                _target = _.get("target", "")
                _user = _.get("user", "")

        self._target = StringVar(app, _target)
        self._user = StringVar(app, _user)
        self._pwd = StringVar(app, "")
        self._pairpath = StringVar(app, "")

        _: Label = Label(app, textvariable=StringVar(app, "Target: "))
        _.grid(column=0, row=0)
        target: Entry = Entry(app, textvariable=self._target)
        target.grid(column=1, row=0)

        _: Label = Label(app, textvariable=StringVar(app, "User: "))
        _.grid(column=0, row=1)
        user: Entry = Entry(app, textvariable=self._user)
        user.grid(column=1, row=1)

        _: Label = Label(app, textvariable=StringVar(app, "Password: "))
        _.grid(column=0, row=2)
        pwd: Entry = Entry(app, show="*", textvariable=self._pwd)
        pwd.grid(column=1, row=2)

        _: Label = Label(app, textvariable=StringVar(app, "Path to keypair"))
        _.grid(column=0, row=3)
        pair: Entry = Entry(app, textvariable=self._pairpath)
        pair.grid(column=1, row=3)

        b: Button = Button(app, text="Next", command=self.exists)
        b.grid(column=1, row=4)

    def exists(self) -> None:
        args = {}

        assert self._target.get()
        assert self._user.get()

        with open("/tmp/cardcraftsetup.json", "w") as f:
            f.write(
                json.dumps({"target": self._target.get(), "user": self._user.get()})
            )

        if self._pairpath.get():
            args["key_filename"] = self._pairpath

        if self._pwd.get():
            args["password"] = self._pwd.get()

        try:
            self._parent.c = Connection(
                self._target.get(), user=self._user.get(), connect_kwargs=args
            )
            exitcode: int = int(
                self._parent.c.run("test -e /opt/cardcraft;echo $?").stdout
            )
        except Exception as ex:
            messagebox.showwarning("Failed!", f"{ex}")
            return

        if 0 == exitcode:
            print("Installed!")
            self._parent.screen = ControlPanel
            self._parent.load()
            return

        print("Not installed!")
        self._parent.screen = Installer
        self._parent.load()


class AppState(PClass):
    size: T.Tuple[int, int] = field(type=tuple)


class Cardcraft(Frame):
    state: AppState = AppState(size=(640, 480))
    c: T.Optional[Connection] = None

    def __init__(self, w: Tk, *a, **kw) -> None:
        super().__init__()

        self.w = self.window = w
        self.w.title("Cardcraft setup")

        width, height = self.state.size
        self.w.geometry(f"{width}x{height}")

        self.screen = Main

    def load(self) -> None:
        for _ in self.winfo_children():
            _.destroy()

        screen: Frame = self.screen(self)
        screen.tkraise()
        self.pack()


if __name__ == "__main__":

    w = Tk()
    app = Cardcraft(w)
    app.load()
    w.mainloop()
