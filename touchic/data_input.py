# -*- coding: utf-8 -*-
"""
Created on May 23 2021

@author: Prosenjit

A class to input alpha numeric data
"""
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from typing import Union
from .display_config import ICDisplayConfig
from .base_widget import ICBaseWidget, ICWidgetState
from .basic_button import ICBasicButton
from .config_button import ICConfigDialogTemplate


class ICDataInputWidget (ICBaseWidget):
    """
        Class for alpha numeric input
    """

    def __init__(self, curr_val: Union[str, int, float], numeric_input: bool = True, widget_id: int = 0, *args, **kwargs):
        super(ICDataInputWidget, self).__init__(widget_id, *args, **kwargs)

        self._is_numeric_input: bool = numeric_input

        if numeric_input:
            # validate and fix curr_val type
            if not isinstance(curr_val, (int, float)):
                curr_val = 0

            self._num_value: Union[float, int] = curr_val

        else:
            self._num_value: Union[float, int] = 0

        self._str_value: str = str(curr_val)

        # setup numeric limit parameters
        self._decimal_places: int = 8
        self._max_limit: Union[float, None] = None
        self._min_limit: Union[float, None] = None

        # setup text size limit parameters
        self._max_characters: int = 24

        # setup the layout
        layout = QtWidgets.QVBoxLayout()

        self._value_display = QtWidgets.QLabel("", self)
        self._value_display.setStyleSheet("QLabel { background-color : " + ICDisplayConfig.QtColorToSting(self.background_color) + "; color : " +
                                          ICDisplayConfig.QtColorToSting(ICDisplayConfig.ValueTextColor) + "; border-radius : 5px; border-style : solid; " +
                                          "border-width : 2px; border-color : " + ICDisplayConfig.QtColorToSting(ICDisplayConfig.LabelBorderColor) + ";}")

        self._value_display.setAlignment(Qt.AlignRight)
        self._value_display.setText("<span style='font-size:" + "{}".format(ICDisplayConfig.LabelTextSize) + "pt;'>" + "{}".format(curr_val) + "</span>")
        layout.addWidget(self._value_display)

        but_lay = QtWidgets.QGridLayout()

        if numeric_input:
            self.__layout_numeric(but_lay)
        else:
            self.__layout_alpha(but_lay)

        layout.addLayout(but_lay)
        self.setLayout(layout)

        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)

        if numeric_input:
            self.size_hint = (ICDisplayConfig.DataInputNumericWidth, ICDisplayConfig.DataInputNumericHeight)
        else:
            self.size_hint = (ICDisplayConfig.DataInputAlphabetWidth, ICDisplayConfig.DataInputAlphabetHeight)

    """
        layout the numeric buttons
    """
    def __layout_numeric(self, but_lay: QtWidgets.QGridLayout):
        row_num = 0
        col_num = 0
        for i in range(10):
            button = ICBasicButton(str(i))
            button.clicked.connect(self.on_number_click)
            but_lay.addWidget(button, row_num, col_num)
            col_num += 1
            if col_num == 3:
                row_num += 1
                col_num = 0

        # decimal button
        self.dot_button: ICBasicButton = ICBasicButton(".")
        self.dot_button.clicked.connect(self.on_number_click)
        but_lay.addWidget(self.dot_button, row_num, col_num)

        row_num += 1
        col_num = 0

        # add -ve button
        self.neg_button = ICBasicButton("+/-")
        self.neg_button.clicked.connect(self.on_neg_click)
        but_lay.addWidget(self.neg_button, row_num, col_num)
        col_num += 1

        # add e (10^) button
        exp_button = ICBasicButton("E")
        exp_button.clicked.connect(self.on_exp_click)
        but_lay.addWidget(exp_button, row_num, col_num)
        col_num += 1

        # add backspace button
        button = ICBasicButton("<-")
        button.clicked.connect(self.on_back_click)
        but_lay.addWidget(button, row_num, col_num)

    """
        layout the alpha buttons
    """
    def __layout_alpha(self, but_lay: QtWidgets.QGridLayout):
        key_layout = [("Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"),
                      ("A", "S", "D", "F", "G", "H", "J", "K", "L", "<-"),
                      ("Z", "X", "C", "V", "B", "N", "M", "_", " ", ".")]

        for row_num, key_line in enumerate(key_layout):
            for col_num, key in enumerate(key_line):
                button = ICBasicButton(key)

                if key == "<-":
                    button.clicked.connect(self.on_back_click)
                else:
                    button.clicked.connect(self.on_alpha_click)

                but_lay.addWidget(button, row_num, col_num)

    ###############################################################
    # Properties
    ###############################################################
    @property
    def is_numeric(self) -> bool:
        return self._is_numeric_input

    @property
    def str_value(self) -> str:
        return self._str_value

    @property
    def number_value(self) -> float:
        if self._is_numeric_input:
            if self.final_check_value(self._str_value):
                self._num_value = float(self._str_value)
                return self._num_value

        return 0.0

    @property
    def decimal_places(self) -> int:
        return self._decimal_places

    @decimal_places.setter
    def decimal_places(self, places: int) -> None:
        # decimal places should be positive
        if places < 0:
            return

        # setup the decimal places
        self._decimal_places = places

        if self._is_numeric_input:
            if self._decimal_places == 0:
                self.dot_button.state = ICWidgetState.VisibleDisabled
            else:
                self.dot_button.state = ICWidgetState.VisibleEnabled

    @property
    def min_limit(self) -> float:
        return self._min_limit

    @min_limit.setter
    def min_limit(self, limit: float) -> None:
        # min limit should be smaller than the max limit
        if self._max_limit is not None:
            if limit > self._max_limit:
                return

        self._min_limit = limit

        if self._is_numeric_input:
            if self._min_limit > 0:
                self.neg_button.state = ICWidgetState.VisibleDisabled
            else:
                self.neg_button.state = ICWidgetState.VisibleEnabled

    @property
    def max_limit(self) -> float:
        return self._max_limit

    @max_limit.setter
    def max_limit(self, limit: float) -> None:
        # max limit should be larger than the min limit
        if self._min_limit is not None:
            if limit < self._min_limit:
                return

        self._max_limit = limit

    @property
    def max_characters(self) -> int:
        return self._max_characters

    @max_characters.setter
    def max_characters(self, limit: int) -> None:
        # at least one character has to be allowed
        if limit < 1:
            return

        self._max_characters = limit

        # readjust the text if required
        if len(self._str_value) > limit:
            self._str_value = self._str_value[:limit]
            self._value_display.setText("<span style='font-size:" + "{}".format(ICDisplayConfig.LabelTextSize) + "pt;'>" + "{}".format(self._str_value) + "</span>")

    ###############################################################
    # Helper functions
    ###############################################################
    """
        check if the current number is fine
    """
    def check_value(self, new_value: str):
        # check if it is a valid number
        try:
            num_value = float(new_value)
        except ValueError:
            print("not a number: " + new_value)
            return False

        # check precision
        x = new_value.split('.')
        if len(x) > 1:
            if len(x[1]) > self.decimal_places:
                return False

        return True

    """
        check if the current number is fine and within limits
    """
    def final_check_value(self, new_value: str):
        # check if it is a valid number
        try:
            num_val = float(new_value)
        except ValueError:
            print("not a number: " + new_value)
            return False

        # check if in range
        if self._min_limit is not None:
            if num_val < self._min_limit:
                return False

        if self._max_limit is not None:
            if num_val > self._max_limit:
                return False

        # check precision
        x = new_value.split('.')
        if len(x) > 1:
            if len(x[1]) > self.decimal_places:
                return False

        return True

    ###############################################################
    # Slots
    ###############################################################
    """
        Handle the number click event
    """
    def on_number_click(self, key):
        if self._str_value == "0" and key != ".":
            new_value = key
        else:
            new_value = self._str_value + key

        # check the numeric correctness of the value
        if self.check_value(new_value):
            self._str_value = new_value
            self._value_display.setText("<span style='font-size:" + "{}".format(ICDisplayConfig.LabelTextSize) + "pt;'>" + "{}".format(self._str_value) + "</span>")

    """
        Handle the number click event
    """
    def on_alpha_click(self, key):
        if len(self._str_value) < self._max_characters:
            self._str_value = self._str_value + key
            self._value_display.setText("<span style='font-size:" + "{}".format(ICDisplayConfig.LabelTextSize) + "pt;'>" + "{}".format(self._str_value) + "</span>")

    """
       Handle the backspace click event
    """
    def on_back_click(self, key):
        if self._is_numeric_input:
            if len(self._str_value) == 1:
                self._str_value = "0"
            else:
                self._str_value = self._str_value[:-1]

        else:
            if len(self._str_value) > 0:
                self._str_value = self._str_value[:-1]

        self._value_display.setText("<span style='font-size:" + "{}".format(ICDisplayConfig.LabelTextSize) + "pt;'>" + "{}".format(self._str_value) + "</span>")

    """
       Handle the negative sign click event
    """
    def on_neg_click(self, key):
        try:
            num_val = float(self._str_value)
        except ValueError:
            print("not a number: " + self._str_value)
            return

        if num_val == 0:
            return

        # check for "E"
        x = self._str_value.split("E")

        if len(x) > 1:
            # E exists
            power = x[1]
            # change the sign of the power
            if power[0] == "-":
                power = power[1:]
            else:
                power = "-" + power

            self._str_value = x[0] + "E" + power
        else:
            # E is not there
            if self._str_value[0] == "-":
                self._str_value = self._str_value[1:]
            else:
                self._str_value = "-" + self._str_value

        self._value_display.setText("<span style='font-size:" + "{}".format(ICDisplayConfig.LabelTextSize) + "pt;'>" + "{}".format(self._str_value) + "</span>")

    """
       Handle the E click event
    """
    def on_exp_click(self, key):
        # check for "E"
        x = self._str_value.split("E")

        if len(x) > 1:
            return

        self._str_value = self._str_value + "E0"
        self._value_display.setText("<span style='font-size:" + "{}".format(ICDisplayConfig.LabelTextSize) + "pt;'>" + "{}".format(self._str_value) + "</span>")


class ICDataInputDialog(ICConfigDialogTemplate):
    """
        A helper dialog class to for data input
    """
    def __init__(self, curr_val: Union[str, int, float], numeric_input: bool = True, widget_id: int = 0, *args, ** kwargs):
        super(ICDataInputDialog, self).__init__(*args, ** kwargs)

        layout = QtWidgets.QVBoxLayout()

        self._data_input_widget: ICDataInputWidget = ICDataInputWidget(curr_val, numeric_input, widget_id)
        layout.addWidget(self._data_input_widget)

        layout.addLayout(self.generate_ok_cancel_buttons())

        self.setLayout(layout)

    ########################################
    # property
    ########################################
    @property
    def data_input_widget(self) -> ICDataInputWidget:
        return self._data_input_widget

    ####################################
    # Callback functions
    ####################################
    # called when ok is clicked
    def on_ok_clicked(self) -> None:
        self._display_value = self._data_input_widget.str_value
        if self._data_input_widget.is_numeric:
            self._value = self._data_input_widget.number_value
        else:
            self._value = self._data_input_widget.str_value
