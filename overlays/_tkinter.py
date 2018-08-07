"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2018 RedFantom
"""
# Standard Library
from threading import Thread
# Packages
from PIL import Image, ImageTk
import tkinter as tk
# Project Modules
from ._overlay import Overlay


class TkinterOverlay(tk.Tk, tk.Toplevel, Thread, Overlay):
    """
    Tkinter window based overlay that can be used as Toplevel or Tk

    If the Overlay is created without a master Tk instance, the
    Overlay will represent a Tk window with its own Tk/Tcl interpreter.
    If the Overlay is created with a master Tk instance, the
    Overlay will represent a Toplevel window that depends on the master
    Tk/Tcl interpreter to run.

    In the first case, the mainloop of the window is run in a separate
    thread.

    :param master: master tk.Tk instance if used in a Tkinter program
    :param background: Background colour of the Overlay if transparency
        is not supported on the platform.
    """

    DEFAULT_COLOR = (0, 0, 0)
    DEFAULT_FONT = ("default", 11, False, False)

    def __init__(self, position: tuple, size: tuple, name: str, master: tk.Tk = None, background: str = "darkblue"):
        """Initialize the window with the appropriate parent classes"""
        Overlay.__init__(self, position, size, name)
        self._bg = background
        self._size, self._position, self._name = size, position, name

        if master is not None:
            tk.Toplevel.__init__(self, master)
            self._parent = tk.Toplevel
        else:
            Thread.__init__(self)
            self._parent = tk.Tk
            self.start()

        self._labels = dict()

    def _init_window(self):
        """Apply special Overlay attributes"""
        self._update_geometry()
        self.wm_title(self._name)
        self.wm_attributes("-topmost", True)
        self.wm_overrideredirect(True)
        self._parent.config(self, background=self._bg)
        try:
            self.wm_attributes("-transparentcolor", "darkblue")
        except tk.TclError:
            self.wm_attributes("-alpha", 0.75)

    def _update_geometry(self):
        """Update the geometry of the window"""
        self.wm_geometry("{}x{}+{}+{}".format(*self._size, *self._position))

    def add_label(
            self, row: int, text: str, image: str = None,
            color: tuple = DEFAULT_COLOR, font: (dict, tuple) = DEFAULT_FONT) -> (str, None):
        """Create a new tk.Label to insert into the Overlay"""
        if image is not None:
            image = ImageTk.PhotoImage(Image.open(image), master=self)
        font = self._process_font(font)
        color = self._color_tuple_to_hex(color)
        self._labels[row] = tk.Label(
            self, text=text, image=image, compound=tk.LEFT,
            foreground=color, font=font, background=self._bg)
        self._labels[row].grid(row=row, column=0, sticky="nsw", padx=5, pady=(0, 5))
        return str(row)

    def remove_label(self, ident: str) -> None:
        """Remove a Label from the grid"""
        row = int(ident)
        self._labels[row].grid_forget()
        del self._labels[row]

    def update(self):
        """Not required for TkinterOverlay"""
        pass

    def run(self):
        """Run the Tkinter mainloop if required"""
        if self._parent is tk.Toplevel:
            return
        tk.Tk.__init__(self)
        self._init_window()
        tk.Tk.mainloop(self)

    @property
    def rectangle(self) -> tuple:
        """Return the box rectangle the Overlay occupies"""
        geometry = self.wm_geometry()
        size, x, y = geometry.split("+")
        w, h = size.split("x")
        x, y, w, h = map(int, (x, y, w, h))
        return x, y, x + w, y + h

    @staticmethod
    def _process_font(font: (dict, tuple)):
        """Process a font dictionary or tuple into a Tkinter font tuple"""
        if isinstance(font, dict):
            font = Overlay._font_dict_to_tuple(font)
        family, size, bold, italics = font
        font = (family, size)
        if bold is True:
            font += ("bold",)
        if italics is True:
            font += ("italic",)
        return font
