#!/usr/bin/env python
from kivy.graphics.vertex_instructions import Rectangle

__author__ = 'Tomas Novacik'


import numpy
import random
import string
import re

from kivy.uix.label import Label


RGBA_SIZE = 4


def shuffle(vals):
    """random.shuffle does not return values -> this returns inplace shuffled
    list"""
    random.shuffle(vals)
    return vals

class Shapes(object):
    """Shape factory"""

    TYPES = {}
    MAX_SHAPES = 9

    DEFAULT_SHAPE = "basic_numeric"

    REGEX_CAMEL_CASE = re.compile(r'[A-Z][a-z]+')

    @staticmethod
    def split_camel_case(name):
        """Split camel case string to separate parts: CamelCase -> [Camel, Case]
        """
        s1 = Shapes.REGEX_CAMEL_CASE.findall(name)
        return s1

    @classmethod
    def get(cls, shape_name=DEFAULT_SHAPE):
        """Factory method -> return appropriate class representing give class"""
        if shape_name not in cls.TYPES:
            raise ValueError("Shape class %s does not exist." % shape_name)
        return cls.TYPES[shape_name]

    @classmethod
    def register(cls, subclass):
        """Registration decorator FIX ME -> should be based on subclasses,
        class names are saved in TYPES, class CamelCaseShape will be saved under
        in following format TYPES={'camel_case': <cls CamelCaseShape>}"""
        cls_name = "_".join(Shapes.split_camel_case(subclass.__name__)[:-1])
        cls_name = cls_name.lower()

        if cls_name in cls.TYPES:
            raise ValueError("Shape subclass %s already exists" % cls_name)
        cls.TYPES[cls_name] = subclass
        return subclass


DEFAULT_NOISE_LEVEL = 0

class BaseLabelShape(Label, Shapes):
    SHAPE_COLOR = [255, 255, 255]
    BACKGROUND_COLOR = [0, 0, 0]
    PADDING = 30
    FONT_SIZE = '3cm'
    MAX_NUM = 10
    SHAPES = None # must be changed by subclass

    def __init__(self, noise_level=DEFAULT_NOISE_LEVEL):

        super(BaseLabelShape, self).__init__(font_size = self.FONT_SIZE)
        self.shape_box = None
        self.noise_level = noise_level

    def reposition_shape_box(self, *largs):
        self.shape_box.pos = self.pos

    def resize_shape_box(self, *largs):
        self.shape_box.size = self.size

    def _convert_shape(self, shape_index):
        """Convert shape to text"""
        return self.SHAPES[shape_index]

    def _apply_noise(self):
        self._label.refresh()
        self.texture_buffer = numpy.fromstring(self._label.texture.pixels,
                                           dtype=numpy.uint8)
        alphas = self.texture_buffer[RGBA_SIZE - 1::RGBA_SIZE]
        for index, item in enumerate(alphas):
            if item != 0 and random.random() < self.noise_level:
                self.texture_buffer[(index + 1) * RGBA_SIZE - 1] = 0

        self._label.texture.blit_buffer(self.texture_buffer,
                                        colorfmt='rgba',
                                        bufferfmt='ubyte')
        if not self.shape_box:
            with self.canvas:
                self.shape_box = Rectangle(size=self.size, pos=self.pos,
                                           texture=self._label.texture)
            self.bind(pos=self.reposition_shape_box,
                      size=self.resize_shape_box)
        center_x = self.center_x - self._label.texture.size[0] / 2
        center_y = self.center_y - self._label.texture.size[1] / 2
        self.shape_box.pos = (center_x, center_y)
        self.shape_box.size = self._label.texture.size
        self.shape_box.texture = self._label.texture
        self.text = ""

    def set_shape(self, shape_index):
        self.text = self._convert_shape(shape_index)
        if self.noise_level:
            self._apply_noise()

    def clear(self):
        if self.noise_level:
            self.texture_buffer.fill(0)
            self._label.texture.blit_buffer(self.texture_buffer,
                                            colorfmt='rgba',
                                            bufferfmt='ubyte')
            self.shape_box.texture = self._label.texture
        else:
            self.text = ""


@Shapes.register
class BasicNumericShape(BaseLabelShape):
    """Random numbers between 1-9 are picked as shapes"""
    MAX_NUM = 10
    MIN_NUM = 1
    SHAPES = shuffle(map(str, range(MIN_NUM, MAX_NUM)))[:Shapes.MAX_SHAPES]


@Shapes.register
class BasicCharacterShape(BaseLabelShape):
    """Random characters a-Z are picked as shapes"""
    SHAPES = shuffle(list(string.uppercase))[:Shapes.MAX_SHAPES]


@Shapes.register
class NumericShape(BaseLabelShape):
    """Random numbers between 100-999 are picked as shapes"""
    MIN_NUM = 100
    MAX_NUM = 999
    SHAPES = shuffle(map(str, range(MIN_NUM, MAX_NUM)))[:Shapes.MAX_SHAPES]

@Shapes.register
class WordShape(BaseLabelShape):
    WORDS = ["hi", "car", "bed", "dog", "cat", "hello", "juny", "july", "cow",
             "pig", "right", "mug", "left", "lip", "map", "bat", "bet"]
    SHAPES = shuffle(WORDS)[:Shapes.MAX_SHAPES]

# eof