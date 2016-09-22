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

    RANDOM_TYPE_STR = "auto_random"

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
        """Factory method -> return appropriate class representing given
        shape"""
        if shape_name == cls.RANDOM_TYPE_STR:
            return random.choice(cls.TYPES.values())

        elif shape_name not in cls.TYPES:
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
    SHAPES = None  # must be changed by subclass
    PIXEL_MAX = 255
    PIXEL_MIN = 0

    def __init__(self, noise_level=DEFAULT_NOISE_LEVEL):

        super(BaseLabelShape, self).__init__(font_size=self.FONT_SIZE)
        self.shape_box = None
        self._init_visibility = 1 - noise_level
        self._shape_visibility = 1
        # when applying noise -> here are pixels that should be normally visible
        # but are not and pixels that should be visible and really are visible
        # this information is used to handle visibility of the shape,
        # only alphas are being modified
        self._invisible_pixels = []
        self._visible_pixels = []

    def reposition_shape_box(self, *largs):
        self.shape_box.pos = self.pos

    def resize_shape_box(self, *largs):
        self.shape_box.size = self.size

    @property
    def shape_visibility(self):
        """Returns visibility of the displayed shape - 1 <= visibility <= 0."""
        return self._shape_visibility

    @shape_visibility.setter
    def shape_visibility(self, visibility):
        if visibility > 1 or visibility < 0:
            raise ValueError("Visibility can be set only in the interval"
                             " between 0 and 1.")

        # do nothing if the visibility level is the same
        if visibility == self._shape_visibility:
            return

        # handle specifically two special cases - when the visibility
        # should be zero and 1 -> just to make it faster
        if visibility == 0:
            for index in self._visible_pixels:
                self.texture_buffer[index] = self.PIXEL_MIN
            self._invisible_pixels.extend(self._visible_pixels)
            self._visible_pixels = []
        elif visibility == 1:
            for index in self._invisible_pixels:
                self.texture_buffer[index] = self.PIXEL_MAX
            self._visible_pixels.extend(self._invisible_pixels)
            self._invisible_pixels = []
        else:
            # compute how many pixels should be [in]visible on given
            # visibility level
            pix_count = len(self._invisible_pixels)\
                        + len(self._visible_pixels)
            visible_diff = int(visibility * pix_count) -\
                           len(self._visible_pixels)

            if visible_diff > 0:
                # we are going to make some pixels visible
                for i in xrange(visible_diff):
                    p_index = self._invisible_pixels.pop()
                    self.texture_buffer[p_index] = self.PIXEL_MAX
                    self._visible_pixels.append(p_index)
            else:
                # we are going to make some pixels invisible
                for i in xrange(visible_diff * -1):
                    p_index = self._visible_pixels.pop()
                    self.texture_buffer[p_index] = self.PIXEL_MIN
                    self._invisible_pixels.append(p_index)

        self._label.texture.blit_buffer(self.texture_buffer,
                                            colorfmt='rgba',
                                            bufferfmt='ubyte')

        self.shape_box.texture = self._label.texture
        self._shape_visibility = visibility

    def _convert_shape(self, shape_index):
        """Convert shape to text"""
        return self.SHAPES[shape_index]

    def set_shape(self, shape_index):
        self.text = self._convert_shape(shape_index)
        self._label.refresh()
        self.texture_buffer = numpy.fromstring(self._label.texture.pixels,
                                               dtype=numpy.uint8)
        alphas = self.texture_buffer[RGBA_SIZE - 1::RGBA_SIZE]
        # reset [in]visible pixels buffers
        self._invisible_pixels = []
        self._visible_pixels = []
        for index, item in enumerate(alphas):
            if item != 0:
                r_index = (index + 1) * RGBA_SIZE - 1
                self._visible_pixels.append(r_index)
        # shuffle the indexes so manipulation with visibility seems random
        random.shuffle(self._visible_pixels)
        if not self.shape_box:
            with self.canvas:
                self.shape_box = Rectangle(size=self.size, pos=self.pos,
                                           texture=self._label.texture)
            self.bind(pos=self.reposition_shape_box,
                      size=self.resize_shape_box)
        center_x = self.center_x - self._label.texture.size[0] / 2
        center_y = self.center_y - self._label.texture.size[1] / 2
        self.shape_visibility = self._init_visibility
        self.shape_box.pos = (center_x, center_y)
        self.shape_box.size = self._label.texture.size
        self.text = ""

    def clear(self):
        self.shape_visibility = 0


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
    WORDS = ["hi", "car", "bed", "dog", "cat", "hello", "june", "july", "cow",
             "pig", "right", "mug", "left", "lip", "map", "bat", "bet", "leg"]
    SHAPES = shuffle(WORDS)[:Shapes.MAX_SHAPES]

# eof
