# -*- coding: utf-8 -*-
"""
Created on May 23 2021

@author: Prosenjit

A class to plot 2D data
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from .display_config import ICDisplayConfig
from .base_widget import ICBaseWidget, ICWidgetState
from typing import Union
import numpy as np


class ICGraph(ICBaseWidget):
    """
    A widget class to plot 2D graphs
    """
    # clicked event
    clicked = pyqtSignal(str, str, int, float, float)

    # constants to configure the plotting
    SCREEN_X_LEFT_GUTTER = 65
    SCREEN_X_RIGHT_GUTTER = 50
    SCREEN_Y_TOP_GUTTER = 10
    SCREEN_Y_BOTTOM_GUTTER_LBL = 30
    SCREEN_Y_BOTTOM_GUTTER_NO_LBL = 10

    def __init__(self, name: str, auto_scale: bool = True, widget_id: int = 0, *args, **kwargs):
        super(ICGraph, self).__init__(widget_id, *args, **kwargs)
        ######################################
        # name of the graph
        ######################################
        self._name: str = name

        ######################################
        # plotting data
        ######################################
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
        self._default_level: float = 0

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
        # During autoscaling _ymin and _ymax is limited to these values
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
        self._face_color: QtGui.QColor = ICDisplayConfig.DefaultPlotFaceColor
        self._line_color: QtGui.QColor = ICDisplayConfig.DefaultPlotLineColor

        # determines if x and y labels are shown
        self._x_tick_label: bool = True
        self._y_tick_label: bool = True

        # format for the axis label
        self._axis_label_format: str = "{0:.2f}"

        # size
        self.size_hint = (ICDisplayConfig.PlotWidth, ICDisplayConfig.PlotHeight + 20)

        # basic property
        self.focusable = True
        self.clickable = True

        # override the default size policy
        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

        # plots can have different background color
        self.setStyleSheet("background-color : " + ICDisplayConfig.QtColorToSting(self._face_color) + ";")

    ###################################################
    #    Properties
    ###################################################
    # name of the plot
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, nm: str) -> None:
        self._name = nm
        self.update()

    # returns a tuple of x_tick_label and y_tick_label
    @property
    def tick_labels(self) -> [bool, bool]:
        return self._x_tick_label, self._y_tick_label

    @tick_labels.setter
    def tick_labels(self, show_labels: [bool, bool]) -> None:
        self._x_tick_label = show_labels[0]
        self._y_tick_label = show_labels[1]

        # adjust the display size if x tick labels are shown or not
        if self._x_tick_label:
            self.size_hint = (ICDisplayConfig.PlotWidth, ICDisplayConfig.PlotHeight + 20)
        else:
            self.size_hint = (ICDisplayConfig.PlotWidth, ICDisplayConfig.PlotHeight)

        # update the screen
        self.update()

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
    def add_line(self, line_name: str, x_data: list[float], y_data: list[float], style: str,
                 line_color: str, fill_color: str = "", rescale_display: float = False) -> None:
        # x and y length should be same
        if len(x_data) != len(y_data):
            return

        # convert to numpy array
        x_data = np.array(x_data)
        y_data = np.array(y_data)

        # add the data and color to the dictionary
        self._plot_x_data[line_name] = x_data
        self._plot_y_data[line_name] = y_data
        self._plot_line_colors[line_name] = QtGui.QColor(line_color)
        if fill_color != "":
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

        # reset y limits if the plot is autoscaling
        self._scale_y_range()
        # reset x limits for the plotting
        self._scale_x_range()

        # set display limits
        if rescale_display:
            self._display_x_min = self._scale_x_min
            self._display_x_max = self._scale_x_max
        else:
            self._display_x_min = self._display_x_min \
                if self._scale_x_max > self._display_x_min > self._scale_x_min \
                else self._scale_x_min
            self._display_x_max = self._display_x_max \
                if self._scale_x_max > self._display_x_max > self._scale_x_min \
                else self._scale_x_max

        # update the screen
        self.update()

    """
        Scale x axis for all lines in the plot
    """
    def _scale_x_range(self) -> None:
        self._scale_x_min = 1.0e18
        self._scale_x_max = -1.0e18

        # find max and min based on the x data of the plots
        for line_name in self._plot_x_data:
            x_arr = self._plot_x_data[line_name]
            if x_arr.size < 2:
                continue
            line_min = x_arr.min(initial=self._scale_x_min)
            line_max = x_arr.max(initial=self._scale_x_max)
            self._scale_x_min = self._scale_x_min if (self._scale_x_min < line_min) else line_min
            self._scale_x_max = self._scale_x_max if (self._scale_x_max > line_max) else line_max

        # find max and min based on the x markers
        for marker_name in self._x_marker_lines:
            x_pos = self._x_marker_lines[marker_name]
            self._scale_x_min = self._scale_x_min if (self._scale_x_min < x_pos) else x_pos
            self._scale_x_max = self._scale_x_max if (self._scale_x_max > x_pos) else x_pos

    """
        Reset y scale based on one line
    """
    def _scale_y(self, y_arr: np.ndarray) -> None:
        # proceed only if auto scaling is on
        if not self._auto_scale:
            return

        # check for empty array in the
        if y_arr.size > 1:
            line_y_max = y_arr.max(initial=self._scale_y_max)
            line_y_min = y_arr.min(initial=self._scale_y_min)
            self._scale_y_max = self._scale_y_max if (self._scale_y_max > line_y_max) else line_y_max
            self._scale_y_min = self._scale_y_min if (self._scale_y_min < line_y_min) else line_y_min

    """
        Scale for all lines in the plot
    """
    def _scale_y_range(self) -> None:
        # return if auto scaling is turned off
        if not self._auto_scale:
            return

        # reset the scale maximum and minimum
        self._scale_y_min = 1.0e18
        self._scale_y_max = -1.0e18

        # find max an min from the y marker lines
        for marker_name in self._y_marker_lines:
            y_pos = self._y_marker_lines[marker_name]
            self._scale_y_min = self._scale_y_min if (self._scale_y_min < y_pos) else y_pos
            self._scale_y_max = self._scale_y_max if (self._scale_y_max > y_pos) else y_pos

        for line_name in self._plot_y_data:
            self._scale_y(self._plot_y_data[line_name])

        # provide for additional gap
        add_gap_y = (self._scale_y_max - self._scale_y_min) * ICDisplayConfig.PlotBufferSpace
        self._scale_y_max += add_gap_y
        self._scale_y_min -= add_gap_y

        # ensure that the min and max limit is within the defined range
        if self._auto_scale_y_min_limit is not None:
            self._scale_y_min = self._scale_y_min if (self._scale_y_min > self._auto_scale_y_min_limit[0]) \
                else self._auto_scale_y_min_limit[0]
            self._scale_y_min = self._scale_y_min if (self._scale_y_min < self._auto_scale_y_min_limit[1]) \
                else self._auto_scale_y_min_limit[1]

        if self._auto_scale_y_max_limit is not None:
            self._scale_y_max = self._scale_y_max if (self._scale_y_max > self._auto_scale_y_max_limit[0]) \
                else self._auto_scale_y_max_limit[0]
            self._scale_y_max = self._scale_y_max if (self._scale_y_max < self._auto_scale_y_max_limit[1]) \
                else self._auto_scale_y_max_limit[1]

    """
        Update data for a given line
    """
    def update_data(self, line_name: str, data: list[float]) -> None:
        # size of new data should be same as previous data
        if len(data) != self._plot_y_data[line_name].size:
            return

        # update the data
        self._plot_y_data[line_name] = np.array(data)

        # reset limits and update the screen
        self._scale_y_range()
        self.update()

    """
        Remove line from the plot
    """
    def remove_line(self, line_name: str, rescale_display: bool = False) -> None:
        if line_name in self._plot_x_data.keys():
            self._plot_x_data.pop(line_name)
            self._plot_y_data.pop(line_name)
            self._plot_line_color.pop(line_name)
            self._plot_style.pop(line_name)
            self._plot_is_line.pop(line_name)

        if line_name in self._plot_fill_color:
            self._plot_fill_color.pop(line_name)

            # rescale the x and y axis
            self._scale_x_range()
            self._scale_y_range()

            # rescale the display
            if rescale_display:
                self._display_x_min = self._scale_x_min
                self._display_x_max = self._scale_x_max
            else:
                self._display_x_min = self._display_x_min \
                    if self._scale_x_max > self._display_x_min > self._scale_x_min \
                    else self._scale_x_min
                self._display_x_max = self._display_x_max \
                    if self._scale_x_max > self._display_x_max > self._scale_x_min \
                    else self._scale_x_max

            # update the screen
            self.update()

    """
       Add limit lines to the plot window
    """
    def add_y_marker(self, marker_name: str, y_pos: float,
                     marker_color: QtGui.QColor = ICDisplayConfig.DefaultPlotYMarkerColor) -> None:
        self._y_marker_lines[marker_name] = y_pos
        self._y_marker_line_colors[marker_name] = marker_color

        # readjust the auto scale limits
        if self._auto_scale:
            self._scale_y_max = self._scale_y_max if (self._scale_y_max > y_pos) else y_pos
            self._scale_y_min = self._scale_y_min if (self._scale_y_min < y_pos) else y_pos

        # update the screen
        self.update()

    """
       Add range lines to the plot window
    """
    def add_x_marker(self, marker_name: str, x_pos: float,
                     marker_color: QtGui.QColor = ICDisplayConfig.DefaultPlotXMarkerColor) -> None:
        self._x_marker_lines[marker_name] = x_pos
        self._x_marker_line_colors[marker_name] = marker_color

        # readjust the auto scale limits
        self._scale_x_max = self._scale_x_max if (self._scale_x_max > x_pos) else x_pos
        self._scale_x_min = self._scale_x_min if (self._scale_x_min < x_pos) else x_pos

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
        defined by [ymin, ymax]. The limits can also be in form of 
        a list which specifies the range of the limit. 
        ymin = [ymin_min, ymin_max]
        ymax = [ymax_min, ymax_max]
    """
    def set_y_auto_scale_limits(self, y_min: Union[float, list[float]], y_max: Union[float, list[float]]) -> None:
        # convert both ymax and ymin to list
        if not isinstance(y_max, list):
            y_max = [y_max, y_max]
        if not isinstance(y_min, list):
            y_min = [y_min, y_min]

        # sort the ymax range
        y_max.sort()
        y_min.sort()

        # ymax should be larger than ymin
        if y_max[0] < y_min[1]:
            return

        # set the largest range if autoscaling is not active
        if not self._auto_scale:
            self._scale_y_max = y_max[1]  # maximum of ymax
            self._scale_y_min = y_min[0]  # minimum of ymin

        # set the limit ranges to match the min and max
        self._auto_scale_y_max_limit = y_max
        self._auto_scale_y_min_limit = y_min

        # perform scaling
        self._scale_y_range()

    """
        Set the default value
    """
    def set_default_value(self, y_def: float) -> None:
        self._default_level = y_def
        self.update()

    ###################################################
    #    Override base class event handlers
    ###################################################
    def on_mouse_released(self, event: QtGui.QMouseEvent) -> None:
        if event.button() & Qt.LeftButton:
            # find the current position in data coordinates
            painter = QtGui.QPainter(self)
            tmp_hght = painter.device().height()
            tmp_wdth = painter.device().width()
            # canvas points
            xmin = self.SCREEN_X_LEFT_GUTTER
            xmax = tmp_wdth - self.SCREEN_X_RIGHT_GUTTER
            ymin = self.SCREEN_Y_TOP_GUTTER
            if self._xtick_label:
                ymax = tmp_hght - self.SCREEN_Y_BOTTOM_GUTTER_LBL
            else:
                ymax = tmp_hght - self.SCREEN_Y_BOTTOM_GUTTER_NOLBL
            add_gapy = (self._ymax - self._ymin) * DisplayConfig.PlotBufferSpace
            x_scale = (float(xmax - xmin)) / (float(self._disp_xmax - self._disp_xmin))
            y_scale = (float(ymin - ymax)) / (float((self._ymax + add_gapy) - (self._ymin - add_gapy)))
            # position in world scales
            real_pos_x = self._disp_xmin + (event.pos().x() - xmin) / x_scale
            real_pos_y = (self._ymin - add_gapy) + (event.pos().y() - ymin) / y_scale
            for line_name in self._plot_xdata:
                # for each line find the closest point in the graph
                xarr = self._plot_xdata[line_name]
                yarr = self._plot_ydata[line_name]
                if xarr.size == 0 or yarr.size == 0:
                    continue
                dist = (xarr - real_pos_x)**2 + (yarr - real_pos_y)**2
                min_index = np.argmin(dist)
                self._selected_index[line_name] = min_index
                self.clicked.emit(self._name, line_name, min_index, xarr[min_index], yarr[min_index])
            self.update()

    ###################################################
    #    Override event handlers
    ###################################################
    """
        Wheel motion zooms in and out
    """
    def wheelEvent(self, event):
        # find the current position in data coordinates
        painter = QtGui.QPainter(self)
        tmp_wdth = painter.device().width()
        x_scale = float(tmp_wdth - (self.SCREEN_X_LEFT_GUTTER + self.SCREEN_X_RIGHT_GUTTER)) / float(self._disp_xmax - self._disp_xmin)
        cur_pos_x = self._disp_xmin + (event.pos().x() - self.SCREEN_X_LEFT_GUTTER) / x_scale
        mid_x = 0.5 * (self._disp_xmax + self._disp_xmin)
        # calculate the new display window width
        numSteps = event.angleDelta().y() / 120
        if numSteps > 0:
            # zoom in based on cursor location
            wnd_x = 0.25 * (self._disp_xmax - self._disp_xmin)
        else:
            # zoom out based on cursor location
            wnd_x = self._disp_xmax - self._disp_xmin
        # change the display window based on position
        if cur_pos_x < mid_x:
            new_left_x = cur_pos_x - wnd_x
            if new_left_x < self._xmin:
                wnd_x += self._xmin - new_left_x
                new_left_x = self._xmin
            self._disp_xmin = new_left_x
            new_right_x = cur_pos_x + wnd_x
            self._disp_xmax = new_right_x if new_right_x < self._xmax else self._xmax
        else:
            new_right_x = cur_pos_x + wnd_x
            if new_right_x > self._xmax:
                wnd_x += new_right_x - self._xmax
                new_right_x = self._xmax
            self._disp_xmax = new_right_x
            new_left_x = cur_pos_x - wnd_x
            self._disp_xmin = new_left_x if new_left_x > self._xmin else self._xmin
        self.update()

    """
        Draw the plot
    """
    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # window dimensions
        tmp_wdth = painter.device().width()
        tmp_hght = painter.device().height()

        # setup the pen
        pen = QtGui.QPen(QtGui.QColor(self._line_color))
        pen.setWidth(2)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        fnt = painter.font()
        fnt.setPixelSize(DisplayConfig.GeneralTextSize)
        painter.setFont(fnt)

        # canvas points
        xmin = self.SCREEN_X_LEFT_GUTTER
        xmax = tmp_wdth - self.SCREEN_X_RIGHT_GUTTER
        ymin = self.SCREEN_Y_TOP_GUTTER
        if self._xtick_label:
            ymax = tmp_hght - self.SCREEN_Y_BOTTOM_GUTTER_LBL
        else:
            ymax = tmp_hght - self.SCREEN_Y_BOTTOM_GUTTER_NOLBL
        if (xmin >= xmax) or (ymin >= ymax):
            return

        # draw the main rect
        rect = QtCore.QRectF(xmin, ymin, xmax-xmin, ymax-ymin)
        painter.drawRect(rect)

        # fix y limits for auto scale
        if self._ymax == self._ymin:
            self._ymax = 1.0
            self._ymin = -1.0

        #addnl_gapy = (self._ymax - self._ymin) * DisplayConfig.PlotBufferSpace
        #self._ymax += addnl_gapy
        #self._ymin -= addnl_gapy

        x_scale = (float(xmax - xmin)) / (float(self._disp_xmax - self._disp_xmin))
        y_scale = (float(ymin - ymax)) / (float(self._ymax - self._ymin))

        # draw x ticks
        num_gaps = np.floor((xmax - xmin) / 100.0)
        num_gaps = 1 if num_gaps == 0 else num_gaps
        real_gap = (self._disp_xmax - self._disp_xmin) / num_gaps
        real_x = self._disp_xmin
        while real_x <= self._disp_xmax:
            # x position in pixels
            curr_x = xmin + x_scale * (real_x - self._disp_xmin)
            painter.drawLine(QtCore.QPointF(curr_x, ymax), QtCore.QPointF(curr_x, ymax+5))
            if self._xtick_label:
                if real_x == self._disp_xmin:
                    rect = QtCore.QRect(int(curr_x), ymax+10, 60, DisplayConfig.GeneralTextSize + 5)
                    painter.drawText(rect, Qt.AlignLeft, self.axis_label_format.format(real_x))
                elif (real_x + real_gap) <= self._disp_xmax:
                    rect = QtCore.QRect(int(curr_x)-25, ymax+10, 60, DisplayConfig.GeneralTextSize + 5)
                    painter.drawText(rect, Qt.AlignHCenter, self.axis_label_format.format(real_x))
                else:
                    rect = QtCore.QRect(int(curr_x)-50, ymax+10, 60, DisplayConfig.GeneralTextSize + 5)
                    painter.drawText(rect, Qt.AlignRight, self.axis_label_format.format(real_x))
            real_x += real_gap

        # draw y ticks
        num_gaps = np.floor((ymax - ymin) / 100.0)
        num_gaps = 1 if num_gaps == 0 else num_gaps
        real_gap = (self._ymax - self._ymin) / num_gaps
        real_y = self._ymax
        while real_y >= self._ymin:
            curr_y = ymax + y_scale * (real_y - self._ymin)
            painter.drawLine(QtCore.QPointF(xmin, curr_y), QtCore.QPointF(xmin-5, curr_y))
            if self._ytick_label:
                if real_y == self._ymin:
                    rect = QtCore.QRect(0, int(curr_y)-20, 60, DisplayConfig.GeneralTextSize + 5)
                    painter.drawText(rect, Qt.AlignRight, self.axis_label_format.format(real_y))
                elif (real_y - real_gap) >= self._ymin:
                    rect = QtCore.QRect(0, int(curr_y)-10, 60, DisplayConfig.GeneralTextSize + 5)
                    painter.drawText(rect, Qt.AlignRight, self.axis_label_format.format(real_y))
                else:
                    rect = QtCore.QRect(0, int(curr_y), 60, DisplayConfig.GeneralTextSize + 5)
                    painter.drawText(rect, Qt.AlignRight, self.axis_label_format.format(real_y))
            real_y -= real_gap

        # draw y limit lines
        for limit_name in self._ylimits:
            pen = QtGui.QPen(QtGui.QColor(self._ylimit_clr[limit_name]))
            pen.setStyle(Qt.DashDotLine)
            pen.setWidth(2)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)
            ypos = ymax + (self._ylimits[limit_name] - self._ymin) * y_scale
            painter.drawLine(QtCore.QPointF(xmin, ypos), QtCore.QPointF(xmax, ypos))
            rect = QtCore.QRect(0, ypos - 0.5*(DisplayConfig.GeneralTextSize + 5), 40, DisplayConfig.GeneralTextSize + 5)
            painter.drawText(rect, Qt.AlignRight, limit_name)

        # draw x range lines
        for range_name in self._xranges:
            x_world = self._xranges[range_name]
            if self._disp_xmin < x_world < self._disp_xmax:
                pen = QtGui.QPen(QtGui.QColor(self._xrange_clr[range_name]))
                pen.setStyle(Qt.DashDotLine)
                pen.setWidth(2)
                pen.setCapStyle(Qt.RoundCap)
                pen.setJoinStyle(Qt.RoundJoin)
                painter.setPen(pen)
                xpos = xmin + (x_world - self._disp_xmin) * x_scale
                painter.drawLine(QtCore.QPointF(xpos, ymin), QtCore.QPointF(xpos, ymax))

        # selected pen
        selected_pen = QtGui.QPen(QtGui.QColor('#FF3333'))
        selected_pen.setWidth(2)
        selected_pen.setCapStyle(Qt.RoundCap)
        selected_pen.setJoinStyle(Qt.RoundJoin)

        # draw the lines
        for line_name in self._plot_xdata:
            xarr = self._plot_xdata[line_name]
            yarr = self._plot_ydata[line_name]
            # if there is selected point
            sel_indx = -1
            if line_name in self._selected_index:
                painter.setPen(selected_pen)
                # plot the circle
                sel_indx = self._selected_index[line_name]
                px = xmin + (xarr[sel_indx] - self._disp_xmin) * x_scale
                py = ymax + (yarr[sel_indx] - self._ymin) * y_scale
                if (py < ymax - 4) and (py > ymin + 4) and (px < xmax - 4) and (px > xmin + 4):
                    painter.drawEllipse(QtCore.QPointF(px, py), 3, 3)
            # draw the main plot
            path = QtGui.QPainterPath()
            path.moveTo(xmin, ymax)
            # normal pen
            pen = QtGui.QPen(QtGui.QColor(self._plot_clrs[line_name]))
            pen.setWidth(2)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            if self._plot_is_line[line_name]:
                pen.setStyle(self._plot_style[line_name])
                painter.setPen(pen)
                skip = True
                for i, x in enumerate(xarr):
                    y = yarr[i]
                    px = xmin + (x - self._disp_xmin) * x_scale
                    py = ymax + (y - self._ymin) * y_scale
                    if skip or (py >= ymax-2) or (py <= ymin+2) or (px >= xmax-2) or (px <= xmin+2):
                        path.moveTo(px, py)
                        skip = False
                    else:
                        path.lineTo(px, py)
            else:
                painter.setPen(pen)
                if self._plot_style[line_name] == "o":
                    # draw circles
                    for i, x in enumerate(xarr):
                        if i == sel_indx:
                            continue
                        y = yarr[i]
                        px = xmin + (x - self._disp_xmin) * x_scale
                        py = ymax + (y - self._ymin) * y_scale
                        if (py < ymax-4) and (py > ymin+4) and (px < xmax-4) and (px > xmin+4):
                            path.addEllipse(QtCore.QPointF(px, py), 3, 3)
                elif self._plot_style[line_name] == "r":
                    # draw rectangles
                    for i, x in enumerate(xarr):
                        if i == sel_indx:
                            continue
                        y = yarr[i]
                        px = xmin + (x - self._disp_xmin) * x_scale
                        py = ymax + (y - self._ymin) * y_scale
                        if (py < ymax-4) and (py > ymin+4) and (px < xmax-4) and (px > xmin+4):
                            path.addRect(px - 3, py - 3, 6, 6)
                elif self._plot_style[line_name] == "t":
                    # draw triangles
                    for i, x in enumerate(xarr):
                        if i == sel_indx:
                            continue
                        y = yarr[i]
                        px = xmin + (x - self._disp_xmin) * x_scale
                        py = ymax + (y - self._ymin) * y_scale
                        if (py < ymax-4) and (py > ymin+4) and (px < xmax-4) and (px > xmin+4):
                            path.moveTo(px, py-3)
                            path.lineTo(px-3, py+3)
                            path.lineTo(px+3, py+3)
                            path.lineTo(px, py-3)
                elif self._plot_style[line_name] == "+":
                    # draw +
                    for i, x in enumerate(xarr):
                        if i == sel_indx:
                            continue
                        y = yarr[i]
                        px = xmin + (x - self._disp_xmin) * x_scale
                        py = ymax + (y - self._ymin) * y_scale
                        if (py < ymax-4) and (py > ymin+4) and (px < xmax-4) and (px > xmin+4):
                            path.moveTo(px, py-3)
                            path.lineTo(px, py+3)
                            path.moveTo(px-3, py)
                            path.lineTo(px+3, py)
                elif self._plot_style[line_name] == "*":
                    # draw *
                    for i, x in enumerate(xarr):
                        if i == sel_indx:
                            continue
                        y = yarr[i]
                        px = xmin + (x - self._disp_xmin) * x_scale
                        py = ymax + (y - self._ymin) * y_scale
                        if (py < ymax-4) and (py > ymin+4) and (px < xmax-4) and (px > xmin+4):
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
                    for i, x in enumerate(xarr):
                        if i == sel_indx:
                            continue
                        y = yarr[i]
                        px = xmin + (x - self._disp_xmin) * x_scale
                        py = ymax + (y - self._ymin) * y_scale
                        if (py < ymax-4) and (py > ymin+4) and (px < xmax-4) and (px > xmin+4):
                            path.moveTo(px-3, py-3)
                            path.lineTo(px+3, py+3)
                            path.moveTo(px-3, py+3)
                            path.lineTo(px+3, py-3)
            painter.drawPath(path)        

        # fix the changes in _y max and _y min
        #self._ymax -= addnl_gapy
        #self._ymin += addnl_gapy

        # add label
        fnt = painter.font()
        fnt.setPixelSize(DisplayConfig.LabelTextSize)
        painter.setFont(fnt)
        rect = QtCore.QRect(-30, -15, 60, 30)
        painter.save()
        painter.translate(xmax+10.0, tmp_hght/2.0)
        painter.rotate(90)
        painter.drawText(rect, Qt.AlignHCenter, self._name)
        painter.rotate(-90)
        painter.translate(-xmax-10.0, -tmp_hght/2.0)
        painter.restore()


