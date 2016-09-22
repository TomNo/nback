#!/usr/bin/env python
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

from basic_screen import BasicScreen

__author__ = 'Tomas Novacik'


class TextLabel(Label):
    """Wraps long text."""
    pass


class AboutScreen(BasicScreen):
    TEXT = ("The n-back task is a continuous performance task that is commonly"
            " used as an assessment in cognitive neuroscience to measure a "
            "part of working memory and working memory capacity. The n-back was"
            " introduced by Wayne Kirchner in 1958.\n"
            "The subject is presented with a sequence of stimuli, and the task "
            "consists of indicating when the current stimulus matches the one "
            "from n steps earlier in the sequence. The load factor 'n' can be "
            "adjusted to make the task more or less difficult. [Wiki]\n\n"
            "Most interesting questions are answered on the following website "
            "https://www.gwern.net/DNB%20FAQ.\n\n"
            "There are many different implementation of this exercise"
            " available. I started this project to try several ideas of my own."
            "First idea - noisy shapes - this idea is based on the premise"
            " that brain focuses far more on noisy/blurry images thus one"
            " session should have greater impact on your brain activity."
            " You should learn faster.\n\n"
            "Second idea is based on the positive/negative response from "
            "playing - assuming that the more spectacular evaluation response"
            " is given the better should be the overall performance. \n\n"
            "None of this ideas are scientifically justifiable - "
            "basically just experiments - final goal of this application "
            "should "
            "be statistical analysis of gathered data.\n\n"
            "My tips on playing -  no rehearsing, picture previous items in"
            " your head - it should be as effortless as possible, no strategies"
            " for different levels.\n\n"
            "My reason is following - you are trying to"
            " improve your efficiency in real life - you never now which 'n' "
            "you are going to need and when you are going to need it, your"
            " brain should do this exercise ideally all the time in "
            "the background so you can access data from relatively short past."
            )
    PADDING = (40, 20)
    TEXT_FONT_SIZE = "0.5cm"

    def on_enter(self):
        scroll_view = ScrollView()
        info_label = TextLabel(text=self.TEXT, font_size=self.TEXT_FONT_SIZE,
                               padding=self.PADDING)
        scroll_view.add_widget(info_label)
        self.add_widget(scroll_view)

    def on_exit(self):
        self.clear_widgets()

# eof
