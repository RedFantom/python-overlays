"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2018 RedFantom

Set of tests for the available Overlay class. Tests functionality
including the addition of multiple labels, image loading and redrawing.
"""
# Standard Library
from unittest import TestCase
# Project Modules
from overlays import Overlay


class TestOverlay(TestCase):
    """Execute tests on the Overlay"""

    def setUp(self):
        """Setup an Overlay instance as an attribute"""
        self.w = Overlay((0, 0), (100, 100), "TestOverlay")

    def tearDown(self):
        """Destroy the open Overlay window"""
        self.w.destroy()

    def test_update(self):
        """Test whether the overlay can update correctly"""
        self.w.update()

    def test_add_label(self):
        """Test the addition of a Label and redrawing after that"""
        i = self.w.add_label(0, "Example Label", color=(255, 255, 255))
        self.w.update()
        self.w.remove_label(i)
        self.w.update()

    def test_rectangle(self):
        """Test the Rectangle property of the Overlay"""
        r = self.w.rectangle
        self.assertIsInstance(r, tuple)
        self.assertEqual(len(r), 4)
        self.assertEqual(r, (0, 0, 100, 100))