class ICPlotWidget(ICBaseWidget):
    clicked = pyqtSignal(str, str, int, float, float)
    
    def __init__(self, rows, cols, names, parent=None, autoscale=True, facecolor='#1C2833', linecolor='#FFEE58',
                 *args, **kwargs):
        super(PSPlotWidget, self).__init__(parent, *args, **kwargs)
        # plots dictionary
        self.py_plots = {}
        self._ring_index = 0
        # main layout
        self.layout = QtWidgets.QGridLayout()
        row_num = 0
        col_num = 0
        for indx, nam in enumerate(names):
            self.py_plots[nam] = _PSGraph(nam, self, autoscale, facecolor, linecolor)
            self.py_plots[nam].clicked.connect(self.onClicked)
            self.layout.addWidget(self.py_plots[nam], row_num, col_num, 1, 1)
            col_num += 1
            if col_num == cols:
                row_num += 1
                col_num = 0
        self.setLayout(self.layout)

        # display parameters
        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )
        
    @pyqtSlot(str, str, int, float, float)
    def onClicked(self, plot_name, line_name, index, x_pos, y_pos):
        self.clicked.emit(plot_name, line_name, index, x_pos, y_pos)

    def sizeHint(self):
        return QtCore.QSize(DisplayConfig.PlotWidth, DisplayConfig.PlotHeight)
    
    def minimumSizeHint(self):
        return QtCore.QSize(DisplayConfig.PlotWidth, DisplayConfig.PlotHeight)

    """
        update multiple plot lines
    """
    def updateDataSet(self, plot_names, line_names, data):
        for index, name in enumerate(plot_names):
            plot = self.py_plots[name]
            plot.updateData(line_names[index], data[index])

    """
        update and redraw all included plots
    """
    def update(self):
        for name in self.py_plots:
            plot = self.py_plots[name]
            plot.update()

    """
        Function for plotting continuous animated plots
    """
    def pushDataSet(self, plot_names, line_names, datas):
        # check the index
        plot = self.py_plots[plot_names[0]]
        data_len = plot._plot_xdata[line_names[0]].size
        if self._ring_index == data_len:
            self._ring_index = 0
        # set the next index point
        nxt_indx = (self._ring_index + 5) % data_len
        # change the datapoint
        for indx, name in enumerate(plot_names):
            plot = self.py_plots[name]
            line = plot._plot_ydata[line_names[indx]]
            line[self._ring_index] = datas[indx]
            if plot._autoscale:
                if self._ring_index == 0:
                    plot._scaleYRange()
                else:
                    plot._ymax = plot._ymax if (plot._ymax > datas[indx]) else datas[indx]
                    plot._ymin = plot._ymin if (plot._ymin < datas[indx]) else datas[indx]
            # remove the next point
            line[nxt_indx] = plot._def_level    
        self._ring_index += 1
