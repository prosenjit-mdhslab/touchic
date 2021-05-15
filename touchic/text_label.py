# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 17:20:01 2020

@author: Prosenjit

This displays a name value pair for a parameter. The exposed attributes are

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

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from .display_config import ICDisplayConfig


class ICTextLabel(QtWidgets.QWidget):
    def __init__(self, name: str, value: str, *args, **kwargs):
        super(ICTextLabel, self).__init__(*args, **kwargs)
        # name and value of the parameter to be displayed in the text label
        self._name: str = name
        self._value: str = value

        # size of the text
        self._name_text_size: int = ICDisplayConfig.LabelNameSize
        self._value_text_size: int = ICDisplayConfig.LabelValueSize

        # size of the text label
        self._width: int = ICDisplayConfig.TextLabelWidth
        self._height: int = ICDisplayConfig.TextLabelHeight

        # colors
        self._back_color_dark: QtGui.QColor = ICDisplayConfig.LabelBackDarkColor
        self._back_color_light: QtGui.QColor = ICDisplayConfig.LabelBackLightColor

        self._border_color: QtGui.QColor = ICDisplayConfig.LabelBorderColor

        self._name_color: QtGui.QColor = ICDisplayConfig.LabelNameColor
        self._value_color: QtGui.QColor = ICDisplayConfig.LabelValueColor

        # setup visual effects
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Minimum
        )
        self.setStyleSheet("background-color : " +
                           ICDisplayConfig.QtColorToSting(ICDisplayConfig.BackgroundColor) + ";")

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
    def value(self) -> str:
        return self._value

    # update the parameter value
    @value.setter
    def value(self, val: str) -> None:
        self._value = val
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

    # get the size hint
    @property
    def size_hint(self) -> [int, int]:
        return self._width, self._height

    # set the size hint of the widget
    @size_hint.setter
    def size_hint(self, sz: [int, int]) -> None:
        self._width = sz[0]
        self._height = sz[1]

    # get the light and dark shades of the background color
    @property
    def back_colors(self) -> [QtGui.QColor, QtGui.QColor]:
        return self._back_color_light, self._back_color_dark

    # set the light and dark shades of the background color
    @back_colors.setter
    def back_colors(self, color: [QtGui.QColor, QtGui.QColor]) -> None:
        self._back_color_light = color[0]
        self._back_color_dark = color[1]
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

    # redraw the widget
    def redraw(self, painter: QtGui.QPainter, event) -> None:
        # draw the label area
        tmp_wdth = painter.device().width()
        tmp_hght = painter.device().height()
        rect = QtCore.QRectF(0, 0, tmp_wdth, tmp_hght)

        # path to be drawn
        path = QtGui.QPainterPath()
        path.setFillRule(Qt.WindingFill)
        path.addRoundedRect(rect, 10, 10)

        # brush to fill the area
        brush = QtGui.QLinearGradient(rect.topRight(), rect.bottomRight())
        brush.setColorAt(0, self._back_color_dark)
        brush.setColorAt(0.5, self._back_color_light)
        brush.setColorAt(1, self._back_color_dark)
        painter.setBrush(brush)

        # define the border pen
        pen = QtGui.QPen(self._border_color)
        pen.setWidth(1)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)

        # draw the rectangle
        painter.drawPath(path)

        # font for the name
        fnt = painter.font()
        fnt.setBold(True)
        fnt.setPixelSize(self._name_text_size)
        painter.setFont(fnt)
        pen.setColor(self._name_color)
        painter.setPen(pen)
        rect = QtCore.QRect(10, 10, tmp_wdth - 20, self._name_text_size + 5)
        painter.drawText(rect, Qt.AlignLeft, str(self._name))

        # draw the value
        fnt.setPixelSize(self._value_text_size)
        painter.setFont(fnt)
        pen.setColor(self._value_color)
        painter.setPen(pen)
        rect = QtCore.QRect(10, tmp_hght - (self._value_text_size + 15), tmp_wdth - 20, self._value_text_size + 5)
        painter.drawText(rect, Qt.AlignRight, str(self._value))

    def sizeHint(self):
        return QtCore.QSize(self._width, self._height)

    def minimumSizeHint(self):
        return QtCore.QSize(self._width, self._height)

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.redraw(painter, e)
