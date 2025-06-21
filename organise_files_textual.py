#!/usr/bin/env python3
"""
organise_files_textual.py
Terminal‑based GUI for the file organiser using Textual 3.x
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Button, DirectoryTree, Footer, Header, Input, Log, Static
from textual.screen import Screen
from textual.containers import VerticalScroll

from organise_files_core import organise  # ← your existing core logic
from pathlib import Path
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import DirectoryTree


class PathChosen(Message):
    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__()


class OrganiserApp(App):
    CSS = """
    Screen { layout: vertical; }
    #toolbar { height: 3; }
    #log { border: solid green; height: 1fr; }
    """

    BINDINGS = [("q", "quit", "Quit")]

    running: reactive[bool] = reactive(False)

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="toolbar"):
            self.path_input = Input(
                placeholder="Folder to organise (Enter to browse)", value="."
            )
            yield self.path_input
            yield Button("Browse…", id="browse")
            yield Button("Start", id="start", variant="success")
            yield Button("Clear", id="clear", variant="warning")
        with Vertical():
            self.log_widget = Log(id="log")
            yield self.log_widget
        yield Footer()

    # ────────────────────────────── UI EVENTS
    def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case "browse":
                self.push_screen(Browser(self.path_input.value))
            case "clear":
                self.log_widget.clear()
            case "start":
                self.run_organise()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.push_screen(Browser(event.value))

    def on_path_chosen(self, message: PathChosen) -> None:
        self.path_input.value = str(message.path)
        self.pop_screen()

    # ────────────────────────────── LOGGING & BACKGROUND
    def log_write(self, text: str) -> None:
        self.call_from_thread(self.log_widget.write_line, text.rstrip())

    def run_organise(self) -> None:
        if self.running:
            return
        folder = Path(self.path_input.value or ".").expanduser().resolve()
        if not folder.is_dir():
            self.log_widget.write_line(f"[ERROR] {folder} is not a directory.")
            return
        self.log_widget.write_line(f"▶ Organising: {folder}")
        self.running = True
        self.run_worker(self._worker, folder, name="organiser", group="organiser")

    def _worker(self, folder: Path) -> None:
        original_print = print

        def patched_print(*args, **kwargs):
            original_print(*args, **kwargs)
            self.log_write(" ".join(map(str, args)))

        try:
            sys.modules["builtins"].print = patched_print  # type: ignore
            organise(folder)
        finally:
            sys.modules["builtins"].print = original_print  # type: ignore
            self.running = False
            self.log_write("✓ Done.")

    def watch_running(self, running: bool) -> None:
        self.query_one("#start", Button).disabled = running


class Browser(Screen):
    """Directory picker with an explicit ‘Up’ button and key bindings."""

    # ── key bindings ──────────────────────────────────────────────────────────
    BINDINGS = [
        Binding("backspace", "go_up", "Parent"),
        Binding("u", "go_up", "Parent"),  # extra convenience
    ]

    def __init__(self, start: str):
        super().__init__()
        self.start_path = Path(start).expanduser().resolve()

    # ── compose UI ────────────────────────────────────────────────────────────
    def compose(self) -> ComposeResult:
        from textual.widgets import Static  # local import to keep header tidy

        yield Horizontal(  # toolbar row
            Button("↑ Up", id="btn_up"),
            Static(str(self.start_path), id="path_label", expand=True),
            id="browser_toolbar",
        )
        yield VerticalScroll(  # scrollable tree area
            DirectoryTree(self.start_path, id="tree"),
            id="tree_container",
        )

    # ── events ───────────────────────────────────────────────────────────────
    async def on_button_pressed(self, event: Button.Pressed) -> None:  # ← async
        if event.button.id == "btn_up":
            await self.go_up()  # ← await so the directory really changes

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        path = event.path
        self.post_message(PathChosen(path if path.is_dir() else path.parent))

    # ── actions and helpers ──────────────────────────────────────────────────
    async def action_go_up(self) -> None:
        """Backspace / ‘u’ key binding."""
        await self.go_up()

    async def go_up(self) -> None:
        """Shared logic for button and key binding."""
        tree: DirectoryTree = self.query_one("#tree", DirectoryTree)
        parent = tree.path.parent
        if parent == tree.path:  # filesystem root guard
            return
        tree.path = parent
        await tree.reload()
        self.query_one("#path_label", Static).update(str(parent))


if __name__ == "__main__":
    OrganiserApp().run()
