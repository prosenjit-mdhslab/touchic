# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 17:00:17 2020

@author: Prosenjit

TODO: popup dialog
"""

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal
from enum import Enum
from typing import Union
from .base_widget import ICBaseWidget, ICWidgetState
from .display_config import ICDisplayConfig
from .config_button import ICConfigDialogTemplate


class ICRadioType(Enum):
    RadioType = 0
    CheckBoxType = 1


class ICRadioOption(ICBaseWidget):
    """
    A class representing one radio box
    """

    # checked signal
    changed = pyqtSignal(str, bool)

    def __init__(self, option_name: str, is_selected: bool, selector_type: ICRadioType = ICRadioType.RadioType,
                 widget_id: int = 0, *args, **kwargs):
        super(ICRadioOption, self).__init__(widget_id, *args, **kwargs)

        # radio button option name
        self._option_name: str = option_name

        # state of the op
        self._is_selected: bool = is_selected

        # selector type
        self._selector_type: ICRadioType = selector_type

        # text size and color
        self._text_size: int = ICDisplayConfig.LabelTextSize
        self._text_color: QtGui.QColor = ICDisplayConfig.RadioBoxTextColor

        # radio box color
        self._radio_border_color: QtGui.QColor = ICDisplayConfig.RadioBoxBorderColor
        self._radio_fill_color: QtGui.QColor = ICDisplayConfig.RadioBoxFillColor

        # set up the size
        self.size_hint = (ICDisplayConfig.RadioButtonWidth, ICDisplayConfig.RadioButtonHeight)
        self.setFixedHeight(ICDisplayConfig.RadioButtonHeight)

        # set the options
        self.focusable = True
        self.clickable = True

        # override the default option
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)

    ###################################################
    # property
    ###################################################
    # get the name
    @property
    def name(self) -> str:
        return self._option_name

    @name.setter
    def name(self, nm: str) -> None:
        self._option_name = nm
        self.update()

    # get and set the checked state
    @property
    def checked(self) -> bool:
        return self._is_selected

    @checked.setter
    def checked(self, chk: bool) -> None:
        if self._is_selected != chk:
            self._is_selected = chk
            # for radio button the signal is emitted only when chk is Ture
            if self._selector_type == ICRadioType.RadioType:
                if chk:
                    self.changed.emit(self._option_name, self._is_selected)
            else:
                self.changed.emit(self._option_name, self._is_selected)
            self.update()

    # text size
    @property
    def text_size(self) -> int:
        return self._text_size

    @text_size.setter
    def text_size(self, sz: int) -> None:
        self._text_size = sz
        self.update()

    # text color
    @property
    def text_color(self) -> QtGui.QColor:
        return self._text_color

    @text_color.setter
    def text_color(self, clr: QtGui.QColor) -> None:
        self._text_color = clr
        self.update()

    # radio color
    @property
    def radio_colors(self) -> tuple[QtGui.QColor, QtGui.QColor]:
        return self._radio_border_color, self._radio_fill_color

    @radio_colors.setter
    def radio_colors(self, clrs: tuple[QtGui.QColor, QtGui.QColor]) -> None:
        self._radio_border_color = clrs[0]
        self._radio_fill_color = clrs[1]
        self.update()

    # selector type
    @property
    def selector_type(self) -> ICRadioType:
        return self._selector_type

    ###################################################
    # base class override
    ###################################################
    # override the click event
    def on_mouse_released(self, event: QtGui.QMouseEvent) -> None:
        if event.button() & Qt.LeftButton:
            if self._selector_type == ICRadioType.RadioType:
                # select if not selected
                if not self._is_selected:
                    self._is_selected = True
                    self.changed.emit(self._option_name, True)
                    self.update()
            else:
                # switch selection state
                self._is_selected = not self._is_selected
                self.changed.emit(self._option_name, self._is_selected)
                self.update()

    ###################################################
    # override and event handlers
    ###################################################
    def paintEvent(self, e) -> None:
        # nothing to do if hidden
        if self.state == ICWidgetState.Hidden:
            return

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # get the widget dimension
        tmp_width = painter.device().width()
        tmp_height = painter.device().height()

        # if widget is in focus then draw the focus selector
        if self.in_focus:
            # overall widget rect
            rect = QtCore.QRectF(1, 1, tmp_width - 2, tmp_height - 2)

            # define and set the path
            pen = QtGui.QPen(self.focus_color)
            pen.setWidth(3)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)

            # define the path and draw
            path = QtGui.QPainterPath()
            path.addRoundedRect(rect, 5, 5)
            painter.drawPath(path)

        # resize the drawing canvas
        tmp_width -= 6
        tmp_height -= 6
        painter.translate(3, 3)

        # set up the pen
        pen = QtGui.QPen()
        pen.setWidth(3)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        if self.state == ICWidgetState.Transparent:
            pen.setColor(self.background_color)
        else:
            pen.setColor(self._radio_border_color)
        painter.setPen(pen)

        if self._selector_type == ICRadioType.RadioType:
            radius = 0.5 * tmp_height
            painter.drawEllipse(QtCore.QPointF(radius, radius), radius - 10, radius - 10)
        else:
            rect = QtCore.QRectF(10, 10, tmp_height - 20, tmp_height - 20)
            painter.drawRect(rect)

        pen.setWidth(0)
        painter.setPen(pen)

        # set the brush to fill the selected area
        if self.state == ICWidgetState.Transparent:
            painter.setBrush(self.background_color)
        else:
            painter.setBrush(self._radio_fill_color)

        # draw the path
        path = QtGui.QPainterPath()
        path.setFillRule(Qt.WindingFill)
        if self._is_selected:
            if self._selector_type == ICRadioType.RadioType:
                path.addEllipse(QtCore.QPointF(radius, radius), radius - 15, radius - 15)
            else:
                rect = QtCore.QRectF(15, 15, tmp_height - 30, tmp_height - 30)
                path.addRoundedRect(rect, 3, 3)
            painter.drawPath(path)

        # draw the text only if the button is visible
        if self.state in (ICWidgetState.VisibleEnabled, ICWidgetState.VisibleDisabled):
            # define the font for drawing
            fnt = painter.font()
            if self._is_selected:
                fnt.setBold(True)
            fnt.setPixelSize(self._text_size)
            painter.setFont(fnt)

            pen.setColor(self._text_color)
            painter.setPen(pen)

            # draw the text
            rect = QtCore.QRectF(tmp_height, (tmp_height - self._text_size)/2, tmp_width - tmp_height, self._text_size + 5)
            painter.drawText(rect, Qt.AlignLeft, str(self._option_name))


class ICRadioGroup(ICBaseWidget):
    """
        A group of radio control
    """
    # value changed signal
    selection_changed = pyqtSignal(int)

    def __init__(self, option_names: list[str], option_codes: list[int] = None, selected: Union[str, int, list[int]] = None,
                 selector_type: ICRadioType = ICRadioType.RadioType, number_of_columns: int = 4, widget_id: int = 0, *args, **kwargs):
        super(ICRadioGroup, self).__init__(widget_id, *args, **kwargs)

        # setup the local variables
        self._option_names: list[str] = option_names

        # option codes
        if option_codes is None:
            self._option_codes = [i for i in range(len(option_names))]
        else:
            self._option_codes = option_codes

        # selected item is a list for checkbox and int for a radio box
        self._selected: Union[int, list[bool]]
        if selector_type == ICRadioType.CheckBoxType:
            self._selected = len(option_names) * [False]
            if type(selected) == list:
                for code in selected:
                    index = self._option_codes.index(code)
                    self._selected[index] = True
            elif type(selected) == int:
                index = self._option_codes.index(selected)
                self._selected[index] = True
            elif type(selected) == str:
                index = self._option_names.index(selected)
                self._selected[index] = True
        else:
            self._selected = self._option_codes[0]
            if type(selected) == int:
                if selected in self._option_codes:
                    self._selected = selected
            elif type(selected) == str:
                if selected in self._option_names:
                    index = self._option_names.index(selected)
                    self._selected: int = self._option_codes[index]

        # selector type
        self._selector_type = selector_type

        # setup basic behaviour
        self.clickable = False
        self.focusable = False

        # arrange in a Grid layout
        layout = QtWidgets.QGridLayout()
        row_num = 0
        col_num = 0

        # list of buttons
        self._buttons: list[ICRadioOption] = []

        for index, name in enumerate(self._option_names):
            # check if this item is in the selected list
            if selector_type == ICRadioType.RadioType:
                curr_selected: bool = (self._selected == self._option_codes[index])
            else:
                curr_selected: bool = self._selected[index]

            # create the button
            if curr_selected:
                self._buttons.append(ICRadioOption(name, True, self._selector_type))
            else:
                self._buttons.append(ICRadioOption(name, False, self._selector_type))

            # add the button to the grid
            layout.addWidget(self._buttons[index], row_num, col_num)

            # set up the event handler
            self._buttons[index].changed.connect(self.on_click)

            # update row and column number
            row_num = row_num if col_num < (number_of_columns - 1) else (row_num + 1)
            col_num = (col_num + 1) if col_num < (number_of_columns - 1) else 0

        self.setLayout(layout)

        # provide a size hint
        height_hint = 1.2 * row_num * ICDisplayConfig.RadioButtonHeight
        self.size_hint = (number_of_columns * ICDisplayConfig.RadioButtonWidth, height_hint)

    ###################################################
    # property
    ###################################################
    # values
    @property
    def option_codes(self) -> list[int]:
        return self._option_codes

    # displayed values
    @property
    def option_names(self) -> list[str]:
        return self._option_names

    @option_names.setter
    def option_names(self, dv: list[str]) -> None:
        self._option_names = dv
        self.update()

    # selected values returns the codes of the selected items
    # if codes were not defined then the return value is the index of the option_names
    @property
    def selected(self) -> Union[int, list[int]]:
        if self._selector_type == ICRadioType.RadioType:
            return self._selected
        else:
            selected = [self._option_codes[i] for i, x in enumerate(self._selected) if x is True]
            return selected

    @selected.setter
    def selected(self, curr: Union[str, int, list[int]]) -> None:
        if self._selector_type == ICRadioType.RadioType:
            # only one can be selected for radio button
            if type(curr) == str:
                if curr in self._option_names:
                    index = self._option_names.index(curr)
                    self._buttons[index].checked = True
            elif type(curr) == int:
                if curr in self._option_codes:
                    index = self._option_codes.index(curr)
                    self._buttons[index].checked = True
        else:
            # multiple buttons can be selected for a checkbox
            if type(curr) == list:
                # loop over all the elements
                for index, button in enumerate(self._buttons):
                    code = self._option_codes[index]
                    # check if the current value is in the input list
                    if code in curr:
                        self._buttons[index].checked = True
                    else:
                        self._buttons[index].checked = False
            elif type(curr) == int:
                # loop over all the elements
                for index, button in enumerate(self._buttons):
                    code = self._option_codes[index]
                    # check if the current value is in the input list
                    if code == curr:
                        self._buttons[index].checked = True
                    else:
                        self._buttons[index].checked = False

    # selector type
    @property
    def selector_type(self) -> ICRadioType:
        return self._selector_type

    ###################################################
    # slots
    ###################################################
    # @pyqtSlot(str, bool)
    def on_click(self, option_name: str, selected: bool) -> None:
        if self._selector_type == ICRadioType.RadioType:
            # only one can be selected

            # check if the provided name is in the available options
            if option_name not in self._option_names:
                return

            # get the index
            index = self._option_names.index(option_name)

            # change only if it is different from previous
            if self._option_codes[index] != self._selected:
                # unselect the old button
                old_index = self._option_codes.index(self._selected)
                self._buttons[old_index].checked = False
                self._buttons[old_index].update()
                self.append_history("unselected", self._selected)
                self._selected = self._option_codes[index]
                self.append_history("selected", self._selected)
                self.selection_changed.emit(self._selected)
        else:
            # multiple can be selected
            if option_name in self._option_names:
                index = self._option_names.index(option_name)
                self._selected[index] = selected
                self.selection_changed.emit(self._option_codes[index])


class ICRadioGroupDialog(ICConfigDialogTemplate):
    """
        A helper dialog class to for radio group
    """

    def __init__(self, option_names: list[str], option_codes: list[int] = None, selected: Union[str, int, list[int]] = None,
                 selector_type: ICRadioType = ICRadioType.RadioType, number_of_columns: int = 4, widget_id: int = 0, *args, **kwargs):
        super(ICRadioGroupDialog, self).__init__(*args, **kwargs)

        layout = QtWidgets.QVBoxLayout()

        self._radio_widget: ICRadioGroup = ICRadioGroup(option_names, option_codes, selected, selector_type, number_of_columns, widget_id)
        layout.addWidget(self._radio_widget)

        layout.addLayout(self.generate_ok_cancel_buttons())

        self.setLayout(layout)

    ########################################
    # property
    ########################################
    @property
    def radio_widget(self) -> ICRadioGroup:
        return self._radio_widget

    ####################################
    # Callback functions
    ####################################
    # called when ok is clicked
    def on_ok_clicked(self) -> None:
        # selected values
        self._value = self._radio_widget.selected

        # display value based on the selector
        if self._radio_widget.selector_type == ICRadioType.RadioType:
            index = self._radio_widget.option_codes.index(self._value)
            self._display_value = self._radio_widget.option_names[index]

        else:
            if len(self._value) > 0:
                index = self._radio_widget.option_codes.index(self._value[0])
                self._display_value = self._radio_widget.option_names[index]
            else:
                self._display_value = ""
