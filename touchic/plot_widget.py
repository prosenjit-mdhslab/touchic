# -*- coding: utf-8 -*-
"""
Created on May 23 2021

@author: Prosenjit

A class to plot 2D data
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from typing import Union
import numpy as np
from .display_config import ICDisplayConfig
from .base_widget import ICBaseWidget, ICWidgetState, ICWidgetPosition
from .linear_axis import ICLinearAxisContainer, ICLinearContainerType, ICLinearAxis


class ICGraph(ICBaseWidget):
    """
    A widget class to draw 2D graphs and plots
    """
    # clicked event
    clicked = pyqtSignal(str, str, int, float, float)

    # current value changed
    current_changed = pyqtSignal(float)

    # x axis rescaled
    rescaled_x = pyqtSignal()

    # y axis rescaled
    rescaled_y = pyqtSignal()

    def __init__(self, name: str, auto_scale: bool = True, widget_id: int = 0, *args, **kwargs):
        super(ICGraph, self).__init__(widget_id, *args, **kwargs)

        ######################################
        # name of the graph
        ######################################
        self._name: str = name

        ######################################
        # plotting data
        ######################################
        # primary line name
        self._primary_name: str = ""

        # raw data
        self._plot_x_data: dict[str, np.ndarray] = {}
        self._plot_y_data: dict[str, np.ndarray] = {}

        # plot line and fill colors
        self._plot_line_color: dict[str, QtGui.QColor] = {}
        self._plot_fill_color: dict[str, QtGui.QColor] = {}

        # plot line and marker style
        self._plot_style: dict[str, Union[str, Qt.PenStyle]] = {}
        self._plot_is_line: dict[str, bool] = {}

        # selected points
        self._selected_index: dict[str, int] = {}

        # default level if not 0. it is used to plot the level for missing points in live data
        self._base_level: float = 0

        # ring index for push operation
        self._ring_index: int = 0

        # alarm level
        self._lower_alarm_level_name: str = ""
        self._upper_alarm_level_name: str = ""

        self.alarm_activated: bool = False

        ######################################
        # Marker lines to draw horizontal or vertical lines to show limits
        ######################################
        # y axis marker lines
        self._y_marker_lines: dict[str, float] = {}
        self._y_marker_line_colors: dict[str, QtGui.QColor] = {}

        # x axis marker lines
        self._x_marker_lines: dict[str, float] = {}
        self._x_marker_line_colors: dict[str, QtGui.QColor] = {}

        ######################################
        # automatic y scaling
        ######################################
        # is auto scaling on
        self._auto_scale: bool = auto_scale

        # range for y axis
        self._scale_y_min: float = 1.0e18
        self._scale_y_max: float = -1.0e18

        # y range limit.
        # During autoscaling y_min and y_max is limited to these values
        self._auto_scale_y_min_limit: [float, float] = None
        self._auto_scale_y_max_limit: [float, float] = None

        #####################################
        # x range for zooming
        #####################################
        # x range
        self._scale_x_min: float = 1.0e18
        self._scale_x_max: float = -1.0e18

        # display x range
        self._display_x_min: float = -1.0e18
        self._display_x_max: float = 1.0e18

        ######################################
        # general appearance
        ######################################
        self.background_color = ICDisplayConfig.DefaultPlotFaceColor

        # selected color
        self._selected_color = ICDisplayConfig.DefaultPlotSelectedColor

        # size hint
        self.size_hint = (ICDisplayConfig.PlotWidth, ICDisplayConfig.PlotHeight)

        # basic property
        self.focusable = False
        self.clickable = True

        # size hint
        self.size_hint = (ICDisplayConfig.PlotWidth, ICDisplayConfig.PlotHeight)

        # override the default size policy
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)

    ###################################################
    #    Properties
    ###################################################
    @property
    def name(self) -> str:
        return self._name

    @property
    def x_data(self) -> dict[str, np.ndarray]:
        return self._plot_x_data

    @property
    def y_data(self) -> dict[str, np.ndarray]:
        return self._plot_y_data

    @property
    def line_color(self) -> dict[str, QtGui.QColor]:
        return self._plot_line_color

    @property
    def fill_color(self) -> dict[str, QtGui.QColor]:
        return self._plot_fill_color

    @property
    def plot_style(self) -> dict[str, Union[str, Qt.PenStyle]]:
        return self._plot_style

    @property
    def plot_is_line(self) -> dict[str, bool]:
        return self._plot_is_line

    @property
    def y_maker_line(self) -> dict[str, float]:
        return self._y_marker_lines

    @property
    def y_marker_line_color(self) -> dict[str, QtGui.QColor]:
        return self._y_marker_line_colors

    @property
    def x_maker_line(self) -> dict[str, float]:
        return self._x_marker_lines

    @property
    def x_marker_line_color(self) -> dict[str, QtGui.QColor]:
        return self._x_marker_line_colors

    @property
    def base_level(self) -> float:
        return self._base_level

    @base_level.setter
    def base_level(self, level: float) -> None:
        self._base_level = level
        self._local_update()

    @property
    def auto_scale(self) -> bool:
        return self._auto_scale

    @auto_scale.setter
    def auto_scale(self, scl: bool) -> None:
        self._auto_scale = scl
        self.update()

    @property
    def selected_color(self) -> QtGui.QColor:
        return self._selected_color

    @selected_color.setter
    def selected_color(self, clr: QtGui.QColor) -> None:
        self._selected_color = clr
        self.update()

    @property
    def display_y_max(self) -> float:
        return self._scale_y_max

    @property
    def display_y_min(self) -> float:
        return self._scale_y_min

    @property
    def display_x_max(self) -> float:
        return self._display_x_max

    @property
    def display_x_min(self) -> float:
        return self._display_x_min

    ###################################################
    #    Functions
    ###################################################
    """
        adds data to a plot
        clr is used to specify the color of the pen
        style specifies the drawing style. currently lines and markers cannot be specified together
        lines 
            (blank) : solid line
            -       : dash line
            .       : dot line
            -.      : dash dot line
            -..     : dash dot dot line
        markers
            o       : circle marker
            t       : triangle marker
            r       : rectangle marker
            x       : cross marker
            +       : plus marker
            *       : star marker
    """
    def add_line(self, line_name: str, x_data: list[float], y_data: list[float], style: str, line_color: str, fill_color: str = "",
                 rescale_display: float = False) -> None:

        # x and y length should be same
        if len(x_data) != len(y_data):
            return

        # the first line dded to the plot is the primary line
        if not self._primary_name:
            self._primary_name = line_name

        # add the data and color to the dictionary
        self._plot_x_data[line_name] = np.array(x_data)
        self._plot_y_data[line_name] = np.array(y_data)

        self._plot_line_color[line_name] = QtGui.QColor(line_color)
        if fill_color:
            self._plot_fill_color[line_name] = QtGui.QColor(fill_color)

        # set the plot style
        if style == "-":
            self._plot_is_line[line_name] = True
            self._plot_style[line_name] = Qt.DashLine
        elif style == ".":
            self._plot_is_line[line_name] = True
            self._plot_style[line_name] = Qt.DotLine
        elif style == "-.":
            self._plot_is_line[line_name] = True
            self._plot_style[line_name] = Qt.DashDotLine
        elif style == "-..":
            self._plot_is_line[line_name] = True
            self._plot_style[line_name] = Qt.DashDotDotLine
        elif style == "o" or style == "t" or style == "r" or style == "x" or style == "+" or style == "*":
            self._plot_is_line[line_name] = False
            self._plot_style[line_name] = style
        else:
            self._plot_is_line[line_name] = True
            self._plot_style[line_name] = Qt.SolidLine

        # reset y limits if the plot is autoscaling and notify others of the change
        if self._scale_y_range():
            self.rescaled_y.emit()

        # rescale the x axis and notify others about x axis rescaling
        if self._scale_display_x(rescale_display):
            self.rescaled_x.emit()

        # update the screen
        self.update()

    """
        Scale x axis display coordinates 
    """
    def _scale_display_x(self, rescale_display: bool) -> bool:
        # reset x limits for the plotting
        self._scale_x_range()

        scaled_x = False

        # set display limits
        if rescale_display:
            if self._display_x_min != self._scale_x_min:
                self._display_x_min = self._scale_x_min
                scaled_x = True

            if self._display_x_max != self._scale_x_max:
                self._display_x_max = self._scale_x_max
                scaled_x = True
        else:
            if not (self._scale_x_max > self._display_x_min > self._scale_x_min):
                self._display_x_min = self._scale_x_min
                scaled_x = True

            if not (self._scale_x_max > self._display_x_max > self._scale_x_min):
                self._display_x_max = self._scale_x_max
                scaled_x = True

        return scaled_x

    """
        Scale x axis for all lines in the plot
    """
    def _scale_x_range(self) -> bool:
        new_min = 1.0e18
        new_max = -1.0e18

        scaled = False

        # find max and min based on the x data of the plots
        for line_name in self._plot_x_data:
            x_arr = self._plot_x_data[line_name]
            if x_arr.size < 2:
                continue
            line_min = x_arr.min(initial=new_min)
            line_max = x_arr.max(initial=new_max)
            new_min = new_min if new_min < line_min else line_min
            new_max = new_max if new_max > line_max else line_max

        # find max and min based on the x markers
        for marker_name in self._x_marker_lines:
            x_pos = self._x_marker_lines[marker_name]
            new_min = new_min if new_min < x_pos else x_pos
            new_max = new_max if new_max > x_pos else x_pos

        if new_min != self._scale_x_min:
            self._scale_x_min = new_min
            scaled = True

        if new_max != self._scale_x_max:
            self._scale_x_max = new_max
            scaled = True

        return scaled

    """
        Scale for all lines in the plot
    """
    def _scale_y_range(self) -> bool:
        # return if auto scaling is turned off
        if not self._auto_scale:
            return False

        scaled = False

        # reset the scale maximum and minimum
        new_min = 1.0e18
        new_max = -1.0e18

        # find max an min from the y marker lines
        for marker_name in self._y_marker_lines:
            y_pos = self._y_marker_lines[marker_name]
            new_min = new_min if new_min < y_pos else y_pos
            new_max = new_max if new_max > y_pos else y_pos

        for line_name in self._plot_y_data:
            y_arr = self._plot_y_data[line_name]
            if y_arr.size < 2:
                continue
            line_max = y_arr.max(initial=new_max)
            line_min = y_arr.min(initial=new_min)
            new_min = new_min if new_min < line_min else line_min
            new_max = new_max if new_max > line_max else line_max

        # provide for additional gap
        add_gap_y = (new_max - new_min) * ICDisplayConfig.PlotBufferSpace
        new_max += add_gap_y
        new_min -= add_gap_y

        # ensure that the min and max limit is within the defined range
        if self._auto_scale_y_min_limit is not None:
            new_min = new_min if new_min > self._auto_scale_y_min_limit[0] else self._auto_scale_y_min_limit[0]
            new_min = new_min if new_min < self._auto_scale_y_min_limit[1] else self._auto_scale_y_min_limit[1]

        if self._auto_scale_y_max_limit is not None:
            new_max = new_max if new_max > self._auto_scale_y_max_limit[0] else self._auto_scale_y_max_limit[0]
            new_max = new_max if new_max < self._auto_scale_y_max_limit[1] else self._auto_scale_y_max_limit[1]

        if new_min != self._scale_y_min:
            self._scale_y_min = new_min
            scaled = True

        if new_max != self._scale_y_max:
            self._scale_y_max = new_max
            scaled = True

        return scaled

    """
        Update data for a given line
    """
    def update_data(self, line_name: str, data: list[float]) -> None:
        # size of new data should be same as previous data
        if len(data) != self._plot_y_data[line_name].size:
            return

        # update the data
        self._plot_y_data[line_name] = np.array(data)

        # reset limits, notify others and update the screen
        if self._scale_y_range():
            self.rescaled_y.emit()

        # update the view
        self.update()

    """
       Push new data point for the current line
       self._ring_index is used to maintain the current position
    """
    def push_data(self, all_line_names: tuple[str], data_set: tuple[float], rescale: bool = True) -> None:
        # check for wrap around
        if self._plot_x_data[self._primary_name].size == self._ring_index:
            self._ring_index = 0

        for line_name in self._plot_x_data.keys():
            try:
                index = all_line_names.index(line_name)
                new_value = data_set[index]
            except ValueError:
                new_value = self._base_level

            line: np.ndarray = self._plot_y_data[line_name]

            # update data
            line[self._ring_index] = new_value

            # update about the change in primary line
            if line_name == self._primary_name:
                self.current_changed[float].emit(new_value)

                # check for alarm
                self.alarm_activated = False
                if self._lower_alarm_level_name:
                    if new_value < self._y_marker_lines[self._lower_alarm_level_name]:
                        self.alarm_activated = True

                if self._upper_alarm_level_name:
                    if new_value > self._y_marker_lines[self._upper_alarm_level_name]:
                        self.alarm_activated = True

            # remove the next point
            next_index = (self._ring_index + 5) % line.size
            line[next_index] = self._base_level

        # if auto scaling is on the plot is completely auto-scaled once at the beginning of the cycle
        if self._auto_scale and rescale:
            if self._ring_index == 0:
                if self._scale_y_range():
                    self.rescaled_y.emit()
            else:
                scaled = False

                min_data = min(data_set)
                if min_data < self._scale_y_min:
                    new_min = min_data

                    # ensure that the min and max limit is within the defined range
                    if self._auto_scale_y_min_limit is not None:
                        new_min = new_min if new_min > self._auto_scale_y_min_limit[0] else self._auto_scale_y_min_limit[0]
                        new_min = new_min if new_min < self._auto_scale_y_min_limit[1] else self._auto_scale_y_min_limit[1]

                    if new_min != self._scale_y_min:
                        self._scale_y_min = new_min
                        scaled = True

                max_data = max(data_set)
                if max_data > self._scale_y_max:
                    new_max = max_data

                    # ensure that the min and max limit is within the defined range
                    if self._auto_scale_y_max_limit is not None:
                        new_max = new_max if new_max > self._auto_scale_y_max_limit[0] else self._auto_scale_y_max_limit[0]
                        new_max = new_max if new_max < self._auto_scale_y_max_limit[1] else self._auto_scale_y_max_limit[1]

                    if new_max != self._scale_y_max:
                        self._scale_y_max = new_max
                        scaled = True

                # notify others about y axis rescaling
                if scaled:
                    self.rescaled_y.emit()

        # increment the ring index and request view update
        self._ring_index += 1
        self.update()

    """
        Remove line from the plot
    """
    def remove_line(self, line_name: str, rescale_display: bool = False) -> None:
        # cannot remove the primary line
        if line_name == self._primary_name:
            return

        if line_name in self._plot_fill_color:
            self._plot_fill_color.pop(line_name)

        if line_name in self._plot_x_data:
            self._plot_x_data.pop(line_name)
            self._plot_y_data.pop(line_name)
            self._plot_line_color.pop(line_name)
            self._plot_style.pop(line_name)
            self._plot_is_line.pop(line_name)

            # rescale the y axis
            if self._scale_y_range():
                self.rescaled_y.emit()

            # rescale the x axis display
            if self._scale_display_x(rescale_display):
                self.rescaled_x.emit()

            # update the screen
            self.update()

    """
       Add limit lines to the plot window
    """
    def add_y_marker(self, marker_name: str, y_pos: float, marker_color: QtGui.QColor = ICDisplayConfig.DefaultPlotYMarkerColor) -> None:
        self._y_marker_lines[marker_name] = y_pos
        self._y_marker_line_colors[marker_name] = marker_color

        # reset y limits if the plot is autoscaling and notify others of the change
        if self._scale_y_range():
            self.rescaled_y.emit()

        # update the screen
        self.update()

    """
        Remove y marker line from the plot
    """
    def remove_y_marker_line(self, line_name: str) -> None:
        if line_name in self._y_marker_lines:
            self._y_marker_lines.pop(line_name)
            self._y_marker_line_colors.pop(line_name)

            # rescale the y axis
            if self._scale_y_range():
                self.rescaled_y.emit()

            # update the screen
            self.update()

    """
       Add lower alarm level
    """
    def add_lower_alarm_level(self, marker_name: str, y_pos: float, marker_color: QtGui.QColor = ICDisplayConfig.DefaultPlotYMarkerColor) -> None:
        self._lower_alarm_level_name = marker_name
        self.add_y_marker(marker_name, y_pos, marker_color)

    """
        Remove lower alarm level
    """
    def remove_lower_alarm_level(self, line_name: str) -> None:
        self._lower_alarm_level_name = ""
        self.remove_y_marker_line(line_name)

    """
       Add upper alarm level
    """
    def add_upper_alarm_level(self, marker_name: str, y_pos: float, marker_color: QtGui.QColor = ICDisplayConfig.DefaultPlotYMarkerColor) -> None:
        self._upper_alarm_level_name = marker_name
        self.add_y_marker(marker_name, y_pos, marker_color)

    """
        Remove lower alarm level
    """
    def remove_upper_alarm_level(self, line_name: str) -> None:
        self._upper_alarm_level_name = ""
        self.remove_y_marker_line(line_name)

    """
       Add range lines to the plot window
    """
    def add_x_marker(self, marker_name: str, x_pos: float, marker_color: QtGui.QColor = ICDisplayConfig.DefaultPlotXMarkerColor) -> None:
        self._x_marker_lines[marker_name] = x_pos
        self._x_marker_line_colors[marker_name] = marker_color

        # rescale the x axis and notify others about x axis rescaling
        if self._scale_display_x(True):
            self.rescaled_x.emit()

        # update the screen
        self.update()

    """
       Remove X range lines to the plot window
    """
    def remove_x_marker(self, marker_name: str, rescale_display: bool = False):
        if marker_name in self._x_marker_lines:
            self._x_marker_lines.pop(marker_name)
            self._x_marker_line_colors.pop(marker_name)

            # rescale the x axis display
            if self._scale_display_x(rescale_display):
                self.rescaled_x.emit()

            # update the screen
            self.update()

    """
        Check if a particular line name exists
    """
    def line_exists(self, line_name) -> bool:
        return line_name in self._plot_x_data

    """
        Length for a given plot
    """
    def length(self, line_name: str) -> int:
        return len(self._plot_x_data[line_name])

    """
        Get the range of x axis
    """
    def get_x_limits(self) -> [int, int]:
        return self._scale_x_min, self._scale_x_max

    """
            Get the range of y axis
    """
    def get_y_limits(self) -> [int, int]:
        return self._scale_y_min, self._scale_y_max

    """
        Set Y range for plots where the plots are not auto scaled
        For plots that are auto scaled the limits provide the limit
        for the scaling. The limits can be numbers specifying the limit 
        defined by [y_min, y_max]. The limits can also be in form of 
        a list which specifies the range of the limit. 
        y_min = [y_min_min, y_min_max]
        y_max = [y_max_min, y_max_max]
    """
    def set_y_auto_scale_limits(self, y_min: Union[float, list[float]], y_max: Union[float, list[float]]) -> None:
        # convert both y_max and y_min to list
        if not isinstance(y_max, list):
            y_max = [y_max, y_max]
        if not isinstance(y_min, list):
            y_min = [y_min, y_min]

        # sort the y_max range
        y_max.sort()
        y_min.sort()

        # y_max should be larger than y_min
        if y_max[0] < y_min[1]:
            return

        # set the largest range if autoscaling is not active
        if not self._auto_scale:
            self._scale_y_max = y_max[1]  # maximum of y_max
            self._scale_y_min = y_min[0]  # minimum of y_min

        # set the limit ranges to match the min and max
        self._auto_scale_y_max_limit = y_max
        self._auto_scale_y_min_limit = y_min

        # perform scaling
        if self._scale_y_range():
            self.rescaled_y.emit()

    ###################################################
    #    Override base class event handlers
    ###################################################
    def on_mouse_released(self, event: QtGui.QMouseEvent) -> None:
        if event.button() & Qt.LeftButton:
            # find the current position in data coordinates
            painter = QtGui.QPainter(self)
            temp_height = painter.device().height()
            temp_width = painter.device().width()

            # screen to world scaling factors
            x_scale = (float(self._display_x_max - self._display_x_min)) / (float(temp_width))
            y_scale = (float(self._scale_y_max - self._scale_y_min)) / (float(temp_height))

            # position in world scales
            real_pos_x = self._display_x_min + event.pos().x() * x_scale
            real_pos_y = self._scale_y_min + (temp_height - event.pos().y()) * y_scale

            for line_name in self._plot_x_data:
                # for each line find the closest point in the graph
                x_array = self._plot_x_data[line_name]
                y_array = self._plot_y_data[line_name]

                if x_array.size == 0 or y_array.size == 0:
                    continue

                dist = (x_array - real_pos_x)**2 + (y_array - real_pos_y)**2
                min_index = np.argmin(dist)

                self._selected_index[line_name] = min_index
                self.clicked.emit(self._name, line_name, min_index, x_array[min_index], y_array[min_index])

            self.update()

    """
        Wheel motion zooms in and out
    """
    def on_wheel_rotated(self, event: QtGui.QWheelEvent) -> None:
        # find the current position in data coordinates
        painter = QtGui.QPainter(self)
        temp_width = painter.device().width()

        x_scale = float(self._display_x_max - self._display_x_min) / float(temp_width)
        cur_pos_x = self._display_x_min + event.pos().x() * x_scale
        mid_x = 0.5 * (self._display_x_max + self._display_x_min)

        # calculate the new display window width
        num_steps = event.angleDelta().y() / 120

        if num_steps > 0:
            # zoom in based on cursor location
            wnd_x = 0.25 * (self._display_x_max - self._display_x_min)
        else:
            # zoom out based on cursor location
            wnd_x = self._display_x_max - self._display_x_min

        # change the display window based on position
        if cur_pos_x < mid_x:
            new_left_x = cur_pos_x - wnd_x

            if new_left_x < self._scale_x_min:
                wnd_x += self._scale_x_min - new_left_x
                new_left_x = self._scale_x_min

            self._display_x_min = new_left_x

            new_right_x = cur_pos_x + wnd_x
            self._display_x_max = new_right_x if new_right_x < self._scale_x_max else self._scale_x_max
        else:
            new_right_x = cur_pos_x + wnd_x

            if new_right_x > self._scale_x_max:
                wnd_x += new_right_x - self._scale_x_max
                new_right_x = self._scale_x_max

            self._display_x_max = new_right_x

            new_left_x = cur_pos_x - wnd_x
            self._display_x_min = new_left_x if new_left_x > self._scale_x_min else self._scale_x_min

        # notify others of the zoom
        self.rescaled_x.emit()

        # update the view
        self.update()

    ###################################################
    #    Override event handlers
    ###################################################
    """
        Draw the plot
    """
    def paintEvent(self, e):
        if self.state in (ICWidgetState.Hidden, ICWidgetState.Transparent):
            return

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # window dimensions
        temp_width = painter.device().width()
        temp_height = painter.device().height()

        # fix y limits for auto scale
        if self._scale_y_max == self._scale_y_min:
            self._scale_y_max += 1.0
            self._scale_y_min -= 1.0

        # world to screen scaling factors
        x_scale = (float(temp_width)) / (float(self._display_x_max - self._display_x_min))
        y_scale = (float(temp_height)) / (float(self._scale_y_max - self._scale_y_min))

        # calculate base level
        base_level_y = temp_height - (self._base_level - self._scale_y_min) * y_scale

        # normal pen
        pen = QtGui.QPen()
        pen.setWidth(2)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)

        # selected pen
        selected_pen = QtGui.QPen(self._selected_color)
        selected_pen.setWidth(2)
        selected_pen.setCapStyle(Qt.RoundCap)
        selected_pen.setJoinStyle(Qt.RoundJoin)

        # draw the lines
        for line_name in self._plot_x_data:
            x_array = self._plot_x_data[line_name]
            y_array = self._plot_y_data[line_name]

            # draw the main plot
            path = QtGui.QPainterPath()
            if line_name in self._plot_fill_color:
                path.setFillRule(Qt.WindingFill)
                brush = QtGui.QBrush(self._plot_fill_color[line_name])
                painter.setBrush(brush)

            # normal pen
            pen.setColor(self._plot_line_color[line_name])

            # if there is selected point
            selected_index = -1
            if line_name in self._selected_index:
                selected_index = self._selected_index[line_name]

            if self._plot_is_line[line_name]:
                pen.setStyle(self._plot_style[line_name])
                painter.setPen(pen)
                skip = True
                last_x = 0
                for i, x in enumerate(x_array):
                    y = y_array[i]
                    px = (x - self._display_x_min) * x_scale
                    py = temp_height - (y - self._scale_y_min) * y_scale

                    # limit py to top and bottom
                    py = py if py > 0 else 0
                    py = py if py < temp_height else temp_height

                    if 0 <= px <= temp_width:
                        if skip:
                            path.moveTo(px, base_level_y)
                            path.lineTo(px, py)
                            skip = False
                        else:
                            path.lineTo(px, py)
                        last_x = px

                    else:
                        # close the loop
                        path.lineTo(last_x, base_level_y)
                        path.closeSubpath()

                        # we start skipping till we get back in range
                        skip = True

                # if we were not skipping close the loop
                if not skip:
                    path.lineTo(last_x, base_level_y)
                    path.closeSubpath()
            else:

                painter.setPen(pen)
                if self._plot_style[line_name] == "o":
                    # draw circles
                    for i, x in enumerate(x_array):
                        # skip the selected point
                        if i == selected_index:
                            continue

                        # calculate screen coordinates
                        y = y_array[i]
                        px = (x - self._display_x_min) * x_scale
                        py = temp_height - (y - self._scale_y_min) * y_scale

                        if (3 < py < temp_height-3) and (3 < px < temp_width-3):
                            path.addEllipse(QtCore.QPointF(px, py), 3, 3)

                elif self._plot_style[line_name] == "r":
                    # draw rectangles
                    for i, x in enumerate(x_array):
                        # skip the selected index
                        if i == selected_index:
                            continue

                        # calculate screen coordinates
                        y = y_array[i]
                        px = (x - self._display_x_min) * x_scale
                        py = temp_height - (y - self._scale_y_min) * y_scale

                        if (3 < py < temp_height-3) and (3 < px < temp_width-3):
                            path.addRect(px - 3, py - 3, 6, 6)

                elif self._plot_style[line_name] == "t":
                    # draw triangles
                    for i, x in enumerate(x_array):
                        # skip the selected index
                        if i == selected_index:
                            continue

                        # calculate screen coordinates
                        y = y_array[i]
                        px = (x - self._display_x_min) * x_scale
                        py = temp_height - (y - self._scale_y_min) * y_scale

                        if (3 < py < temp_height-3) and (3 < px < temp_width-3):
                            path.moveTo(px, py-3)
                            path.lineTo(px-3, py+3)
                            path.lineTo(px+3, py+3)
                            path.lineTo(px, py-3)

                elif self._plot_style[line_name] == "+":
                    # draw +
                    for i, x in enumerate(x_array):
                        # skip the selected index
                        if i == selected_index:
                            continue

                        # calculate screen coordinates
                        y = y_array[i]
                        px = (x - self._display_x_min) * x_scale
                        py = temp_height - (y - self._scale_y_min) * y_scale

                        if (3 < py < temp_height-3) and (3 < px < temp_width-3):
                            path.moveTo(px, py-3)
                            path.lineTo(px, py+3)
                            path.moveTo(px-3, py)
                            path.lineTo(px+3, py)

                elif self._plot_style[line_name] == "*":
                    # draw *
                    for i, x in enumerate(x_array):
                        # skip the selected index
                        if i == selected_index:
                            continue

                        # calculate screen coordinates
                        y = y_array[i]
                        px = (x - self._display_x_min) * x_scale
                        py = temp_height - (y - self._scale_y_min) * y_scale

                        if (3 < py < temp_height-3) and (3 < px < temp_width-3):
                            path.moveTo(px, py)
                            path.lineTo(px, py-3)
                            path.moveTo(px, py)
                            path.lineTo(px-3, py)
                            path.moveTo(px, py)
                            path.lineTo(px+3, py)
                            path.moveTo(px, py)
                            path.lineTo(px+3, py+3)
                            path.moveTo(px, py)
                            path.lineTo(px-3, py+3)

                else:
                    # draw x
                    for i, x in enumerate(x_array):
                        # skip the selected index
                        if i == selected_index:
                            continue

                        # calculate screen coordinates
                        y = y_array[i]
                        px = (x - self._display_x_min) * x_scale
                        py = temp_height - (y - self._scale_y_min) * y_scale

                        if (3 < py < temp_height-3) and (3 < px < temp_width-3):
                            path.moveTo(px-3, py-3)
                            path.lineTo(px+3, py+3)
                            path.moveTo(px-3, py+3)
                            path.lineTo(px+3, py-3)

            # draw the line
            painter.drawPath(path)

            # draw the selected point
            if selected_index != -1:
                painter.setPen(selected_pen)

                # plot the circle
                px = (x_array[selected_index] - self._display_x_min) * x_scale
                py = temp_height - (y_array[selected_index] - self._scale_y_min) * y_scale

                if (3 < py < temp_height-3) and (3 < px < temp_width-3):
                    painter.drawEllipse(QtCore.QPointF(px, py), 3, 3)

        # setup the pen
        pen = QtGui.QPen()
        pen.setStyle(Qt.DashDotLine)
        pen.setWidth(2)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)

        # draw y limit lines
        for marker_name in self._y_marker_lines:
            pen.setColor(self._y_marker_line_colors[marker_name])
            painter.setPen(pen)
            y_pos = temp_height - (self._y_marker_lines[marker_name] - self._scale_y_min) * y_scale
            painter.drawLine(QtCore.QPointF(0, y_pos), QtCore.QPointF(temp_width, y_pos))

            y_text_pos = y_pos - (ICDisplayConfig.GeneralTextSize + 5)
            if y_text_pos < 0:
                y_text_pos = y_pos + (ICDisplayConfig.GeneralTextSize + 5)

            rect = QtCore.QRectF(0, y_text_pos, 60, ICDisplayConfig.GeneralTextSize + 5)
            painter.drawText(rect, Qt.AlignLeft, marker_name)

        # draw the base line
        pen.setColor(ICDisplayConfig.LinearGaugeRulerColor)
        painter.setPen(pen)
        y_pos = temp_height - (self._base_level - self._scale_y_min) * y_scale
        painter.drawLine(QtCore.QPointF(0, y_pos), QtCore.QPointF(temp_width, y_pos))

        # draw x range lines
        for marker_name in self._x_marker_lines:
            x_world = self._x_marker_lines[marker_name]
            if self._display_x_min < x_world < self._display_x_max:
                pen.setColor(self._x_marker_line_colors[marker_name])
                painter.setPen(pen)
                x_pos = (x_world - self._display_x_min) * x_scale
                painter.drawLine(QtCore.QPointF(x_pos, 0), QtCore.QPointF(x_pos, temp_height))

                x_text_pos = x_pos + 3
                align = Qt.AlignLeft
                if x_text_pos + 60 > temp_width:
                    x_text_pos = x_text_pos - 63
                    align = Qt.AlignRight

                rect = QtCore.QRectF(x_text_pos, 3, 60, ICDisplayConfig.GeneralTextSize + 5)
                painter.drawText(rect, align, marker_name)


class ICPlotWidget(ICLinearAxisContainer):
    """
        Container class for plots
    """
    
    def __init__(self, name: str, unit: str, auto_scale=True, show_y_axis: bool = True, display_steps_y: int = 4,
                 show_x_axis: bool = True, display_steps_x: int = 4, show_title: bool = True, show_value: bool = True, widget_id: int = 0, *args, **kwargs):

        if (not show_value) and (not show_value):
            cont_type = ICLinearContainerType.PLOT_NO_TITLE_NO_VALUE
        elif not show_value:
            cont_type = ICLinearContainerType.PLOT_NO_VALUE
        elif not show_title:
            cont_type = ICLinearContainerType.PLOT_NO_TITLE
        else:
            cont_type = ICLinearContainerType.PLOT

        super(ICPlotWidget, self).__init__(cont_type, widget_id, *args, **kwargs)

        # title and unit
        self.title = name
        self.unit = unit

        # local parameters
        self._show_y_axis = show_y_axis
        self._display_steps_y = display_steps_y

        self._show_x_axis = show_x_axis
        self._display_steps_x = display_steps_x

        # the plot window
        self._plot = ICGraph(name, auto_scale)
        self._plot.current_changed[float].connect(self.value_changed)
        self._plot.rescaled_x.connect(self.update_x_axis)
        self._plot.rescaled_y.connect(self.update_y_axis)
        self.add_central_widget(self._plot)

        # display parameters
        self.on_layout_update()

        # display parameters
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)

    ########################################################
    # properties
    ########################################################
    @property
    def graph(self) -> ICGraph:
        return self._plot

    @property
    def show_x_axis(self) -> bool:
        return self._show_x_axis

    @show_x_axis.setter
    def show_x_axis(self, sa: bool) -> None:
        # proceed only if teh status is different from before
        if sa == self._show_x_axis:
            return

        self._show_x_axis = sa

        # if true then create the scale bar
        if self._show_x_axis:
            if self.scale_bar_one is None:
                max_val = self.plot.display_x_max
                min_val = self.plot.display_x_min
                scale_values, scale_displayed_values = ICLinearAxis.create_ticks(max_val, min_val, self._display_steps_x, "{0:.0f}")
                self.add_first_scale_bar("", scale_values, scale_displayed_values, ICWidgetPosition.Bottom)
        else:
            # if false then remove scale bar
            if self.scale_bar_one is not None:
                index = self._layout.indexOf(self.scale_bar_one)
                if index >= 0:
                    _ = self._layout.takeAt(index)
                self.scale_bar_one = None
                self._update_layout()

    @property
    def show_y_axis(self) -> bool:
        return self._show_y_axis

    @show_y_axis.setter
    def show_y_axis(self, sa: bool) -> None:
        # proceed only if teh status is different from before
        if sa == self._show_y_axis:
            return

        self._show_y_axis = sa

        # if true then create the scale bar
        if self._show_y_axis:
            if self.scale_bar_two is None:
                max_val = self._plot.display_y_max
                min_val = self._plot.display_y_min
                scale_values, scale_displayed_values = ICLinearAxis.create_ticks(max_val, min_val, self._display_steps_x, "{0:.0f}")
                self.add_second_scale_bar("", scale_values, scale_displayed_values, ICWidgetPosition.Left)
        else:
            # if false then remove scale bar
            if self.scale_bar_one is not None:
                index = self._layout.indexOf(self.scale_bar_one)
                if index >= 0:
                    _ = self._layout.takeAt(index)
                self.scale_bar_one = None
                self._update_layout()

    ########################################################
    # functions
    ########################################################

    ########################################################
    # slots
    ########################################################
    # handles the signal for value update
    def update_x_axis(self) -> None:
        if not self._show_x_axis:
            return

        max_val = self._plot.display_x_max
        min_val = self._plot.display_x_min
        # if scale bar is not present then create it otherwise update
        if self.scale_bar_one is None:
            scale_values, scale_displayed_values = ICLinearAxis.create_ticks(max_val, min_val, self._display_steps_x, "{0:.0f}")
            self.add_first_scale_bar("", scale_values, scale_displayed_values, ICWidgetPosition.Bottom)
        else:
            self.scale_bar_one.update_ticks(max_val, min_val)

    def update_y_axis(self) -> None:
        if not self._show_y_axis:
            return

        max_val = self._plot.display_y_max
        min_val = self._plot.display_y_min
        # if scale bar is not present then create it otherwise update
        if self.scale_bar_two is None:
            scale_values, scale_displayed_values = ICLinearAxis.create_ticks(max_val, min_val, self._display_steps_y, "{0:.0f}")
            self.add_second_scale_bar("", scale_values, scale_displayed_values, ICWidgetPosition.Left)
        else:
            self.scale_bar_two.update_ticks(max_val, min_val)

    ########################################################
    # base class event overrides
    ########################################################
    # change layout based on the orientation
    def on_layout_update(self) -> None:
        plot_width = ICDisplayConfig.PlotWidth
        plot_height = ICDisplayConfig.PlotHeight

        if self.scale_bar_one is not None:
            scale_height = self.scale_bar_one.estimate_max_scale_width()
        else:
            scale_height = 0

        if self.scale_bar_two is not None:
            scale_width = self.scale_bar_two.estimate_max_scale_width()
        else:
            scale_width = 0

        self._plot.size_hint = (plot_width + scale_width, plot_height + scale_height)
        self.size_hint = (plot_width + scale_width, plot_height + scale_height + 50)

        if self.scale_bar_one is not None:
            self.scale_bar_one.size_hint = (plot_width, scale_height)

        if self.scale_bar_two is not None:
            self.scale_bar_two.size_hint = (scale_width, plot_height)

    ########################################################
    # event handlers
    ########################################################
    # override the default show event
    def showEvent(self, e):
        self.on_layout_update()
