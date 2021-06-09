# -*- coding: utf-8 -*-
"""
Created on May 23 2021

@author: Prosenjit

A button to input different kind of data
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from typing import Union
from .display_config import ICDisplayConfig
from .base_widget import ICBaseWidget, ICWidgetState
from .basic_button import ICBasicButton


class ICConfigDialogTemplate (QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super(ICConfigDialogTemplate, self).__init__(*args, **kwargs)

        # internal variables for displaying on the button
        self._title: str = ""
        self._display_value: str = ""
        self._unit: str = ""

        # actual return value
        self._value = None

        # background color of the button
        self.setStyleSheet("background-color : " + ICDisplayConfig.QtColorToSting(ICDisplayConfig.BackgroundColor) + ";")

    # generate the standard ok and cancel button
    def generate_ok_cancel_buttons(self) -> QtWidgets.QHBoxLayout:
        hr_lay = QtWidgets.QHBoxLayout()
        ok_button = ICBasicButton("Ok")
        ok_button.clicked.connect(self.ok_clicked)
        hr_lay.addWidget(ok_button)
        cancel_button = ICBasicButton("Cancel")
        cancel_button.clicked.connect(self.cancel_clicked)
        hr_lay.addWidget(cancel_button)
        return hr_lay

    ####################################
    # Properties
    ####################################
    @property
    def value(self):
        return self._value

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, x: str) -> None:
        self._title = x

    @property
    def display_value(self) -> str:
        return self._display_value

    @display_value.setter
    def display_value(self, x: str) -> None:
        self._display_value = x

    @property
    def unit(self) -> str:
        return self._unit

    @unit.setter
    def unit(self, x: str) -> None:
        self._unit = x

    ####################################
    # Callback functions
    ####################################
    # called when ok is clicked
    def on_ok_clicked(self) -> None:
        pass

    # called when cancel is clicked
    def on_cancel_clicked(self) -> None:
        pass

    # called when something additional has to be rendered on the button
    def draw_additional(self, painter: QtGui.QPainter, width: int, height: int, keep_out_width: int, keep_out_height: int) -> None:
        pass

    ####################################
    # Slots
    ####################################
    def ok_clicked(self):
        self.on_ok_clicked()
        self.accept()

    def cancel_clicked(self):
        self.on_cancel_clicked()
        self.reject()


class ICConfigButton(ICBasicButton):
    """
        A button class for updating configuration
    """
    config_updated = pyqtSignal()

    def __init__(self, title: str, value: str, unit: str, config_dialog: ICConfigDialogTemplate, widget_id: int = 0, *args, **kwargs):
        super(ICConfigButton, self).__init__(value, widget_id, *args, **kwargs)

        self._config_dialog: ICConfigDialogTemplate = config_dialog

        self._config_dialog.title = title
        self._config_dialog.display_value = str(value)
        self._config_dialog.unit = unit

        # local copy of the value
        self.__local_value = value

        # display parameters
        self._label_color: QtGui.QColor = ICDisplayConfig.ParamButtonLabelColor
        self._label_text_size: int = ICDisplayConfig.LabelTextSize

        # connect the events
        self.clicked.connect(self.on_clicked)

        # setup visual effects
        self.text_size = ICDisplayConfig.ParamDisplayTextSize

        # set up the display
        self.size_hint = (ICDisplayConfig.ButtonMinWidth, ICDisplayConfig.ParamButtonMinHeight)

        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

    ####################################
    # Slots
    ####################################
    def on_clicked(self) -> None:
        if self._config_dialog.exec():
            if self._config_dialog.value != self.__local_value:
                self.__local_value = self._config_dialog.value
                self.config_updated.emit()

    ####################################
    # Properties
    ####################################
    @property
    def value(self):
        return self.__local_value

    @property
    def config_dialog(self) -> ICConfigDialogTemplate:
        return self._config_dialog

    @property
    def label_color(self) -> QtGui.QColor:
        return self._label_color

    @label_color.setter
    def label_color(self, clr: QtGui.QColor) -> None:
        self._label_color = clr
        self.update()

    @property
    def label_text_size(self) -> int:
        return self._label_text_size

    @label_text_size.setter
    def label_text_size(self, sz: int) -> None:
        self._label_text_size = sz
        self.update()

    ####################################
    # Override
    ####################################
    def paintEvent(self, e):
        # for hidden button nothing to draw
        if self.state == ICWidgetState.Hidden:
            return

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # draw the base button
        self.name = self._config_dialog.display_value
        super().redraw(painter, (self._label_text_size + 15)/2)

        ##################################
        # draw the text only if it is visible
        ##################################
        if self.state in (ICWidgetState.VisibleEnabled, ICWidgetState.VisibleDisabled):
            temp_width = painter.device().width()
            temp_height = painter.device().height()

            # setup the pen
            pen = QtGui.QPen(self._label_color)
            pen.setWidth(1)
            painter.setPen(pen)

            # setup the font
            fnt = painter.font()
            fnt.setPixelSize(self._label_text_size)
            fnt.setBold(True)
            painter.setFont(fnt)

            # draw the title
            rect = QtCore.QRect(10, 10, temp_width - 20, self._label_text_size + 5)
            painter.drawText(rect, Qt.AlignLeft, self._config_dialog.title)

            # draw the unit
            painter.drawText(rect, Qt.AlignRight, self._config_dialog.unit)

            # calculate the dimensions to call additional draw
            temp_height = temp_height - (self._label_text_size + 15)
            painter.translate(0, self._label_text_size + 15)

            fnt.setPixelSize(self.text_size)
            font_matrices = QtGui.QFontMetrics(fnt)
            text_width = font_matrices.horizontalAdvance(self.name)

            # call to dialog for drawing additional elements
            self._config_dialog.draw_additional(painter, temp_width, temp_height, text_width, self.text_size)
