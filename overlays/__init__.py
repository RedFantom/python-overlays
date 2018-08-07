"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2018 RedFantom
"""
from ._overlay import Overlay
from ._tkinter import TkinterOverlay

OVERLAYS = [
    ("overlays._windows", "WindowsOverlay"),
    ("overlays._gtk", "GtkOverlay")
]

for overlay in OVERLAYS:
    try:
        exec("from {} import {} as Overlay".format(*overlay))
    except ImportError as e:
        continue
if "Overlay" not in locals():
    raise ImportError("Could not import any Overlay implementation")
