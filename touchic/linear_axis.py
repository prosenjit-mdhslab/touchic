# -*- coding: utf-8 -*-
"""
Created on May 24 2021

@author: Prosenjit

A linear axis for use with different widgets
"""

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from enum import Enum
from typing import Union
from .display_config import ICDisplayConfig
from .base_widget import ICBaseWidget, ICWidgetState, ICWidgetPosition


class ICLinearAxis(ICBaseWidget):
    """
        A linear axis class for use with different GUI widgets
    """
    AXIS_OFFSET = 0

    def __init__(self, label: str, values: list[float], displayed_values: list[str] = None, position: ICWidgetPosition = ICWidgetPosition.Bottom,
                 widget_id: int = 0, *args, **kwargs):
        super(ICLinearAxis, self).__init__(widget_id, *args, **kwargs)

        # format for tick labels
        self._tick_label_format: str = "{0:.0f}"

        # setup local variables
        self._label: str = label
        self._values: list[float] = values
        if displayed_values is not None:
            self._displayed_values: list[str] = displayed_values
        else:
            self._displayed_values: list[str] = [self._tick_label_format.format(x) for x in values]

        # should we draw the text labels
        self._drawing_labels: bool = True

        # tick color and text size
        self._tick_color: QtGui.QColor = ICDisplayConfig.LinearGaugeRulerColor
        self._tick_text_size: int = ICDisplayConfig.GeneralTextSize

        # margin left out on both sides of the scale
        self._margin: int = 0

        # click-ability and focus-ability
        self.focusable = False
        self.clickable = False

        # set the position of the axis with respect to the main widget
        self.position = position

        # display configuration
        if position.is_vertical():
            self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.MinimumExpanding)
        else:
            self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum)

    ########################################################
    # properties
    ########################################################
    # label get and set
    @property
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, lbl: str) -> None:
        self._label = lbl
        self.update()

    # are we drawing the labels?
    @property
    def drawing_labels(self) -> bool:
        return self._drawing_labels

    @drawing_labels.setter
    def drawing_labels(self, cond: bool) -> None:
        self._drawing_labels = cond
        self.update()

    # get the tick text size
    @property
    def tick_text_size(self) -> int:
        return self._tick_text_size

    # set the tick text size
    @tick_text_size.setter
    def tick_text_size(self, sz: int) -> None:
        self._tick_text_size = sz
        self.update()

    # get the tick color
    @property
    def tick_color(self) -> QtGui.QColor:
        return self._tick_color

    # set the tick color
    @tick_color.setter
    def tick_color(self, clr: QtGui.QColor) -> None:
        self._tick_color = clr
        self.update()

    # margin from the edge of the widget
    @property
    def margin(self) -> int:
        return self._margin

    @margin.setter
    def margin(self, x: int) -> None:
        self._margin = x
        self.update()

    # tick label format
    @property
    def tick_label_format(self) -> str:
        return self._tick_label_format

    # the labels need to be updated once the  format is updated
    @tick_label_format.setter
    def tick_label_format(self, fmt: str) -> None:
        self._tick_label_format = fmt
        for index, each_value in enumerate(self._values):
            self._displayed_values[index] = self._tick_label_format.format(each_value)
        self.update()

    ########################################################
    # functions
    ########################################################
    # update the values
    def update_value(self, index: int, value: float) -> None:
        self._values[index] = value
        self._displayed_values[index] = self._tick_label_format.format(value)
        self.update()

    # update displayed values
    def update_displayed_value(self, index: int, displayed_value: str) -> None:
        self._displayed_values[index] = displayed_value
        self.update()

    # estimate the widget size based on the text size
    def estimate_max_scale_width(self) -> int:
        # size required depends on the orientation of the widget
        if self.position.is_horizontal():
            if self._drawing_labels:
                if self._label:
                    return 2 * self._tick_text_size + 24
                else:
                    return self._tick_text_size + 14
            else:
                return 14
        else:
            # setup the font
            painter = QtGui.QPainter(self)
            fnt = painter.font()
            fnt.setPixelSize(self._tick_text_size)

            # create the font matrices
            font_matrices = QtGui.QFontMetrics(fnt)
            max_width: int = 0

            for value in self._displayed_values:
                temp_width = font_matrices.horizontalAdvance(value)
                max_width = max_width if max_width > temp_width else temp_width

            if self._drawing_labels:
                if self._label:
                    return 20 + max_width + self._tick_text_size
                else:
                    return 10 + max_width
            else:
                return 14

    ########################################################
    # base class override
    ########################################################
    def on_position_changed(self) -> None:
        if self.position.is_vertical():
            self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.MinimumExpanding)
        else:
            self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Maximum)

    ########################################################
    # override event handlers
    ########################################################
    # override the default paint event
    def paintEvent(self, e):
        # if not visible then nothing else to do
        if self.state not in (ICWidgetState.VisibleEnabled, ICWidgetState.VisibleDisabled):
            return

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # get the size of the containing widget
        tmp_width = painter.device().width()
        tmp_height = painter.device().height()

        ##########################################################
        # draw the scale line
        ##########################################################
        # modify the pen to draw the vertical or horizontal scale bar
        pen = QtGui.QPen()
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setWidth(3)
        pen.setBrush(self._tick_color)
        painter.setPen(pen)

        # calculate and draw the vertical or horizontal line
        min_slide = self._margin
        if self.position == ICWidgetPosition.Left:
            max_slide = tmp_height - self._margin
            rule_loc = tmp_width - self.AXIS_OFFSET

            # draw the scale line
            painter.drawLine(QtCore.QPointF(rule_loc, min_slide), QtCore.QPointF(rule_loc, max_slide))

        elif self.position == ICWidgetPosition.Right:
            max_slide = tmp_height - self._margin
            rule_loc = self.AXIS_OFFSET

            # draw the scale line
            painter.drawLine(QtCore.QPointF(rule_loc, min_slide), QtCore.QPointF(rule_loc, max_slide))

        elif self.position == ICWidgetPosition.Bottom:
            max_slide = tmp_width - self._margin
            rule_loc = self.AXIS_OFFSET

            # draw the scale line
            painter.drawLine(QtCore.QPointF(min_slide, rule_loc), QtCore.QPointF(max_slide, rule_loc))

        else:
            max_slide = tmp_width - self._margin
            rule_loc = tmp_height - self.AXIS_OFFSET

            # draw the scale line
            painter.drawLine(QtCore.QPointF(min_slide, rule_loc),  QtCore.QPointF(max_slide, rule_loc))

        # modify the font to write the scale
        fnt = painter.font()
        fnt.setPixelSize(self._tick_text_size)
        painter.setFont(fnt)

        #############################################
        # draw the ticks and tick labels
        #############################################
        curr_index = 0
        max_index = len(self._values)

        # length of slide in pixels
        slide_length = max_slide - min_slide

        # space between the ticks in pixels
        delta_x = ((self._values[1] - self._values[0]) / (self._values[-1] - self._values[0])) * slide_length

        # draw the ticks
        while curr_index < max_index:
            # calculate the location for drawing the tick
            tick_pos = min_slide + slide_length * ((self._values[curr_index] - self._values[0]) / (self._values[-1] - self._values[0]))

            if self.position.is_horizontal():
                # calculate the position to draw the text
                if self._drawing_labels:
                    # calculate the position to draw the text
                    tick_pos_c = tick_pos - 0.5 * delta_x
                    align = Qt.AlignCenter

                    # correct for the corner cases
                    if curr_index == 0:
                        tick_pos_c = tick_pos
                        align = Qt.AlignLeft
                    elif curr_index == (max_index - 1):
                        tick_pos_c = tick_pos - delta_x
                        align = Qt.AlignRight

                # draw the tick
                if self.position == ICWidgetPosition.Bottom:
                    painter.drawLine(QtCore.QPointF(tick_pos, rule_loc), QtCore.QPointF(tick_pos, rule_loc + 5))

                    # if text is enabled then draw the text
                    if self._drawing_labels:
                        rect = QtCore.QRectF(tick_pos_c, rule_loc + 7, delta_x, self._tick_text_size + 5)
                        painter.drawText(rect, align, self._displayed_values[curr_index])

                elif self.position == ICWidgetPosition.Top:
                    # draw the tick
                    painter.drawLine(QtCore.QPointF(tick_pos, rule_loc), QtCore.QPointF(tick_pos, rule_loc - 5))

                    # if text is enabled then draw the text
                    if self._drawing_labels:
                        rect = QtCore.QRectF(tick_pos_c, rule_loc - 12 - self._tick_text_size, delta_x, self._tick_text_size + 5)
                        painter.drawText(rect, align, self._displayed_values[curr_index])

            else:
                # calculate the position to draw the text
                if self._drawing_labels:
                    start_y = tick_pos
                    start_y = start_y if curr_index == 0 else (start_y - 0.5 * self._tick_text_size)
                    start_y = (start_y - 0.5 * self._tick_text_size - 3) if curr_index == max_index - 1 else start_y

                if self.position == ICWidgetPosition.Left:
                    # draw the tick
                    painter.drawLine(QtCore.QPointF(rule_loc, tick_pos), QtCore.QPointF(rule_loc - 5, tick_pos))

                    # if text is enabled then draw the text
                    if self._drawing_labels:
                        rect = QtCore.QRectF(0, start_y, rule_loc - 7, self._tick_text_size + 5)
                        painter.drawText(rect, Qt.AlignRight, self._displayed_values[max_index - 1 - curr_index])

                else:
                    # draw the tick
                    painter.drawLine(QtCore.QPointF(rule_loc, tick_pos), QtCore.QPointF(rule_loc + 5, tick_pos))

                # if text is enabled then draw the text
                if self._drawing_labels:
                    rect = QtCore.QRectF(7, start_y, tmp_width - rule_loc - 7, self._tick_text_size + 5)
                    painter.drawText(rect, Qt.AlignLeft, self._displayed_values[max_index - 1 - curr_index])

            # increment the index
            curr_index += 1

        ##################################################
        # draw the axis label
        ##################################################
        if self._drawing_labels and self._label:
            half_text_size = int(self._tick_text_size/2)

            if self.position.is_vertical():
                rect = QtCore.QRect(-50, -half_text_size - 3, 100, self._tick_text_size + 6)
                if self.position == ICWidgetPosition.Left:
                    painter.translate(half_text_size + 3, tmp_height / 2.0)
                else:
                    painter.translate(tmp_width - half_text_size - 3, tmp_height / 2.0)
                painter.rotate(90)
                painter.drawText(rect, Qt.AlignHCenter, self._label)

            else:
                if self.position == ICWidgetPosition.Top:
                    rect = QtCore.QRectF(tmp_width/2 - 50, 3, 100, self._tick_text_size + 5)
                else:
                    rect = QtCore.QRectF(tmp_width / 2 - 50, tmp_height - (self._tick_text_size + 5), 100, self._tick_text_size + 5)
                painter.drawText(rect, Qt.AlignHCenter, self._label)

    ########################################################
    # helper functions
    ########################################################
    # update ticks
    def update_ticks(self, max_value: float, min_value: float) -> None:
        # get the number of steps in display from the current length
        display_steps = len(self._values) - 1

        # add the first element
        self._values[0] = min_value
        self._displayed_values[0] = self._tick_label_format.format(min_value)

        # loop for other elements
        index = 1
        value_step = (max_value - min_value) / display_steps

        while index < display_steps:
            self._values[index] = self._values[index - 1] + value_step
            self._displayed_values[index] = self._tick_label_format.format(self._values[index])
            index += 1

        # add the last element
        self._values[display_steps] = max_value
        self._displayed_values[display_steps] = self._tick_label_format.format(max_value)

        # update the view
        self.update()

    # create the value and displayed value lists from max an min range
    @staticmethod
    def create_ticks(max_value: float, min_value: float, display_steps: int, format_str: str) -> [list[float], list[str]]:
        # pre-allocate memory
        values = (display_steps + 1) * [0.0]
        displayed_values = (display_steps + 1) * [""]

        # add the first element
        values[0] = min_value
        displayed_values[0] = format_str.format(min_value)

        # loop for other elements
        index = 1
        value_step = (max_value - min_value) / display_steps

        while index < display_steps:
            values[index] = values[index - 1] + value_step
            displayed_values[index] = format_str.format(values[index])
            index += 1

        # add the last element
        values[display_steps] = max_value
        displayed_values[display_steps] = format_str.format(max_value)

        return values, displayed_values

    # create the value and displayed value lists from
    @staticmethod
    def select_ticks(values: list[float], displayed_values: list[str], display_steps: int) -> [list[float], list[str]]:
        # pre-allocate memory
        selected_values = (display_steps + 1) * [0.0]
        selected_displayed_values = (display_steps + 1) * [""]

        # add the first element
        selected_values[0] = values[0]
        selected_displayed_values[0] = displayed_values[0]

        # loop for other elements
        index = 1
        value_step = (values[-1] - values[0]) / display_steps

        while index < display_steps:
            next_value = selected_values[index - 1] + value_step

            # find the next viable value in the list
            gap = [abs(x - next_value) for x in values]
            min_index = gap.index(min(gap))

            selected_values[index] = values[min_index]
            selected_displayed_values[index] = displayed_values[min_index]

            index += 1

        # add the last element
        selected_values[-1] = values[-1]
        selected_displayed_values[-1] = displayed_values[-1]

        return selected_values, selected_displayed_values


