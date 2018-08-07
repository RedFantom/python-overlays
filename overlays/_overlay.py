"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2018 RedFantom

Provides the abstract class the Overlay interface is based upon
"""


class Overlay(object):
    """Abstract class specifying Overlay interface"""

    def __init__(self, position: tuple, size: tuple, name: str):
        """Initialize the transparent overlay at given position"""
        assert isinstance(position, tuple) and len(position) == 2
        assert isinstance(size, tuple) and len(size) == 2
        assert isinstance(name, str)

    def destroy(self):
        """Destroy the open Overlay"""
        raise NotImplementedError()

    def add_label(
            self, row: int, text: str, image: str = None,
            color: tuple = None, font: (dict, tuple) = None) -> (str, None):
        """Create a new label in the grid with the specifications"""
        raise NotImplementedError()

    def remove_label(self, ident: str) -> None:
        """Remove a label from the grid with the identifier"""
        raise NotImplementedError()

    def update(self):
        """Update the window state"""
        raise NotImplementedError()

    @property
    def rectangle(self)->tuple:
        """Return the box rectangle the overlay occupies"""
        raise NotImplementedError()

    @staticmethod
    def _font_dict_to_tuple(font: dict):
        """Build a font tuple from a font dictionary"""
        if isinstance(font, tuple):
            if len(font) == 2:
                return font + (False, False)
            elif len(font) == 3:
                return font + (False,)
            return font
        font_t = (font.pop("family"), font.pop("size"))
        if "bold" in font and font["bold"] is True:
            font_t += (True,)
        if "italic" in font and font["italic"] is True:
            font_t += (True,) if len(font_t) == 3 else (False, True)
        return font_t

    @staticmethod
    def _color_tuple_to_hex(color: tuple) -> str:
        """Format a color tuple as a hex color code"""
        return "#{:02x}{:02x}{:02x}".format(*color)
