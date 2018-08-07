"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2018 RedFantom

Gtk-based overlay that provides a transparent, decoration-less (on most
window managers) and topmost (on most window managers) window that can
show labels (each occupying a single row) with images.
"""
# Standard Library
import os
from threading import Thread
# Packages
import cairo
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk  # python3-gi
# Project Modules
from ._overlay import Overlay


class GtkOverlay(Gtk.Window, Thread, Overlay):
    """
    Gtk.Window that represents the actual Overlay and draws the text

    Thread that runs Gtk.main to show the Gtk.Window

    Implements the Overlay interface
    """

    DEFAULT_COLOR = (0, 0, 0)
    DEFAULT_FONT = ("normal", 11, False, False)

    _INSTANCES = list()
    _GTK_MAIN = None

    def __init__(self, position: tuple, size: tuple, name: str):
        """Initialize window and attributes"""
        Gtk.Window.__init__(self)
        Thread.__init__(self)

        self._position = position
        self._size = size
        self._name = name

        self.move(*position)
        self.set_border_width(0)

        # Initialize Label
        self._labels = dict()
        self._vbox = Gtk.VBox()
        self.add(self._vbox)
        self._init_window()
        self.start()

    def _init_window(self):
        """Initialize Window attributes"""
        # Initialize Transparency Handler
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual is not None and screen.is_composited():
            self.set_visual(visual)
        # Initialize other attributes
        self.set_app_paintable(True)
        self.set_resizable(False)
        self.connect("draw", self._redraw)
        self.connect("destroy", Gtk.main_quit)
        self.set_keep_above(True)
        self.set_decorated(False)
        self.show_all()

    def add_label(
            self, row: int, text: str, image: str = None,
            color: tuple = DEFAULT_COLOR, font: (dict, tuple) = DEFAULT_FONT) -> (str, None):
        """Create a new Label for the specified row"""
        hbox = Gtk.HBox()

        if image is not None:
            if not os.path.exists(image):
                raise FileNotFoundError("Image file does not exist")
            image = Gtk.Image.new_from_file(image)
            hbox.add(image)

        label = Gtk.Label()
        label.set_use_markup(True)
        label.set_markup(self._format_text(text, color, font))
        label.set_justify(Gtk.Justification.LEFT)
        hbox.add(label)

        self._vbox.add(hbox)
        self._vbox.reorder_child(hbox, row)
        self.show_all()

        self._labels[row] = (label, image, hbox)
        return str(row)

    def remove_label(self, ident: str) -> None:
        """Remove a Label from the VBox"""
        _, _, hbox = self._labels[ident]
        self._vbox.remove(hbox)
        hbox.do_destroy()  # Releases Child references
        del self._labels[ident]

    def destroy(self):
        """Destroy the Overlay window and stop the Thread"""
        Gtk.Window.destroy(self)

    def update(self):
        """Update the state of the window"""
        Gtk.Window.update(self)

    def start(self):
        """Check if it is safe to start the Thread before starting it"""
        if self._GTK_MAIN is not None:
            return
        Thread.start(self)

    def run(self):
        """Run the Gtk event loop"""
        self._INSTANCES.append(self)
        if Gtk.main_level() != 0:
            return
        self._GTK_MAIN = self
        Gtk.main()
        self._GTK_MAIN = None
        self._INSTANCES.remove(self)
        if len(self._INSTANCES) > 0:
            self._INSTANCES[0].start()

    @property
    def rectangle(self):
        return (0, 0, 0, 0)

    @staticmethod
    def _redraw(_: Gtk.Widget, cr):
        """Redraw this window with transparency"""
        cr.set_source_rgba(0, 0, 0, 0)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)

    @staticmethod
    def _format_text(text: str, color: tuple, font: (tuple, dict)) -> str:
        """Format the text in a markup string for Gtk Label"""
        font = GtkOverlay._process_font(font)
        span = "<span face=\"{0}\" size=\"{1}\" weight=\"{2}\" style=\"{3}\" color=\"{4}\">". \
            format(*font, Overlay._color_tuple_to_hex(color)) + "{}</span>"
        return span.format(text)

    @staticmethod
    def _process_font(font: (tuple, dict)) -> tuple:
        """Process a font tuple or dictionary into a compatible tuple"""
        if isinstance(font, dict):
            font = Overlay._font_dict_to_tuple(font)
        face, size, bold, italics = font
        bold = "bold" if bold is True else "normal"
        italics = "italic" if italics is True else "normal"
        return face, size, bold, italics