class ICLinearContainerType(Enum):
    BAR = 1
    BAR_NO_TITLE = 2
    BAR_NO_VALUE = 3
    BAR_NO_TITLE_NO_VALUE = 4
    PLOT = 5
    PLOT_NO_TITLE = 6
    PLOT_NO_VALUE = 7
    PLOT_NO_TITLE_NO_VALUE = 8


class ICLinearAxisContainer(ICBaseWidget):
    """
        Container class to plot a widget with
        1. one scale with optional title and value
        2. two scales with optional title and value
    """
    LAYOUT_MAP_BAR = {
        ICWidgetPosition.Left: {
            "title": (0, 0, 1, 3),
            "value": (4, 0, 1, 3),
            "scale": (1, 0, 3, 1),
            "gauge": (1, 1, 3, 2)
        },
        ICWidgetPosition.Right: {
            "title": (0, 0, 1, 3),
            "value": (4, 0, 1, 3),
            "scale": (1, 2, 3, 1),
            "gauge": (1, 0, 3, 2)
        },
        ICWidgetPosition.Bottom: {
            "title": (3, 0, 1, 1),
            "value": (3, 1, 1, 1),
            "scale": (2, 0, 1, 3),
            "gauge": (0, 0, 2, 3)
        },
        ICWidgetPosition.Top: {
            "title": (3, 0, 1, 1),
            "value": (3, 1, 1, 1),
            "scale": (0, 0, 1, 3),
            "gauge": (1, 0, 2, 3)
        }
    }

    LAYOUT_MAP_BAR_NOT = {
        ICWidgetPosition.Left: {
            "value": (3, 0, 1, 3),
            "scale": (0, 0, 3, 1),
            "gauge": (0, 1, 3, 2)
        },
        ICWidgetPosition.Right: {
            "value": (3, 0, 1, 3),
            "scale": (0, 2, 3, 1),
            "gauge": (0, 0, 3, 2)
        },
        ICWidgetPosition.Bottom: {
            "value": (3, 1, 1, 1),
            "scale": (2, 0, 1, 3),
            "gauge": (0, 0, 2, 3)
        },
        ICWidgetPosition.Top: {
            "value": (3, 1, 1, 1),
            "scale": (0, 0, 1, 3),
            "gauge": (1, 0, 2, 3)
        }
    }

    LAYOUT_MAP_BAR_NOT_NOV = {
        ICWidgetPosition.Left: {
            "scale": (0, 0, 3, 1),
            "gauge": (0, 1, 3, 2)
        },
        ICWidgetPosition.Right: {
            "scale": (0, 2, 3, 1),
            "gauge": (0, 0, 3, 2)
        },
        ICWidgetPosition.Bottom: {
            "scale": (2, 0, 1, 3),
            "gauge": (0, 0, 2, 3)
        },
        ICWidgetPosition.Top: {
            "scale": (0, 0, 1, 3),
            "gauge": (1, 0, 2, 3)
        }
    }

    LAYOUT_MAP_PLOT = {
        ICWidgetPosition.Left: {
            "scale": (1, 0, 2, 1)
        },
        ICWidgetPosition.Right: {
            "scale": (1, 3, 2, 1)
        },
        ICWidgetPosition.Bottom: {
            "scale": (3, 1, 1, 2)
        },
        ICWidgetPosition.Top: {
            "scale": (0, 1, 1, 2)
        }
    }

    def __init__(self, container_type: ICLinearContainerType, widget_id: int = 0, *args, **kwargs):
        super(ICLinearAxisContainer, self).__init__(widget_id, *args, **kwargs)

        # container type: fixed. container map determines the layout
        self.__container_type: ICLinearContainerType = container_type
        if container_type == ICLinearContainerType.BAR:
            self.__container_map = self.LAYOUT_MAP_BAR
        elif container_type in (ICLinearContainerType.BAR_NO_VALUE, ICLinearContainerType.BAR_NO_TITLE):
            self.__container_map = self.LAYOUT_MAP_BAR_NOT
        elif container_type == ICLinearContainerType.BAR_NO_TITLE_NO_VALUE:
            self.__container_map = self.LAYOUT_MAP_BAR_NOT_NOV
        else:
            self.__container_map = self.LAYOUT_MAP_PLOT

        # create the local variables
        self._title: str = ""
        self._value: float = 0.0
        self._unit: str = ""

        # title and value text color
        self._title_color: QtGui.QColor = ICDisplayConfig.HeaderTextColor
        self._value_color: QtGui.QColor = ICDisplayConfig.ValueTextColor

        # value color for alarm condition
        self._error_back_color: QtGui.QColor = ICDisplayConfig.ErrorTextBackColor
        self._error_text_color: QtGui.QColor = ICDisplayConfig.ErrorTextColor

        # title, value and unit text size
        self._title_size: int = ICDisplayConfig.LabelTextSize
        self._value_size: int = ICDisplayConfig.LabelTextSize
        self._unit_size: int = ICDisplayConfig.UnitTextSize

        # format changed
        self._title_format_changed: bool = False
        self._value_format_changed: bool = False

        # last alarm status
        self._alarmed = False

        # the central widget
        self._central_widget = None

        # the first scale bar
        self.scale_bar_one = None

        # the second scale bar
        self.scale_bar_two = None

        #########################################################
        # create the title and value
        #########################################################
        # add title display label
        self._title_display = None
        if self.__container_type in (ICLinearContainerType.PLOT, ICLinearContainerType.PLOT_NO_VALUE, ICLinearContainerType.BAR,
                                     ICLinearContainerType.BAR_NO_VALUE):
            self._title_display = QtWidgets.QLabel("", self)
            self._title_display.setStyleSheet("QLabel { background-color : " + ICDisplayConfig.QtColorToSting(self.background_color) + "; color : " +
                                              ICDisplayConfig.QtColorToSting(self._title_color) + ";}")
            self._title_display.setAlignment(Qt.AlignCenter)

        # add display value label
        self._value_display = None
        if self.__container_type in (ICLinearContainerType.PLOT, ICLinearContainerType.PLOT_NO_TITLE, ICLinearContainerType.BAR,
                                     ICLinearContainerType.BAR_NO_TITLE):
            self._value_display = QtWidgets.QLabel("", self)
            self._value_display.setStyleSheet("QLabel { background-color : " + ICDisplayConfig.QtColorToSting(self.background_color) + "; color : " +
                                              ICDisplayConfig.QtColorToSting(self._value_color) + "; border-radius : 5px; }")

        # create the grid layout
        self._layout: QtWidgets.QGridLayout = QtWidgets.QGridLayout()
        self.setLayout(self._layout)

        # fix maximum dimension of the widget
        self._maximum_vertical_width: int = QtWidgets.QWIDGETSIZE_MAX
        self._maximum_horizontal_height: int = QtWidgets.QWIDGETSIZE_MAX

        # set the parameters for the base class
        self.focusable = True
        self.clickable = False

        # override the base Size policy
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)

        # setup the layout
        self._update_layout()

    ########################################################
    # functions to add elements
    ########################################################
    # add the central widget
    def add_central_widget(self, central_widget: ICBaseWidget) -> None:
        self._central_widget = central_widget
        self.position = central_widget.position
        self._update_layout()

    # add the first scale bar
    def add_first_scale_bar(self, label: str, values: list[float], displayed_values: list[str], position: ICWidgetPosition) -> ICLinearAxis:
        self.scale_bar_one: ICLinearAxis = ICLinearAxis(label, values, displayed_values, position)
        self._update_layout()
        return self.scale_bar_one

    # add the second scale bar
    def add_second_scale_bar(self, label: str, values: list[float], displayed_values: list[str], position: ICWidgetPosition) -> Union[ICLinearAxis, None]:
        if self.__container_type in (ICLinearContainerType.PLOT, ICLinearContainerType.PLOT_NO_VALUE, ICLinearContainerType.PLOT_NO_TITLE,
                                     ICLinearContainerType.PLOT_NO_TITLE_NO_VALUE):
            self.scale_bar_two: ICLinearAxis = ICLinearAxis(label, values, displayed_values, position)
            self._update_layout()
        return self.scale_bar_two

    ########################################################
    # properties
    ########################################################
    # get the gauge title
    @property
    def title(self) -> str:
        return self._title

    # set the gauge title
    @title.setter
    def title(self, nm: str) -> None:
        self._title = nm
        self._title_update()

    # get current value of the gauge
    @property
    def value(self) -> float:
        return self._value

    # set the current value of the gauge
    @value.setter
    def value(self, val: float) -> None:
        # first set the value for the gauge where limit check takes place
        if self._value != val:
            self._value = val
            self._value_update()

            # allow the subclass to change itself
            self.on_value_update(self._value)

    # get the current unit
    @property
    def unit(self) -> str:
        return self._unit

    # set the gauge unit
    @unit.setter
    def unit(self, un: str) -> None:
        self._unit = un
        self._local_update()

    # For plot type widgets the scale bar positions are changed independently.
    @property
    def first_scale_position(self) -> ICWidgetPosition:
        return None if self.scale_bar_one is None else self.scale_bar_one.position

    @first_scale_position.setter
    def first_scale_position(self, position: ICWidgetPosition) -> None:
        # this property is only for plot type widgets
        if self.__container_type in (ICLinearContainerType.BAR, ICLinearContainerType.BAR_NO_TITLE, ICLinearContainerType.BAR_NO_VALUE,
                                     ICLinearContainerType.BAR_NO_TITLE_NO_VALUE) or (self.scale_bar_one is None):
            return

        # if same as the previous position then nothing to do
        if self.scale_bar_one.position == position:
            return

        # update the scale bar and self position
        self.scale_bar_one.position = position

        # update the display
        self._update_layout()

    # second scale bar position
    @property
    def second_scale_position(self) -> ICWidgetPosition:
        return None if self.scale_bar_two is None else self.scale_bar_two.position

    @second_scale_position.setter
    def second_scale_position(self, position: ICWidgetPosition) -> None:
        # this property is valid
        #   only for plot type widgets and
        #   when the second scale bar exists
        if (self.__container_type in (ICLinearContainerType.BAR, ICLinearContainerType.BAR_NO_TITLE, ICLinearContainerType.BAR_NO_VALUE,
                                      ICLinearContainerType.BAR_NO_TITLE_NO_VALUE)) or (self.scale_bar_two is None):
            return

        # proceed only if the new position is not the same as old position
        if self.scale_bar_two.position == position:
            return

        # update the orientation
        self.scale_bar_two.position = position

        # update the display
        self._update_layout()

    # synonym for first scale position for bar type widgets.
    @property
    def scale_position(self) -> ICWidgetPosition:
        return None if self.scale_bar_one is None else self.scale_bar_one.position

    # For bar type widgets the central widget position is synchronised with that of the first scale bar.
    @scale_position.setter
    def scale_position(self, position: ICWidgetPosition) -> None:
        if self.scale_bar_one is None:
            return

        # this property is only for bar type widgets
        if self.__container_type in (ICLinearContainerType.BAR, ICLinearContainerType.BAR_NO_TITLE, ICLinearContainerType.BAR_NO_VALUE,
                                     ICLinearContainerType.BAR_NO_TITLE_NO_VALUE):

            # if same as the previous position then nothing to do
            if self.scale_bar_one.position == position:
                return

            # set the scale bar position
            self.scale_bar_one.position = position

            # set the position of the central widget
            widget_position = ICWidgetPosition.opposite(position)
            self._central_widget.position = widget_position

            # change the position of the container
            self.position = widget_position

            # update the display
            self._update_layout()

    # central widget position property for bar type widgets
    @property
    def widget_position(self) -> ICWidgetPosition:
        return None if self._central_widget is None else self._central_widget.position

    @widget_position.setter
    def widget_position(self, position: ICWidgetPosition) -> None:
        if self._central_widget is None:
            return

        # this property is only for bar type widgets
        if self.__container_type in (ICLinearContainerType.BAR, ICLinearContainerType.BAR_NO_TITLE, ICLinearContainerType.BAR_NO_VALUE,
                                     ICLinearContainerType.BAR_NO_TITLE_NO_VALUE):

            # if same as the previous position then nothing to do
            if self._central_widget.position == position:
                return

            # set the position of the central widget
            self._central_widget.position = position

            # set the scale bar position
            scale_position = ICWidgetPosition.opposite(position)
            self.scale_bar_one.position = scale_position

            # change the position of the container.
            self.position = position

            # update the display
            self._update_layout()

    @property
    def first_scale_bar(self) -> ICLinearAxis:
        return self.scale_bar_one

    @property
    def second_scale_bar(self) -> ICLinearAxis:
        return self.scale_bar_two

    # get the color of the title
    @property
    def title_text_color(self) -> QtGui.QColor:
        return self._title_color

    # set the title color
    @title_text_color.setter
    def title_text_color(self, clr: QtGui.QColor) -> None:
        self._title_color = clr
        self._title_format_changed = True
        self._title_update()

    # get the color of the title
    @property
    def value_text_color(self) -> QtGui.QColor:
        return self._value_color

    # set the title color
    @value_text_color.setter
    def value_text_color(self, clr: QtGui.QColor) -> None:
        self._value_color = clr
        self._value_format_changed = True
        self._value_update()

    # get the color of alarm text
    @property
    def alarm_colors(self) -> tuple[QtGui.QColor, QtGui.QColor]:
        return self._error_back_color, self._error_text_color

    # set the color of alarm text
    @alarm_colors.setter
    def alarm_colors(self, clrs: tuple[QtGui.QColor, QtGui.QColor]) -> None:
        self._error_back_color = clrs[0]
        self._error_text_color = clrs[1]
        self._value_update()

    # get the size of the title text
    @property
    def title_size(self) -> int:
        return self._title_size

    # set the size of the title text
    @title_size.setter
    def title_size(self, sz: int) -> None:
        self._title_size = sz
        self._title_format_changed = True
        self._title_update()

    # get the size of the value text
    @property
    def value_size(self) -> int:
        return self._value_size

    # set the size of the title text
    @value_size.setter
    def value_size(self, sz: int) -> None:
        self._value_size = sz
        self._value_format_changed = True
        self._value_update()

    # get the size of the title text
    @property
    def unit_size(self) -> int:
        return self._unit_size

    # set the size of the title text
    @unit_size.setter
    def unit_size(self, sz: int) -> None:
        self._unit_size = sz
        self._title_format_changed = True
        self._value_format_changed = True
        self._local_update()

    # get the maximum width of the vertical gauge
    @property
    def vertical_gauge_width(self) -> int:
        return self._maximum_vertical_width

    # set the maximum width of the vertical gauge
    @vertical_gauge_width.setter
    def vertical_gauge_width(self, wd: int) -> None:
        self._maximum_vertical_width = wd
        if self.position.is_vertical():
            self.setMaximumSize(self._maximum_vertical_width, QtWidgets.QWIDGETSIZE_MAX)
        self._local_update()

    # get the maximum height of the horizontal gauge
    @property
    def horizontal_gauge_height(self) -> int:
        return self._maximum_horizontal_height

    # set the maximum height of the horizontal gauge
    @horizontal_gauge_height.setter
    def horizontal_gauge_height(self, ht: int) -> None:
        self._maximum_horizontal_height = ht
        if self.position.is_horizontal():
            self.setMaximumSize(QtWidgets.QWIDGETSIZE_MAX, self._maximum_horizontal_height)
        self._local_update()

    ########################################################
    # slots
    ########################################################
    # handles the signal for value update
    # @pyqtSlot(float)
    def value_changed(self, val: float) -> None:
        self.value = val

    ########################################################
    # subclass callback functions
    ########################################################
    # called when layout has been changed. sub-classes can reimplement this to update themselves
    def on_layout_update(self) -> None:
        pass

    # called when value has been changed. sub-classes can reimplement this to update themselves
    def on_value_update(self, value: float) -> None:
        pass

    ########################################################
    # layout management functions
    ########################################################
    # setup display for BAR type
    def _update_layout_bar(self) -> None:
        if self.position.is_horizontal():
            self.setMaximumSize(QtWidgets.QWIDGETSIZE_MAX, self._maximum_horizontal_height)
        else:
            self.setMaximumSize(self._maximum_vertical_width, QtWidgets.QWIDGETSIZE_MAX)

        # get the position map based on the scale bar position
        scale_position = ICWidgetPosition.opposite(self.position)
        pos_map = self.__container_map[scale_position]

        # place the gauge
        index = self._layout.indexOf(self._central_widget)
        if index >= 0:
            _ = self._layout.takeAt(index)
        x = pos_map["gauge"]
        self._layout.addWidget(self._central_widget, x[0], x[1], x[2], x[3])

        # place the scale
        if self.scale_bar_one is not None:
            index = self._layout.indexOf(self.scale_bar_one)
            if index >= 0:
                _ = self._layout.takeAt(index)
            x = pos_map["scale"]
            self._layout.addWidget(self.scale_bar_one, x[0], x[1], x[2], x[3])

        # place the title
        if self.__container_type in (ICLinearContainerType.BAR, ICLinearContainerType.BAR_NO_VALUE):
            index = self._layout.indexOf(self._title_display)
            if index >= 0:
                _ = self._layout.takeAt(index)
            x = pos_map["title"]
            self._layout.addWidget(self._title_display, x[0], x[1], x[2], x[3])

        # place the value
        if self.__container_type in (ICLinearContainerType.BAR, ICLinearContainerType.BAR_NO_TITLE):
            index = self._layout.indexOf(self._value_display)
            if index >= 0:
                _ = self._layout.takeAt(index)
            x = pos_map["value"]
            self._layout.addWidget(self._value_display, x[0], x[1], x[2], x[3])

    # setup display for PLOT type
    def _update_layout_plot(self) -> None:
        # place the plot
        index = self._layout.indexOf(self._central_widget)
        if index >= 0:
            _ = self._layout.takeAt(index)
        self._layout.addWidget(self._central_widget, 1, 1, 2, 2)

        # place the first scale
        if self.scale_bar_one is not None:
            pos_map_one = self.__container_map[self.scale_bar_one.position]
            index = self._layout.indexOf(self.scale_bar_one)
            if index >= 0:
                _ = self._layout.takeAt(index)
            x = pos_map_one["scale"]
            self._layout.addWidget(self.scale_bar_one, x[0], x[1], x[2], x[3])

        # check if the second bar exists
        if self.scale_bar_two is not None:
            pos_map_two = self.__container_map[self.scale_bar_two.position]
            # place the second scale
            index = self._layout.indexOf(self.scale_bar_two)
            if index >= 0:
                _ = self._layout.takeAt(index)
            x = pos_map_two["scale"]
            self._layout.addWidget(self.scale_bar_two, x[0], x[1], x[2], x[3])

        # place the title
        if self.__container_type in (ICLinearContainerType.PLOT, ICLinearContainerType.PLOT_NO_VALUE):
            index = self._layout.indexOf(self._title_display)
            # place if it has not been placed
            if index < 0:
                self._layout.addWidget(self._title_display, 4, 1, 1, 1)

        # place the value
        if self.__container_type in (ICLinearContainerType.PLOT, ICLinearContainerType.PLOT_NO_TITLE):
            index = self._layout.indexOf(self._value_display)
            # place if it has not been placed
            if index < 0:
                self._layout.addWidget(self._value_display, 4, 2, 1, 1)

    # setup display
    def _update_layout(self) -> None:

        if self.__container_type in (ICLinearContainerType.PLOT, ICLinearContainerType.PLOT_NO_TITLE, ICLinearContainerType.PLOT_NO_VALUE,
                                     ICLinearContainerType.PLOT_NO_TITLE_NO_VALUE):
            # update only if the central widget is set
            if self._central_widget is None:
                return

            self._update_layout_plot()
        else:
            # update only if central widget is set
            if self._central_widget is None:
                return

            self._update_layout_bar()

        # notify the subclass about change in the layout
        self.on_layout_update()
        self.update()

    # update title
    def _title_update(self) -> None:
        # nothing to do if hidden
        if self.state == ICWidgetState.Hidden or self._title_display is None:
            return

        # set up the display style
        if self._title_format_changed:
            self._title_display.setStyleSheet("QLabel { background-color : " + ICDisplayConfig.QtColorToSting(self.background_color) + "; color : " +
                                              ICDisplayConfig.QtColorToSting(self._title_color) + ";}")
            self._title_format_changed = False

        # update the text based on the state
        if self.state in (ICWidgetState.Transparent, ICWidgetState.FrameOnly):
            self._title_display.setText("<span style='font-size:" + "{}".format(self._title_size) + "pt;'>" + "</span><span style='font-size:" +
                                        "{}".format(self._unit_size) + "pt;'></span>")
        else:
            if self._unit:
                self._title_display.setText("<span style='font-size:" + "{}".format(self._title_size) + "pt;'>" + self._title +
                                            "</span> <span style='font-size:" + "{}".format(self._unit_size) + "pt;'>(" + self._unit + ")</span>")
            else:
                self._title_display.setText("<span style='font-size:" + "{}".format(self._title_size) + "pt;'>" + self._title + "</span>")

        # update the title
        self._title_display.update()

    # update value
    def _value_update(self):
        # nothing to do if hidden
        if self.state == ICWidgetState.Hidden or self._value_display is None or self._central_widget is None:
            return

        # update the value based on widget visibility state
        self._value_display.setAlignment(Qt.AlignCenter)
        if self.state in (ICWidgetState.Transparent, ICWidgetState.FrameOnly):
            # set background color and do not draw
            self._value_display.setStyleSheet("QLabel { background-color : " + ICDisplayConfig.QtColorToSting(self.background_color) + "; color : " +
                                              ICDisplayConfig.QtColorToSting(self._value_color) + "; border-radius : 5px;}")
            self._value_display.setText("<span style='font-size:" + "{}".format(self._value_size) + "pt;'> </span> <span style='font-size:" +
                                        "{}".format(self._unit_size) + "pt;'></span>")
        else:
            # change if alarm status changed or format changed
            if self._central_widget.alarm_activated != self._alarmed or self._value_format_changed:
                self._alarmed = self._central_widget.alarm_activated
                # select format based on  alarm state
                if self._central_widget.alarm_activated:
                    self._value_display.setStyleSheet("QLabel { background-color : " + ICDisplayConfig.QtColorToSting(self._error_back_color) +
                                                      "; color : " + ICDisplayConfig.QtColorToSting(self._error_text_color) + "; border-radius : 5px; }")
                else:
                    self._value_display.setStyleSheet("QLabel { background-color : " + ICDisplayConfig.QtColorToSting(self.background_color) +
                                                      "; color : " + ICDisplayConfig.QtColorToSting(self._value_color) + "; border-radius : 5px; }")

            # update the value text
            if self._unit:
                self._value_display.setText("<span style='font-size:" + "{}".format(self._value_size) + "pt;'>" + "{:.2f}".format(self._value) +
                                            "</span> <span style='font-size:" + "{}".format(self._unit_size) + "pt;'>" + self._unit + "</span>")
            else:
                self._value_display.setText("<span style='font-size:" + "{}".format(self._value_size) + "pt;'>" + "{:.2f}".format(self._value) + "</span>")

        # update the label
        self._value_display.update()

    # update the widget
    def _local_update(self):
        # update the title text
        self._title_update()
        # update the value text
        self._value_update()
        # update self
        self.update()

    ########################################################
    # base class event overrides
    ########################################################
    # change in the orientation of the container
    def on_position_changed(self) -> None:
        if self.__container_type in (ICLinearContainerType.BAR, ICLinearContainerType.BAR_NO_TITLE, ICLinearContainerType.BAR_NO_VALUE,
                                     ICLinearContainerType.BAR_NO_TITLE_NO_VALUE):
            # update the widget position
            self.widget_position = self.position

            # update the scale_position
            self.scale_position = ICWidgetPosition.opposite(self.position)

    # change the visibility of elements
    def on_state_changed(self) -> None:
        if self.state == ICWidgetState.Hidden:
            # hide the central widget
            self._central_widget.state = ICWidgetState.Hidden
            self._central_widget.update()

            # hide the first scale bar
            if self.scale_bar_one  is not None:
                self.scale_bar_one.state = ICWidgetState.Hidden
                self.scale_bar_one.update()

            # hide the second scale bar
            if self.scale_bar_two is not None:
                self.scale_bar_two.state = ICWidgetState.Hidden
                self.scale_bar_two.update()

            # hide the title label
            if self._title_display is not None:
                self._title_display.hide()
                self._title_display.setMaximumSize(0, 0)

            # hide the value label
            if self._value_display is not None:
                self._value_display.hide()
                self._value_display.setMaximumSize(0, 0)

            # hide self
            self.hide()
            self.update()

        else:
            # show self
            self.show()

            # hide the title label
            if self._title_display is not None:
                self._title_display.show()
                self._title_display.setMaximumSize(QtWidgets.QWIDGETSIZE_MAX, QtWidgets.QWIDGETSIZE_MAX)

            # hide the value label
            if self._value_display is not None:
                self._value_display.show()
                self._value_display.setMaximumSize(QtWidgets.QWIDGETSIZE_MAX, QtWidgets.QWIDGETSIZE_MAX)

            # set the gauge bar state
            if self._central_widget is not None:
                self._central_widget.state = self.state

            # set the scale bar state
            if self.scale_bar_one is not None:
                self.scale_bar_one.state = self.state

            # hide the second scale bar
            if self.scale_bar_two is not None:
                self.scale_bar_two.state = self.state

            # update the screen
            self._local_update()

    ########################################################
    # override event handlers
    ########################################################
    # override the default paint event
    def paintEvent(self, e):
        # if hidden or transparent then nothing else to do
        if self.state == ICWidgetState.Hidden:
            return

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # get the size of the containing widget
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
