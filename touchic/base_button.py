# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 14:12:21 2020

Update:
author: Prosenjit, date: 5-May-2021, change: added remarks

The base class for all types of buttons. This class draws the standard button with a label.

The following attributes are exposed.

name : label of the button
text_size : size of the label text
text_colors: pair of values
        text_color_enabled : color for the text when the button is enabled
        text_color_disabled : color for the text when the button is disabled

but_id : id of the button. can be used to identify buttons with same text label

state : visibility of the button. It can have multiple states. Determines what all is drawn

clickable : determines if the button emits the "clicked" signal for the host to capture

size_hint: a value pair providing the size hint (width and height) to the layout manager
        min_width : minimum width of the button
        min_height : minimum height of the button

button_colors: colors for rendering the button
        button_color_light : color of the button
        button_color_dark : color of the button

The defaults for the visual aspects of the class is defined in the ICDisplayConfig class
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from enum import Enum
from .display_config import ICDisplayConfig


class ICWidgetState(Enum):
    VisibleEnabled = 0
    VisibleDisabled = 1
    FrameOnly = 2
    Transparent = 3
    Hidden = 4


class ICBaseButton(QtWidgets.QWidget):
    # signal emitted when the button is clicked
    clicked = pyqtSignal([str], [str, int])

    def __init__(self, name: str, but_id: int = None, *args, **kwargs):
        super(ICBaseButton, self).__init__(*args, **kwargs)

        # the text on the button is also its name
        if name is not None:
            self._name: str = name
        else:
            self._name: str = ""

        # id of the button. useful in a scenario when multiple buttons have the same name
        self._but_id: int = but_id

        # sets the click-ability of the button
        self._clickable: bool = True

        # set the visibility of the button
        self._state: ICWidgetState = ICWidgetState.VisibleEnabled

        # set the text size used for the button label
        self._text_size = ICDisplayConfig.ButtonTextSize

        # the color of the button
        self._button_color_light = ICDisplayConfig.ButtonColorLight
        self._button_color_dark = ICDisplayConfig.ButtonColorDark

        # the color of the text
        self._text_color_enabled = ICDisplayConfig.ButtonTextColorEnabled
        self._text_color_disabled = ICDisplayConfig.ButtonTextColorDisabled

        # minimum width of the window
        self._width_min = ICDisplayConfig.ButtonMinWidth

        # minimum height of the window
        self._height_min = ICDisplayConfig.ButtonMinHeight

        # setup visual effects
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Minimum
        )

        # background color of the button
        self.setStyleSheet("background-color : " +
                           ICDisplayConfig.QtColorToSting(ICDisplayConfig.BackgroundColor) + ";")

    # returns the name of the button
    @property
    def name(self) -> str:
        return self._name

    # set the name of the button
    @name.setter
    def name(self, nm: str) -> None:
        if nm is not None:
            self._name = nm
        else:
            self._name = ""
        self.update()

    # returns the id of the button.
    # if it is not defined then None is returned
    @property
    def button_id(self) -> int:
        return self._but_id

    # set the button id. once set it cannot be reset to none
    # button id is always greater than zero
    @button_id.setter
    def button_id(self, bid: int) -> None:
        if bid is not None:
            if bid > 0:
                self._but_id = bid
                self.update()

    # return if the button is clickable
    @property
    def clickable(self) -> bool:
        return self._clickable

    # set the click-ability of the button
    # if enabled the button will emit the clicked signal
    @clickable.setter
    def clickable(self, click_able: bool) -> None:
        self._clickable = click_able

    # get the visibility of the button
    @property
    def state(self) -> ICWidgetState:
        return self._state

    # set the visibility of the button
    @state.setter
    def state(self, st: ICWidgetState) -> None:
        self._state = st
        if self._state in (ICWidgetState.Hidden, ICWidgetState.Transparent, ICWidgetState.VisibleDisabled):
            self._clickable = False
        else:
            self._clickable = True
        self.update()

    # get the text size
    @property
    def text_size(self) -> int:
        return self._text_size

    # set the text size
    @text_size.setter
    def text_size(self, sz: int) -> None:
        self._text_size = sz
        self.update()

    # get the light and dark shades used to render the button
    @property
    def button_colors(self) -> [QtGui.QColor, QtGui.QColor]:
        return [self._button_color_light, self._button_color_dark]

    # set the light and dark shades used to render the button
    @button_colors.setter
    def button_colors(self, colors: [QtGui.QColor, QtGui.QColor]) -> None:
        self._button_color_light = colors[0]
        self._button_color_dark = colors[1]
        self.update()

    # get the colors used for enabled and disabled text
    @property
    def text_colors(self) -> [QtGui.QColor, QtGui.QColor]:
        return self._text_color_enabled, self._text_color_disabled

    # set the colors used for enabled and disabled text
    @text_colors.setter
    def text_colors(self, colors: [QtGui.QColor, QtGui.QColor]) -> None:
        self._text_color_enabled = colors[0]
        self._text_color_disabled = colors[1]
        self.update()

    # get size hint
    @property
    def size_hint(self) -> [int, int]:
        return self._width_min, self._height_min

    # set size hint
    @size_hint.setter
    def size_hint(self, sz: [int, int]) -> None:
        self._width_min = sz[0]
        self._height_min = sz[1]

    # function to draw the button
    def redraw(self, painter: QtGui.QPainter) -> None:
        # if the button is hidden then there is nothing to draw
        if self._state == ICWidgetState.Hidden:
            return

        # the size of the button is determined by the size of the widget
        tmp_wdth = painter.device().width()
        tmp_hght = painter.device().height()

        # define the rectangle to draw the button
        rect = QtCore.QRectF(5, 5, tmp_wdth - 10, tmp_hght - 10)

        # a linear gradient brush is used to fill the button
        brush = QtGui.QLinearGradient(rect.topRight(), rect.bottomRight())

        # if the widget is transparent then the rect is drawn using background color
        if self._state == ICWidgetState.Transparent:
            brush.setColorAt(0, ICDisplayConfig.BackgroundColor)
            brush.setColorAt(1, ICDisplayConfig.BackgroundColor)
        else:
            brush.setColorAt(0, self._button_color_light)
            brush.setColorAt(1, self._button_color_dark)

        # define the pen that with rounded cap and join style
        pen = QtGui.QPen()
        pen.setWidth(1)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setBrush(brush)

        # set the pen and brush in the painter
        painter.setBrush(brush)
        painter.setPen(pen)

        # define the path that needs to be drawn
        path = QtGui.QPainterPath()
        path.setFillRule(Qt.WindingFill)
        path.addRoundedRect(rect, 10, 10)
        painter.drawPath(path)

        # draw the text only if the button is visible
        if self._state in (ICWidgetState.VisibleEnabled, ICWidgetState.VisibleDisabled):
            # define the font for drawing
            fnt = painter.font()
            fnt.setBold(True)
            fnt.setPixelSize(self._text_size)
            painter.setFont(fnt)

            # select the font color based on if the button is enabled or not
            if self._state == ICWidgetState.VisibleEnabled:
                pen.setColor(self._text_color_enabled)
            else:
                pen.setColor(self._text_color_disabled)
            painter.setPen(pen)

            # draw the text
            rect = QtCore.QRect(10, tmp_hght / 2 - 0.5 * (self._text_size + 5), tmp_wdth - 20, self._text_size + 5)
            painter.drawText(rect, Qt.AlignCenter, str(self._name))

    # override the default mouse press event handler for the button
    # this is equivalent to a touch event on a touch screen
    def mousePressEvent(self, event):
        # if the button is clickable then address the mouse event
        if self._clickable and (event.buttons() & Qt.LeftButton):
            if self._but_id is None:
                self.clicked[str].emit(self._name)
            else:
                self.clicked[str, int].emit(self._name, self._but_id)

    # size hint for the layout manager
    def sizeHint(self):
        if self._state == ICWidgetState.Hidden:
            return QtCore.QSize(0, 0)
        else:
            return QtCore.QSize(self._width_min, self._height_min)

    # minimum size hint for teh layout manager
    def minimumSizeHint(self):
        if self._state == ICWidgetState.Hidden:
            return QtCore.QSize(0, 0)
        else:
            return QtCore.QSize(self._width_min, self._height_min)

    # overriding the default paint event of the widget
    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.redraw(painter)
