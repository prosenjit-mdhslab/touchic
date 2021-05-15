# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 15:16:00 2020

@author: Prosenjit

This is a class for the toggle button. There is a label which is shown on the
top left corner of the button. The central text shows the status toggle state.
This class is extended from the BaseButton class. In addition to the attributes
exposed by the parent class the following attributes are defined

label:
label_text_size:
label_text_color:

off-text:
on-text:
on-off-text color:

curr_state:
toggle_type:
led_position
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from enum import Enum
from .base_button import ICBaseButton, ICWidgetState
from .display_config import ICDisplayConfig


# Different types of the toggle switch
class ICLEDType(Enum):
    ToggleNormal = 0
    AlarmCritical = 1
    AlarmNormal = 2
    AlarmInformation = 3


# position of the LED
class ICLEDPosition(Enum):
    Bottom = 0
    Top = 1
    Left = 2
    Right = 3


class ICToggleButton(ICBaseButton):

    # toggled signal emitted when the system changes state
    toggled = pyqtSignal([bool], [bool, int])
    
    def __init__(self, label: str, off_text: str, on_text: str, curr_state: bool,
                 led_type: ICLEDType = ICLEDType.ToggleNormal, but_id: int = None, *args, **kwargs):
        # initial test to determine the
        curr_val = on_text if curr_state else off_text

        # call the constructor for the base class
        super(ICToggleButton, self).__init__(name=curr_val, but_id=but_id, *args, **kwargs)

        # label of the toggling switch
        self._label: str = label

        # text to be shown during the on state and off state
        self._off_text: str = off_text
        self._on_text: str = on_text

        # current state of the toggle switch
        self._curr_state: bool = curr_state

        # type of the toggle switch
        self._led_type: ICLEDType = led_type

        # on off LED color
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

        # LED display position
        self._led_position: ICLEDPosition = ICLEDPosition.Bottom

        # setup visual effects
        self.text_size = ICDisplayConfig.ParamDisplayTextSize

        # size of the label text
        self._label_text_size: int = ICDisplayConfig.ParamButtonLabelTextSize

        # color of the label text
        self._label_color: QtGui.QColor = ICDisplayConfig.ParamButtonLabelColor

        # adjust the button height
        self._height_min = ICDisplayConfig.ToggleButtonMinHeight

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Minimum
        )
        self.setStyleSheet("background-color : " +
                           ICDisplayConfig.QtColorToSting(ICDisplayConfig.BackgroundColor) + ";")

    # get the current state
    @property
    def toggle_state(self) -> bool:
        return self._curr_state

    # set the current state
    @toggle_state.setter
    def toggle_state(self, st: bool) -> None:
        self._curr_state = st
        self.name = self._on_text if st else self._off_text
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
    def on_off_text(self) -> [str, str]:
        return self._on_text, self._off_text

    # set the on and off text used in the toggle button
    @on_off_text.setter
    def on_off_text(self, on_off_txt: [str, str]) -> None:
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
    def on_off_led_color(self) -> [QtGui.QColor, QtGui.QColor]:
        return self._toggle_on_color, self._toggle_off_color

    # set the on off color
    @on_off_led_color.setter
    def on_off_led_color(self, color: [QtGui.QColor, QtGui.QColor]) -> None:
        self._toggle_on_color = color[0]
        self._toggle_off_color = color[1]

    # get the position of the LED
    @property
    def led_position(self) -> ICLEDPosition:
        return self._led_position

    # set the position of the LED
    @led_position.setter
    def led_position(self, pos: ICLEDPosition):
        self._led_position = pos

    # handle the mouse press event
    def mousePressEvent(self, event):
        # process left click if the button is enabled
        if self._clickable and (event.buttons() & Qt.LeftButton):
            self._curr_state = not self._curr_state
            self._name = self._on_text if self._curr_state else self._off_text
            if self._but_id is None:
                self.toggled[bool].emit(self._curr_state)
            else:
                self.toggled[bool, int].emit(self._curr_state, self._but_id)
            self.update()

    # paint event for the button
    def paintEvent(self, e):
        # if the button is hidden then there is nothing to draw
        if self._state == ICWidgetState.Hidden:
            return

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # draw the base button
        super().redraw(painter)

        # draw the text
        tmp_wdth = painter.device().width()
        tmp_hght = painter.device().height()

        pen = QtGui.QPen()
        pen.setWidth(1)
        pen.setColor(self._label_color)
        painter.setPen(pen)

        fnt = painter.font()
        fnt.setPixelSize(self._label_text_size)
        fnt.setBold(True)
        painter.setFont(fnt) 

        if self._led_position in (ICLEDPosition.Bottom, ICLEDPosition.Right):
            rect = QtCore.QRect(10, 10, tmp_wdth - 20, self._label_text_size)
            painter.drawText(rect, Qt.AlignLeft, self._label)
        else:
            rect = QtCore.QRect(10, tmp_hght - self._label_text_size-10, tmp_wdth - 20, self._label_text_size)
            painter.drawText(rect, Qt.AlignRight, self._label)

        # draw the toggle
        path = QtGui.QPainterPath()
        path.setFillRule(Qt.WindingFill)
        if self._led_position == ICLEDPosition.Bottom:
            rect = QtCore.QRectF(10, tmp_hght - 25, tmp_wdth - 20, 15)
        elif self._led_position == ICLEDPosition.Top:
            rect = QtCore.QRectF(10, 10, tmp_wdth - 20, 15)
        elif self._led_position == ICLEDPosition.Right:
            rect = QtCore.QRectF(tmp_wdth-30, 10, 20, tmp_hght-20)
        else:
            rect = QtCore.QRectF(10, 10, 20, tmp_hght - 20)
        path.addRoundedRect(rect, 5, 5)
        if self._curr_state:
            painter.setBrush(self._toggle_on_color)
        else:
            painter.setBrush(self._toggle_off_color)
        painter.drawPath(path)                
