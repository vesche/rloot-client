#!/usr/local/bin/env python3

import os
import json
import threading
import subprocess

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer


class UeberzugImageDisplayer:
    """
    Source: https://github.com/ranger/ranger/blob/c8d21c6a9e33aacf936c52e8f400bd909b043e1a/ranger/ext/img_display.py#L730

    Implementation of ImageDisplayer using ueberzug.
    Ueberzug can display images in a Xorg session.
    Does not work over SSH.
    """
    IMAGE_ID = 'preview'
    is_initialized = False
    working_dir = os.environ.get('XDG_RUNTIME_DIR', os.path.expanduser("~") or None)

    def __init__(self):
        self.process = None

    def initialize(self):
        """start ueberzug"""
        if (self.is_initialized and self.process.poll() is None
                and not self.process.stdin.closed):
            return

        # We cannot close the process because that stops the preview.
        # pylint: disable=consider-using-with
        self.process = subprocess.Popen(['ueberzug', 'layer', '--silent'], cwd=self.working_dir,
                             stdin=subprocess.PIPE, universal_newlines=True)
        self.is_initialized = True

    def _execute(self, **kwargs):
        self.initialize()
        self.process.stdin.write(json.dumps(kwargs) + '\n')
        self.process.stdin.flush()

    def draw(self, path, start_x, start_y, width, height):
        self._execute(
            action='add',
            identifier=self.IMAGE_ID,
            x=start_x,
            y=start_y,
            max_width=width,
            max_height=height,
            path=path
        )

    def clear(self, start_x, start_y, width, height):
        if self.process and not self.process.stdin.closed:
            self._execute(action='remove', identifier=self.IMAGE_ID)

    def quit(self):
        if self.is_initialized and self.process.poll() is None:
            timer_kill = threading.Timer(1, self.process.kill, [])
            try:
                self.process.terminate()
                timer_kill.start()
                self.process.communicate()
            finally:
                timer_kill.cancel()


class Client(App):
    """A Textual app to manage stopwatches."""

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

        max_x, max_y = os.get_terminal_size()

        for x in range(0, max_x, 30):
            u_img.draw("/home/vesche/rloot/rloot-client/test_images/lost_poster.jpg", x, 0, 30, 30)
            import time
            time.sleep(1)

    
if __name__ == "__main__":
    u_img = UeberzugImageDisplayer()
    u_img.initialize()
    app = Client()
    app.run()
    u_img.quit()
