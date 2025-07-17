# -*- coding: utf-8 -*-
"""
Created on May 18 2021

@author: Prosenjit

This is a simple basic button
"""

from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt, pyqtSignal
from .display_config import ICDisplayConfig
from .base_widget import ICBaseWidget, ICWidgetState


class ICBasicButton(ICBaseWidget):
    """
    Basic button class. Emits a "clicked" signal.
    """
    # signal emitted when the button is clicked
    clicked = pyqtSignal(str, int)

    def __init__(self, name: str, but_id: int = 0, *args, **kwargs):
        super(ICBasicButton, self).__init__(but_id, *args, **kwargs)

        # the text on the button is also its name
        if name is not None:
            self._name: str = name
        else:
            self._name: str = ""

        # set the text size used for the button label
        self._text_size = ICDisplayConfig.ButtonTextSize

        # the color of the button
        self._button_color_light = ICDisplayConfig.ButtonColorLightRaised
        self._button_color_dark = ICDisplayConfig.ButtonColorDarkRaised

        # the color of the text
        self._text_color_enabled = ICDisplayConfig.ButtonTextColorEnabled
        self._text_color_disabled = ICDisplayConfig.ButtonTextColorDisabled

        # set the size hint for the button class
        self.size_hint = (ICDisplayConfig.ButtonMinWidth, ICDisplayConfig.ButtonMinHeight)

        # sets the click-ability and focus-ability of the button
        self.clickable = True
        self.focusable = True

    ########################################################
    # properties
    ########################################################
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
    def button_colors(self) -> tuple[QtGui.QColor, QtGui.QColor]:
        return self._button_color_light, self._button_color_dark

    # set the light and dark shades used to render the button
    @button_colors.setter
    def button_colors(self, colors: tuple[QtGui.QColor, QtGui.QColor]) -> None:
        self._button_color_light = colors[0]
        self._button_color_dark = colors[1]
        self.update()

    # get the colors used for enabled and disabled text
    @property
    def text_colors(self) -> tuple[QtGui.QColor, QtGui.QColor]:
        return self._text_color_enabled, self._text_color_disabled

    # set the colors used for enabled and disabled text
    @text_colors.setter
    def text_colors(self, colors: tuple[QtGui.QColor, QtGui.QColor]) -> None:
        self._text_color_enabled = colors[0]
        self._text_color_disabled = colors[1]
        self.update()

    ########################################################
    # base class event overrides
    ########################################################
    # mouse press event for the button. this is equivalent to a touch event on a touch screen
    def on_mouse_pressed(self, event: QtGui.QMouseEvent) -> None:
        if event.button() & Qt.LeftButton:
            # switch to depressed colors
            self.button_colors = (ICDisplayConfig.ButtonColorLightDepressed, ICDisplayConfig.ButtonColorDarkDepressed)

    # mouse release event for the button
    def on_mouse_released(self, event: QtGui.QMouseEvent) -> None:
        if event.button() & Qt.LeftButton:
            # switch back to raised colors
            self.button_colors = (ICDisplayConfig.ButtonColorLightRaised, ICDisplayConfig.ButtonColorDarkRaised)
            # append user event to the history
            self.append_history("clicked", 0)
            self.clicked.emit(self._name, self._widget_id)

    ########################################################
    # overrides and event handlers
    ########################################################
    # overriding the default paint event of the widget
    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.redraw(painter)

    # function to draw the button
    def redraw(self, painter: QtGui.QPainter, vertical_offset: float = 0) -> None:
        # if the button is hidden then there is nothing to draw
        if self._state == ICWidgetState.Hidden:
            return

        # the size of the button is determined by the size of the widget
        tmp_width = painter.device().width()
        tmp_height = painter.device().height()

        # define the rectangle to draw the button
        rect = QtCore.QRectF(5, 5, tmp_width - 10, tmp_height - 10)

        # a linear gradient brush is used to fill the button
        brush = QtGui.QLinearGradient(rect.topRight(), rect.bottomRight())
        # if the widget is transparent then the rect is drawn using background color
        if self._state == ICWidgetState.Transparent:
            brush.setColorAt(0, self.background_color)
            brush.setColorAt(1, self.background_color)
        else:
            brush.setColorAt(0, self._button_color_light)
            brush.setColorAt(1, self._button_color_dark)

        # set the brush
        painter.setBrush(brush)

        # define the pen that with rounded cap and join style
        if not self.in_focus:
            pen = QtGui.QPen()
            pen.setWidth(1)
        else:
            pen = QtGui.QPen(self.focus_color)
            pen.setWidth(3)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)

        # set the pen to use the brush and set the painter pen
        if not self.in_focus:
            pen.setBrush(brush)
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
            rect = QtCore.QRectF(10, tmp_height / 2 - 0.5 * (self._text_size + 5) + vertical_offset, tmp_width - 20, self._text_size + 5)
            painter.drawText(rect, Qt.AlignCenter, str(self._name))
