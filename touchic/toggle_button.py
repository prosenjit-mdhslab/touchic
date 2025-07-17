# -*- coding: utf-8 -*-
"""
Created on May  18 2021

@author: Prosenjit

This file implements a toggle button
"""

from enum import Enum
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt, pyqtSignal
from .base_widget import ICWidgetState, ICWidgetPosition
from .basic_button import ICBasicButton
from .display_config import ICDisplayConfig


# Different types of the toggle switch
class ICLEDType(Enum):
    """
        Enum for LED Type
    """
    ToggleNormal = 0
    AlarmCritical = 1
    AlarmNormal = 2
    AlarmInformation = 3


class ICToggleButton(ICBasicButton):
    """
        Toggle Button Class
    """
    # toggled signal emitted when the system changes state
    toggled = pyqtSignal(bool, int)
    
    def __init__(self, label: str, off_text: str, on_text: str, switch_pos: bool, led_type: ICLEDType = ICLEDType.ToggleNormal,
                 but_id: int = 0, *args, **kwargs):
        super(ICToggleButton, self).__init__(name="", but_id=but_id, *args, **kwargs)

        # label of the toggling switch
        self._label: str = label

        # text to be shown during the on state and off state
        self._off_text: str = off_text
        self._on_text: str = on_text

        # current state of the toggle switch
        self._switch_pos: bool = switch_pos

        if self._switch_pos:
            self.button_colors = (ICDisplayConfig.ButtonColorLightDepressed, ICDisplayConfig.ButtonColorDarkDepressed)
        else:
            self.button_colors = (ICDisplayConfig.ButtonColorLightRaised, ICDisplayConfig.ButtonColorDarkRaised)

        # set the current name for the text
        self.name = on_text if switch_pos else off_text

        # type of the toggle switch
        self._led_type: ICLEDType = led_type

        # on-off LED color. LED color is linked to the LED type
        self._toggle_on_color: QtGui.QColor = ICDisplayConfig.AlarmInformationOnColor
        self._toggle_off_color: QtGui.QColor = ICDisplayConfig.AlarmInformationOffColor

        if led_type == ICLEDType.ToggleNormal:
            self._toggle_on_color = ICDisplayConfig.ToggleOnColor
            self._toggle_off_color = ICDisplayConfig.ToggleOffColor
        elif led_type == ICLEDType.AlarmCritical:
            self._toggle_on_color = ICDisplayConfig.AlarmCriticalOnColor
            self._toggle_off_color = ICDisplayConfig.AlarmCriticalOffColor
        elif led_type == ICLEDType.AlarmNormal:
            self._toggle_on_color = ICDisplayConfig.AlarmNormalOnColor
            self._toggle_off_color = ICDisplayConfig.AlarmNormalOffColor

        # setup visual effects
        self.text_size = ICDisplayConfig.ParamDisplayTextSize

        # size of the label text
        self._label_text_size: int = ICDisplayConfig.ParamButtonLabelTextSize

        # color of the label text
        self._label_color: QtGui.QColor = ICDisplayConfig.ParamButtonLabelColor

        # adjust the button height
        curr_width, _ = self.size_hint
        self.size_hint = (curr_width, ICDisplayConfig.ToggleButtonMinHeight)

    ########################################################
    # properties
    ########################################################
    # get the current switch position
    @property
    def toggle_state(self) -> bool:
        return self._switch_pos

    # set the current state. button label is updated
    @toggle_state.setter
    def toggle_state(self, st: bool) -> None:
        # if the state is same as before, we dont need to change
        if self._switch_pos == st:
            return
        self._switch_pos = st
        self._name = self._on_text if self._switch_pos else self._off_text
        if self._switch_pos:
            self.button_colors = (ICDisplayConfig.ButtonColorLightDepressed, ICDisplayConfig.ButtonColorDarkDepressed)
        else:
            self.button_colors = (ICDisplayConfig.ButtonColorLightRaised, ICDisplayConfig.ButtonColorDarkRaised)
        # append user event to the history
        self.append_history(self._name, float(self._switch_pos))
        self.toggled.emit(self._switch_pos, self._widget_id)
        self.update()

    # get the label for the toggle button
    @property
    def label(self) -> str:
        return self._label

    # set the label for the toggle button
    @label.setter
    def label(self, lbl: str) -> None:
        self._label = lbl
        self.update()

    # get the on and off text used in the toggle button
    @property
    def on_off_text(self) -> tuple[str, str]:
        return self._on_text, self._off_text

    # set the on and off text used in the toggle button
    @on_off_text.setter
    def on_off_text(self, on_off_txt: tuple[str, str]) -> None:
        self._on_text = on_off_txt[0]
        self._off_text = on_off_txt[1]
        self.update()

    # get the toggle type for the switch
    @property
    def led_type(self) -> ICLEDType:
        return self._toggle_type

    # set the toggle type for the switch
    @led_type.setter
    def led_type(self, l_type: ICLEDType) -> None:
        self._led_type = l_type
        if self._toggle_type == ICLEDType.ToggleNormal:
            self._toggle_on_color = ICDisplayConfig.ToggleOnColor
            self._toggle_off_color = ICDisplayConfig.ToggleOffColor
        elif self._toggle_type == ICLEDType.AlarmCritical:
            self._toggle_on_color = ICDisplayConfig.AlarmCriticalOnColor
            self._toggle_off_color = ICDisplayConfig.AlarmCriticalOffColor
        elif self._toggle_type == ICLEDType.AlarmNormal:
            self._toggle_on_color = ICDisplayConfig.AlarmNormalOnColor
            self._toggle_off_color = ICDisplayConfig.AlarmNormalOffColor
        else:
            self._toggle_on_color: QtGui.QColor = ICDisplayConfig.AlarmInformationOnColor
            self._toggle_off_color: QtGui.QColor = ICDisplayConfig.AlarmInformationOffColor
        self.update()

    # get label text size
    @property
    def label_text_size(self) -> int:
        return self._label_text_size

    # set the label text size
    @label_text_size.setter
    def label_text_size(self, sz: int) -> None:
        self._label_text_size = sz

    # get the label text color
    @property
    def label_text_color(self) -> QtGui.QColor:
        return self._label_color

    # set the label text color
    @label_text_color.setter
    def label_text_color(self, clr: QtGui.QColor) -> None:
        self._label_color = clr
        self.update()

    # get the on off color
    @property
    def on_off_led_color(self) -> tuple[QtGui.QColor, QtGui.QColor]:
        return self._toggle_on_color, self._toggle_off_color

    # set the on off color
    @on_off_led_color.setter
    def on_off_led_color(self, color: tuple[QtGui.QColor, QtGui.QColor]) -> None:
        self._toggle_on_color = color[0]
        self._toggle_off_color = color[1]

    ########################################################
    # base class event overrides
    ########################################################
    # mouse release for the button. this is equivalent to a touch event on a touch screen
    def on_mouse_released(self, event: QtGui.QMouseEvent):
        # process left click if the button is enabled
        if event.button() & Qt.LeftButton:
            # property setter will take care of the remaining steps
            self.toggle_state = not self.toggle_state

    ########################################################
    # overrides and event handlers
    ########################################################
    # paint event for the button
    def paintEvent(self, e):
        # if the button is hidden then there is nothing to draw
        if self._state == ICWidgetState.Hidden:
            return

        # get the painter object
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # draw the base button
        super().redraw(painter)

        # draw the text only if the button is visible
        if self._state in (ICWidgetState.VisibleEnabled, ICWidgetState.VisibleDisabled):
            tmp_width = painter.device().width()
            tmp_height = painter.device().height()

            # create and set the pen
            pen = QtGui.QPen()
            pen.setWidth(1)
            pen.setColor(self._label_color)
            painter.setPen(pen)

            # create and set the font
            fnt = painter.font()
            fnt.setPixelSize(self._label_text_size)
            fnt.setBold(True)
            painter.setFont(fnt)

            # draw the text based on the LED position
            if self._led_position in (ICWidgetPosition.Bottom | ICWidgetPosition.Right):
                rect = QtCore.QRect(10, 10, tmp_width - 20, self._label_text_size + 3)
                painter.drawText(rect, Qt.AlignLeft, self._label)
            else:
                rect = QtCore.QRect(10, tmp_height - self._label_text_size-10, tmp_width - 20, self._label_text_size + 3)
                painter.drawText(rect, Qt.AlignRight, self._label)

            # draw the toggle LED
            path = QtGui.QPainterPath()
            path.setFillRule(Qt.WindingFill)

            if self._led_position == ICWidgetPosition.Bottom:
                rect = QtCore.QRectF(10, tmp_height - 25, tmp_width - 20, 15)
            elif self._led_position == ICWidgetPosition.Top:
                rect = QtCore.QRectF(10, 10, tmp_width - 20, 15)
            elif self._led_position == ICWidgetPosition.Right:
                rect = QtCore.QRectF(tmp_width-30, 10, 20, tmp_height-20)
            else:
                rect = QtCore.QRectF(10, 10, 20, tmp_height - 20)
            path.addRoundedRect(rect, 5, 5)

            # color depends on the switch position (on or off)
            if self._switch_pos:
                painter.setBrush(self._toggle_on_color)
            else:
                painter.setBrush(self._toggle_off_color)
            painter.drawPath(path)
