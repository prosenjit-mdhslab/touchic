# -*- coding: utf-8 -*-
"""
Created on May 22 2021

@author: prosenjit

Custom Qt Widget to show alarm message.
"""

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from datetime import datetime
from enum import Enum
from .display_config import ICDisplayConfig
from .toggle_button import ICToggleButton, ICLEDType
from .basic_button import ICBasicButton
from .base_widget import ICBaseWidget


class ICAlarmMessage(QtWidgets.QDialog):

    def __init__(self, title, message, *args, **kwargs):
        super(ICAlarmMessage, self).__init__(*args, **kwargs)

        self.setWindowTitle("{}".format(title))

        layout = QtWidgets.QVBoxLayout()
        label = QtWidgets.QLabel("", self)
        label.setStyleSheet("QLabel { background-color : " + ICDisplayConfig.QtColorToSting(ICDisplayConfig.BackgroundColor) + "; color : " +
                            ICDisplayConfig.QtColorToSting(ICDisplayConfig.HeaderTextColor) + ";}")
        label.setText("<span style='font-size:" + "{}".format(ICDisplayConfig.GeneralTextSize) + "pt;'>" + message + "</span>")
        label.setWordWrap(True)
        layout.addWidget(label)

        horizontal_layout = QtWidgets.QHBoxLayout()

        # Acknowledge the alarm
        self._okBut = ICBasicButton("Yes")
        self._okBut.clicked.connect(self.accept)
        horizontal_layout.addWidget(self._okBut)

        # Cancel the alarm
        self._cancelBut = ICBasicButton("No")
        self._cancelBut.clicked.connect(self.reject)
        horizontal_layout.addWidget(self._cancelBut)

        layout.addLayout(horizontal_layout)
        self.setLayout(layout)

        self.setStyleSheet("background-color : " + ICDisplayConfig.QtColorToSting(ICDisplayConfig.BackgroundColor) + ";")


class ICAlarmStatus(Enum):
    Active = 1
    Acknowledged = 2
    Inactive = 3


