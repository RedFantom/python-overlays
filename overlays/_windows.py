"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2018 RedFantom

Provides a Win32 (through pywin32) based Overlay that supports a
transparent background, multi-line text and images.
"""
# Standard Library
import os
import random
import sys
from threading import Thread
import time
# Packages
from PIL import Image
import win32api as api
import win32con as con
import win32gui as gui
import win32ui as ui
# Project Modules
from ._overlay import Overlay


class WindowsOverlay(Overlay, Thread):
    """
    Create a Win32 based overlay

    Sources used for this class:
    - The pywin32 documentation
    - StackOverflow: <https://stackoverflow.com/questions/21840133>
    """

    DEFAULT_COLOR = (0, 0, 0)
    DEFAULT_FONT = ("Calibri", 12, False, False)

    def __init__(self, position: tuple, size: tuple,  name: str):
        """Initialize the libraries and attributes"""
        Overlay.__init__(self, position, size, name)
        Thread.__init__(self)
        self._position = position
        self._size = size

        self._h_instance = None
        self._class_name = name
        self._window_class = None
        self._window_class_atom = None
        self._ex_style = None
        self._style = None
        self._window_handle = None
        self._error = None
        self._window = None
        self.__init = False

        self._labels = dict()
        self._index = 0

        self._init_win32()
        self._init_style()
        self._init_window()
        self.start()

    def _init_win32(self):
        """Initialize the window and its attributes"""
        self._h_instance = api.GetModuleHandle()
        self._window_class = gui.WNDCLASS()
        self._window_class.style = con.CS_HREDRAW | con.CS_VREDRAW
        self._window_class.lpfnWndProc = self._draw
        self._window_class.hInstance = self._h_instance
        self._window_class.hCursor = gui.LoadCursor(None, con.IDC_ARROW)
        self._window_class.hbrBackground = gui.GetStockObject(con.WHITE_BRUSH)
        random.seed(time.time())
        rand = random.randint(0, sys.maxsize)
        self._window_class.lpszClassName = "{}_{}".format(self._window_class, rand)
        self._window_class_atom = gui.RegisterClass(self._window_class)

    def _init_style(self):
        """Initialize drawing style of the overlay"""
        self._ex_style = con.WS_EX_COMPOSITED | con.WS_EX_LAYERED | \
            con.WS_EX_NOACTIVATE | con.WS_EX_TOPMOST | con.WS_EX_TRANSPARENT
        self._style = con.WS_DISABLED | con.WS_POPUP | con.WS_VISIBLE

    def _init_window(self):
        """Initialize the actual window and show it"""
        self._window = gui.CreateWindowEx(
            self._ex_style,  # External style
            self._window_class_atom,  # Window class
            self._class_name,  # Window title
            self._style,  # Window style
            self._position[0],  # X coordinate
            self._position[1],  # y coordinate
            self._size[0],  # Width
            self._size[1],  # Height
            None,  # Parent window
            None,  # Menu
            self._h_instance,
            None  # lpParam
        )
        gui.SetLayeredWindowAttributes(self._window, 0x00ffffff, 0xff, con.LWA_COLORKEY | con.LWA_ALPHA)
        gui.UpdateWindow(self._window)
        gui.SetWindowPos(
            self._window,  # Window object
            con.HWND_TOPMOST,  # Topmost window handle
            self._position[0],  # x coordinate
            self._position[1],  # y coorinate
            0,  # width (resizes automatically)
            0,  # height (resizes automatically)
            con.SWP_NOACTIVATE | con.SWP_NOMOVE | con.SWP_NOSIZE | con.SWP_SHOWWINDOW
        )
        gui.ShowWindow(self._window, con.SW_SHOW)
        self.__init = True

    def _draw(self, window, message, w, l):
        """Callback for events on the window"""
        if message == con.WM_PAINT:
            return self._paint(window, message, w, l)
        elif message == con.WM_DESTROY:
            gui.PostQuitMessage(0)
            return 0
        else:
            return gui.DefWindowProc(window, message, w, l)

    def _paint(self, window, message, w, l):
        """Draw the Labels on the Windows surface"""
        try:
            if not self.__init:
                return
            handle, paint = gui.BeginPaint(window)
            r = self.rectangle
            y, w, h = 0, r[2] - r[0], r[3] - r[1]
            for _, (text, image, color, font) in sorted(self._labels.copy().items(), key=lambda k: k[0]):
                x = 0
                if image is not None:
                    x = self._draw_image(handle, paint, (0, y, w, h - y), image)
                box = (x, y, w, h - y)
                _y, _ = self._draw_text(handle, box, text, color, font)
                y += _y
            gui.EndPaint(window, paint)
            return 0
        except Exception as e:
            self._error = e
            return -1

    def _draw_text(self, handle: int, box: tuple, text: str, color: tuple, font: (dict, tuple)) -> tuple:
        """Draw text in the given location"""
        font = self._build_font(font, self._get_dpi_scale(handle))
        gui.SelectObject(handle, font)
        gui.SetTextColor(handle, self._color(color))
        return gui.DrawText(handle, text, -1, box, con.DT_NOCLIP | con.DT_LEFT | con.DT_SINGLELINE | con.DT_TOP)

    def _build_font(self, font: (dict, tuple), dpi_scale: float)->int:
        """Build a font from the given font options"""
        family, size, bold, italics = self._font_dict_to_tuple(font)
        font = gui.LOGFONT()
        if family != "default":
            font.lfFaceName = family
        font.lfHeight = int(round(dpi_scale * size))
        font.lfQuality = con.NONANTIALIASED_QUALITY
        font.lfWeight = 900 if bold else 400
        font.lfItalic = italics
        return gui.CreateFontIndirect(font)

    def _draw_image(self, handle: int, paint, box: tuple, image: Image.Image) -> int:
        """Draw an image in the overlay at the specified location"""
        pixels = image.convert("RGBA").load()
        w, h = image.size
        l, t, r, b = box
        for x in range(w):
            for y in range(h):
                _x, _y = l + x, t + y
                c = pixels[x, y]
                if c[3] == 0:
                    c = (255, 255, 255)
                else:
                    c = c[:3]
                # print("{} -> {:08x}".format(pixels[x, y], c))
                _c = gui.SetPixel(handle, _x, _y, self._color(c))
                # if _c != c:
                #     print("Requested: {}, Set: {}".format(c, _c))
                # break
        return w

    def update(self):
        """Update the window"""
        if self.__init is False:
            raise RuntimeError("Window is not initialized")
        if self._error is not None:
            self.destroy()
            self.__init = False
            raise Exception from self._error
        gui.UpdateWindow(self._window)
        gui.SetWindowPos(self._window, None, self._position[0], self._position[1], 0, 0, con.SWP_NOSIZE)
        gui.SetLayeredWindowAttributes(self._window, 0x00ffffff, 0xff, con.LWA_COLORKEY | con.LWA_ALPHA)
        gui.RedrawWindow(self._window, None, None, con.RDW_INVALIDATE | con.RDW_ERASE)
        gui.PumpWaitingMessages()

    def run(self):
        """Run the loop to update the window"""
        while True:
            try:
                self.update()
            except RuntimeError as e:
                if e.args == ("Window is not initialized",):
                    break
                raise

    def add_label(
            self, row: int, text: str, image: str = None,
            color: tuple = DEFAULT_COLOR, font: (dict, tuple) = DEFAULT_FONT) -> (str, None):
        """Create a new label in the Labels dictionary to be drawn"""
        if image is not None:
            image = self._open_image(image)
        self._labels[row] = (text, image, color, font)
        return str(row)

    def remove_label(self, ident: str):
        """Remove a Label from the Labels dictionary"""
        del self._labels[int(ident)]

    @property
    def rectangle(self):
        """Return the rectangle the overlay occupies"""
        if self.__init is False:
            raise RuntimeError("Window is not initialized")
        return gui.GetClientRect(self._window)

    def destroy(self):
        """Destroy this WindowsOverlay"""
        return gui.SendMessage(self._window, con.WM_CLOSE, None, None)

    @staticmethod
    def _open_image(file: str) -> Image:
        """Load an image from a file"""
        if not os.path.exists(file):
            raise FileNotFoundError("Image file does not exist")
        """
        if not file.endswith(".bmp"):
            path = os.path.join(tempfile.gettempdir(), os.path.basename(file[:-4] + ".bmp"))
            img = Image.open(file)
            img.save(path)
        else:
            path = file
            img = Image.open(path)
        image = gui.LoadImage(0, path, con.IMAGE_BITMAP, 0, 0, con.LR_LOADFROMFILE | con.LR_LOADFROMFILE)
        return (image,) + img.size
        """
        return Image.open(file)

    @staticmethod
    def _get_dpi_scale(handle: int) -> float:
        """Return the DPI scaling factor"""
        return ui.GetDeviceCaps(handle, con.LOGPIXELSX) / 60.0

    @staticmethod
    def _color(color: tuple) -> int:
        if len(color) == 3:
            return eval("0x{2:02x}{1:02x}{0:02x}".format(*color))
        return eval("0x{3:02x}{2:02x}{1:02x}{0:02x}".format(*color))
