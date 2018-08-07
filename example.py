"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2018 RedFantom

Example showing off the available Overlay for the platform. Creates
multiple different overlays, each with different properties.
"""
from overlays import Overlay


w1 = Overlay((0, 0), (100, 100), "Overlay1")
w2 = Overlay((0, 100), (100, 100), "Overlay2")
w1.add_label(0, "Example Overlay 1", color=(255, 0, 0))
w1.add_label(1, "Second Label", color=(255, 0, 255))
w2.add_label(0, "Example Overlay 2", color=(0, 255, 255), font=("default", 14, True, True))
w2.add_label(1, "Second Label", image="tests/image.png")

try:
    import time
    time.sleep(30)
    raise KeyboardInterrupt()
except KeyboardInterrupt:
    w1.destroy()
    w2.destroy()
exit(0)
