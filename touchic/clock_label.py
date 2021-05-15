# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 17:20:01 2020

@author: Prosenjit

This displays a clock. The exposed attributes are

name: name of the parameter to be displayed
name_text_size: size of the text for displaying the name
name_color: color of the name text

value: value of the parameter to be displayed
value_text_size: size of the text for displaying the value
value_color: color of the value text

width: width hint of the text label for the layout manager
height: height hint of the text label for the layout manager

back_colors:
        back_color_light: light shade of color for the background
        back_color_dark: dark shade of color for the background
border_color: color of the border
"""

from .display_config import ICDisplayConfig
from PyQt5.QtCore import QTimer, pyqtSlot
from datetime import datetime
from .text_label import ICTextLabel


class ICClockLabel(ICTextLabel):
    def __init__(self, name: str, *args, **kwargs):
        super(ICClockLabel, self).__init__(name, "", *args, **kwargs)
        # configure the display
        self.value_text_size = ICDisplayConfig.ClockLabelSize
        self.value_text_color = ICDisplayConfig.ClockLabelColor
        # set the current time
        now = datetime.now()
        self.value = now.strftime('%H:%M:%S')
        # start the timer
        self._clock_timer = QTimer()
        self._clock_timer.timeout.connect(self.update_time)
        self._clock_timer.start(1000)

    @pyqtSlot()
    def update_time(self):
        now = datetime.now()
        self.value = now.strftime('%H:%M:%S')