class ICAlarmWidget(ICBaseWidget):

    # signal for acknowledging the event
    acknowledged = pyqtSignal(int)

    def __init__(self, alarm_id: int, alarm: str, message: str, led_type: ICLEDType = ICLEDType.AlarmCritical,
                 *args, **kwargs):
        super(ICAlarmWidget, self).__init__(*args, **kwargs)

        # alarm information
        self._alarm_id: int = alarm_id
        self._alarm_txt: str = alarm
        if message is not None:
            self._descriptive_txt: str = message + " Do you want to acknowledge and silence the alarm?"
        else:
            self._descriptive_txt: str = " Do you want to acknowledge and silence the alarm?"

        # alarm status
        self._status: ICAlarmStatus = ICAlarmStatus.Active

        # alarm led type
        self._led_type: ICLEDType = led_type

        # alarm raised and acknowledged time
        self._raised_time: datetime = datetime.now()
        self._acknowledged_time: datetime = datetime.now()

        # alarm inactive time after acknowledged
        self._reactivation_wait_time = 0.0

        # error display parameters
        self._msg_size = ICDisplayConfig.GeneralTextSize
        self._msg_color = ICDisplayConfig.ErrorTextColor

        # set the background color
        self._msg_back_color = ICDisplayConfig.AlarmCriticalOffColor
        self._msg_border_color = ICDisplayConfig.AlarmCriticalOnColor

        if led_type == ICLEDType.AlarmNormal:
            self._msg_back_color = ICDisplayConfig.AlarmNormalOffColor
            self._msg_border_color = ICDisplayConfig.AlarmNormalOnColor
        elif led_type == ICLEDType.AlarmInformation:
            self._msg_back_color = ICDisplayConfig.AlarmInformationOffColor
            self._msg_border_color = ICDisplayConfig.AlarmInformationOnColor

        # create the horizontal layout
        layout = QtWidgets.QHBoxLayout()

        # short message of the alarm
        self._alarm_display = QtWidgets.QLabel("", self)
        self._alarm_display.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Sunken)
        self._alarm_display.setStyleSheet("QLabel { background-color : " + ICDisplayConfig.QtColorToSting(self._msg_back_color) + "; color : " +
                                          ICDisplayConfig.QtColorToSting(self._msg_color) + "; border-radius : 8px; border-color : " +
                                          ICDisplayConfig.QtColorToSting(self._msg_border_color) + "; border-width : 2px; border-style: outset; }")
        self._alarm_display.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._alarm_display.setWordWrap(True)
        self._alarm_display.setText("<span style='font-size:" + "{}".format(self._msg_size) + "pt;'> ({}):".format(self._raised_time.strftime("%H:%M:%S"))
                                    + self._alarm_txt + "</span>")

        # override the default size policy
        self._alarm_display.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        layout.addWidget(self._alarm_display)

        # add the acknowledge button
        self.acknowledge_button = ICToggleButton("Status", "Silent", "Alarmed", True, self._led_type)
        self.acknowledge_button.toggled.connect(self.clicked_acknowledge)
        layout.addWidget(self.acknowledge_button)

        self.setLayout(layout)

    # alarm id property
    @property
    def alarm_id(self) -> int:
        return self._alarm_id

    # set the alarm id
    @alarm_id.setter
    def alarm_id(self, idd: int) -> None:
        self._alarm_id = idd

    # alarm text property
    @property
    def alarm_text(self) -> str:
        return self._alarm_txt

    # set the alarm text
    @alarm_text.setter
    def alarm_text(self, txt: str) -> None:
        self._alarm_txt = txt
        self._local_update()

    # get the descriptive text for the alarm
    @property
    def alarm_description(self) -> str:
        return self._descriptive_txt

    # set the alarm description
    @alarm_description.setter
    def alarm_description(self, desc: str) -> None:
        self._descriptive_txt = desc

    # get the alarm status (read only)
    @property
    def alarm_status(self) -> ICAlarmStatus:
        return self._status

    # get the alarm led type
    @property
    def alarm_type(self) -> ICLEDType:
        return self._led_type

    # set the alarm led type
    @alarm_type.setter
    def alarm_type(self, at: ICLEDType) -> None:
        self._led_type = at
        self.acknowledge_button.led_type = at
        if at == ICLEDType.AlarmNormal:
            self._msg_back_color = ICDisplayConfig.AlarmNormalOffColor
            self._msg_border_color = ICDisplayConfig.AlarmNormalOnColor
        elif at == ICLEDType.AlarmInformation:
            self._msg_back_color = ICDisplayConfig.AlarmInformationOffColor
            self._msg_border_color = ICDisplayConfig.AlarmInformationOnColor
        else:
            self._msg_back_color = ICDisplayConfig.AlarmCriticalOffColor
            self._msg_border_color = ICDisplayConfig.AlarmCriticalOnColor
        self._local_update()

    # get the last time the alarm was raised (read only)
    @property
    def raised_time(self) -> datetime:
        return self._raised_time

    # get the last time the alarm was acknowledged (read only)
    @property
    def acknowledged_time(self) -> datetime:
        return self._acknowledged_time

    # get the reactivation wait time
    @property
    def reactivation_time(self) -> float:
        return self._reactivation_wait_time

    # set reactivation time
    @reactivation_time.setter
    def reactivation_time(self, rt: float) -> None:
        self._reactivation_wait_time = rt

    # get message text size
    @property
    def message_text_size(self) -> int:
        return self._msg_size

    # set message text
    @message_text_size.setter
    def message_text_size(self, sz: int) -> None:
        self._msg_size = sz
        self._local_update()

    # get message text font color
    @property
    def message_font_color(self) -> QtGui.QColor:
        return self._msg_color

    # set time text font color
    @message_font_color.setter
    def message_font_color(self, clr: QtGui.QColor) -> None:
        self._msg_color = clr
        self._local_update()

    # get message text font color
    @property
    def message_back_color(self) -> QtGui.QColor:
        return self._msg_back_color

    # set time text font color
    @message_back_color.setter
    def message_back_color(self, clr: QtGui.QColor) -> None:
        self._msg_back_color = clr
        self._local_update()

    # get message text font color
    @property
    def message_border_color(self) -> QtGui.QColor:
        return self._msg_border_color

    # set time text font color
    @message_border_color.setter
    def message_border_color(self, clr: QtGui.QColor) -> None:
        self._msg_border_color = clr
        self._local_update()

    # acknowledge the alarm and let others know that the alarm has been acknowledged
    @pyqtSlot(bool)
    def clicked_acknowledge(self, st: bool):
        # alarm is acknowledged only when toggle state changes from Ture (on) to False (off)
        # and alarm status is active
        if not st and self._status == ICAlarmStatus.Active:
            popup = ICAlarmMessage(self._alarm_txt, self._descriptive_txt)
            result = popup.exec()
            if result:
                # set the alarm status to Acknowledged
                self._status = ICAlarmStatus.Acknowledged
                # record the time when the alarm was acknowledged time
                self._acknowledged_time = datetime.now()
                # once acknowledged the button is not clickable
                self.acknowledge_button.clickable = False
                # let others know that the alarm has been acknowledged
                self.acknowledged.emit(self._alarm_id)
                # add to the history that the alarm was acknowledged
                self.append_history("acknowledged", self._alarm_id)
            else:
                # ensure that the acknowledge button resets to the active(on) state
                self.acknowledge_button.switch_position = True

    # activate the alarm
    def activate(self) -> None:
        # the alarm is already active then there is nothing to do
        if self._status == ICAlarmStatus.Active:
            return
        elif self._status == ICAlarmStatus.Acknowledged:
            elapsed = datetime.now() - self._acknowledged_time
            # if the reactivation time has not been elapsed
            if elapsed.total_seconds() < self._reactivation_wait_time:
                return
        # change the status of the alarm
        self._status = ICAlarmStatus.Active
        # record the activated (raised) time
        self._raised_time = datetime.now()
        # as the button is not clickable manually
        # change the state of the acknowledged button
        self.acknowledge_button.switch_position = True
        # make the button clickable
        self.acknowledge_button.clickable = True
        # show the widget
        self.show()
        # append the event to history
        self.append_history("activated", self._alarm_id)
        # update the display
        self._local_update()

    # deactivate the alarm
    def deactivate(self) -> None:
        # set the status of the alarm
        self._status = ICAlarmStatus.Inactive
        # disable button click
        self.acknowledge_button.clickable = False
        # hide the widget
        self.hide()
        # append the event to history
        self.append_history("deactivated", self._alarm_id)
        # update the display
        self._local_update()

    def _local_update(self) -> None:
        # update alarm text
        self._alarm_display.setStyleSheet("QLabel { background-color : " + ICDisplayConfig.QtColorToSting(self._msg_back_color) + "; color : " +
                                          ICDisplayConfig.QtColorToSting(self._msg_color) + "; border-radius : 8px; border-color : " +
                                          ICDisplayConfig.QtColorToSting(self._msg_border_color) + "; border-width : 2px; border-style: outset; }")
        self._alarm_display.setAlignment(Qt.AlignCenter)
        self._alarm_display.setText("<span style='font-size:" + "{}".format(self._msg_size) + "pt;'> ({}) : ".format(self._raised_time.strftime("%H:%M:%S"))
                                    + self._alarm_txt + "</span>")
        self._alarm_display.update()

        # update the button
        self.acknowledge_button.update()
