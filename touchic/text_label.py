# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 17:20:01 2020

@author: Prosenjit

This displays a name value pair for a parameter.
# TODO: clickable & focusable button will allow a popup of a graph showing its history
"""

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from typing import Union
from enum import Enum
from datetime import datetime
from .display_config import ICDisplayConfig
from .base_widget import ICBaseWidget, ICWidgetState


class ICTextLabelType(Enum):
    LabelInteger = 0
    LabelFloat = 1
    LabelText = 2


class ICTextLabel(ICBaseWidget):
    """
        Basic text label class to display (name, value) pair
    """
    def __init__(self, name: str, value: Union[int, float, str], label_type: ICTextLabelType = ICTextLabelType.LabelText, *args, **kwargs):
        super(ICTextLabel, self).__init__(*args, **kwargs)

        # internal variable of label type
        self.__type: ICTextLabelType = label_type

        # name and value of the parameter to be displayed in the text label
        self._name: str = name
        self._value: Union[int, float, str] = value

        # format for the axis label
        self._text_format = "{0:.0f}"

        # size of the text
        self._name_text_size: int = ICDisplayConfig.LabelNameSize
        self._value_text_size: int = ICDisplayConfig.LabelValueSize

        # colors
        self._label_color_light: QtGui.QColor = ICDisplayConfig.LabelBackLightColor
        self._label_color_dark: QtGui.QColor = ICDisplayConfig.LabelBackDarkColor

        # border color
        self._border_color: QtGui.QColor = ICDisplayConfig.LabelBorderColor

        # font colors
        self._name_color: QtGui.QColor = ICDisplayConfig.LabelNameColor
        self._value_color: QtGui.QColor = ICDisplayConfig.LabelValueColor

        # sets the click-ability and focus-ability of the button
        self.clickable = True
        self.focusable = True

        # set size of the text label
        self.size_hint = (ICDisplayConfig.TextLabelWidth, ICDisplayConfig.TextLabelHeight)

    ########################################################
    # properties
    ########################################################
    # get the name of the parameter
    @property
    def name(self) -> str:
        return self._name

    # set the name of the parameter
    @name.setter
    def name(self, nm: str) -> None:
        self._name = nm
        self.update()

    # get the parameter value
    @property
    def value(self) -> Union[int, float, str]:
        return self._value

    # update the parameter value
    @value.setter
    def value(self, val: Union[int, float, str]) -> None:
        # strict type checking while setting
        if self.__type == ICTextLabelType.LabelText:
            self._value = str(val)
            # add to the history and update the display
            self.append_history(self._value, 0)
            self.update()

        elif (self.__type == ICTextLabelType.LabelInteger) and (type(val) in (int, float)):
            self._value = int(val)
            # add to the history and update the display
            self.append_history("", float(self._value))
            self.update()

        elif type(val) in (int, float):
            self._value = float(val)
            # add to the history and update the display
            self.append_history("", self._value)
            self.update()

    # text format to convert float to str
    def text_format(self) -> str:
        return self._text_format

    # set text format
    def text_format(self, fmt_str: str) -> None:
        self._text_format = fmt_str
        self.update()

    # get the text size for name
    @property
    def name_text_size(self) -> int:
        return self._name_text_size

    # set the size of the text for name
    @name_text_size.setter
    def name_text_size(self, size: int) -> None:
        self._name_text_size = size
        self.update()

    # get the text size for value
    @property
    def value_text_size(self) -> int:
        return self._value_text_size

    # set the size of the text for value
    @value_text_size.setter
    def value_text_size(self, size: int) -> None:
        self._value_text_size = size
        self.update()

    # get the light and dark shades of the background color
    @property
    def label_colors(self) -> tuple[QtGui.QColor, QtGui.QColor]:
        return self._label_color_light, self._label_color_dark

    # set the light and dark shades of the background color
    @label_colors.setter
    def label_colors(self, color: tuple[QtGui.QColor, QtGui.QColor]) -> None:
        self._label_color_light = color[0]
        self._label_color_dark = color[1]
        self.update()

    # get the border color
    @property
    def border_color(self) -> QtGui.QColor:
        return self._border_color

    # set the border color
    @border_color.setter
    def border_color(self, color: QtGui.QColor) -> None:
        self._border_color = color
        self.update()

    # get the name text color
    @property
    def name_text_color(self) -> QtGui.QColor:
        return self._name_color

    # set the border color
    @name_text_color.setter
    def name_text_color(self, color: QtGui.QColor) -> None:
        self._name_color = color
        self.update()

    # get the value color
    @property
    def value_text_color(self) -> QtGui.QColor:
        return self._value_color

    # set the border color
    @value_text_color.setter
    def value_text_color(self, color: QtGui.QColor) -> None:
        self._value_color = color
        self.update()

    ########################################################
    # overrides and event handlers
    ########################################################
    # redraw the widget
    def redraw(self, painter: QtGui.QPainter, event) -> None:
        # if the button is hidden then there is nothing to draw
        if self._state == ICWidgetState.Hidden:
            return

        # draw the label area
        tmp_width = painter.device().width()
        tmp_height = painter.device().height()

        # define the rectangle to draw the button
        rect = QtCore.QRectF(3, 3, tmp_width-6, tmp_height-6)

        # path to be drawn
        path = QtGui.QPainterPath()
        path.setFillRule(Qt.WindingFill)
        path.addRoundedRect(rect, 10, 10)

        # brush to fill the area
        brush = QtGui.QLinearGradient(rect.topRight(), rect.bottomRight())
        if self._state == ICWidgetState.Transparent:
            brush.setColorAt(0, self.background_color)
            brush.setColorAt(1, self.background_color)
        else:
            brush.setColorAt(0, self._label_color_dark)
            brush.setColorAt(0.5, self._label_color_light)
            brush.setColorAt(1, self._label_color_dark)
        painter.setBrush(brush)

        # define the border pen
        if self._state == ICWidgetState.Transparent:
            pen = QtGui.QPen(self.background_color)
        else:
            pen = QtGui.QPen(self._border_color)
        if self.in_focus:
            pen.setWidth(3)
        else:
            pen.setWidth(1)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)

        # draw the rectangle
        painter.drawPath(path)

        # draw the text only if the button is visible
        if self._state in (ICWidgetState.VisibleEnabled, ICWidgetState.VisibleDisabled):
            # draw the name
            fnt = painter.font()
            fnt.setBold(True)
            fnt.setPixelSize(self._name_text_size)
            painter.setFont(fnt)
            pen.setColor(self._name_color)
            painter.setPen(pen)
            rect = QtCore.QRect(10, 10, tmp_width - 20, self._name_text_size + 5)
            painter.drawText(rect, Qt.AlignLeft, str(self._name))

            # draw the value
            fnt.setPixelSize(self._value_text_size)
            painter.setFont(fnt)
            pen.setColor(self._value_color)
            painter.setPen(pen)
            rect = QtCore.QRect(10, tmp_height - (self._value_text_size + 15), tmp_width - 20, self._value_text_size + 5)
            if self.__type == ICTextLabelType.LabelText:
                painter.drawText(rect, Qt.AlignRight, self._value)
            elif self.__type == ICTextLabelType.LabelInteger:
                painter.drawText(rect, Qt.AlignRight, str(self._value))
            else:
                painter.drawText(rect, Qt.AlignRight, self._text_format.format(self._value))

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.redraw(painter, e)


class ICClockLabel(ICTextLabel):
    """
        A text label showing current time
    """
    def __init__(self, name: str, *args, **kwargs):
        super(ICClockLabel, self).__init__(name, "", *args, **kwargs)
        # configure the display
        self.value_text_size = ICDisplayConfig.ClockLabelSize
        self.value_text_color = ICDisplayConfig.ClockLabelColor

        # datetime format
        self._time_format: str = '%H:%M:%S'

        # set the current time
        self._time_now = datetime.now()
        self.value = self._time_now.strftime(self._time_format)

        # start the timer
        self._clock_timer = QTimer()
        self._clock_timer.timeout.connect(self.update_time)
        self._clock_timer.start(1000)

    @property
    def time_format(self) -> str:
        return self._time_format

    @time_format.setter
    def time_format(self, fmt: str) -> None:
        self._time_format = fmt
        self.update_time()

    @property
    def time_now(self):
        self._time_now = datetime.now()
        return self._time_now

    @pyqtSlot()
    def update_time(self):
        self._time_now = datetime.now()
        self.value = self._time_now.strftime(self._time_format)
