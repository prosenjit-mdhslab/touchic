# -*- coding: utf-8 -*-
"""
Created on May  19 2021

@author: Prosenjit

Custom Qt Widget to show a linear gauge with min-max. The following modifiable
attributes are exposed.
"""

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, pyqtSlot, pyqtSignal
from typing import Union
from .display_config import ICDisplayConfig
from .base_widget import ICBaseWidget, ICWidgetState, ICWidgetPosition
from .linear_axis import ICLinearAxis, ICLinearAxisContainer, ICLinearContainerType


class ICGaugeBar(ICBaseWidget):
    """
    Class for a custom widget to draw a colored bar.
    Length of the colored bar is proportional to the value.
    """

    # bar state has changed signal. it can be current value or alarm status
    changed = pyqtSignal(float)

    def __init__(self, min_val: float, max_val: float, curr_val: float, position: ICWidgetPosition = ICWidgetPosition.Bottom,
                 widget_id: int = 0, *args, **kwargs):
        super(ICGaugeBar, self).__init__(widget_id, *args, **kwargs)

        # minimum and maximum value of the gauge bar
        self._gauge_range_min: float = min_val
        self._gauge_range_max: float = max_val

        # current value of the gauge
        self._gauge_val: float = curr_val

        # has the current value lead to an alarm
        self.alarm_activated = False

        # upper alarm level for the gauge
        self._alarm_upper_level: float = max_val
        self._alarm_upper_level_text: str = "UL"
        self._alarm_upper_level_set: bool = False

        # lower alarm level for the gauge
        self._alarm_lower_level: float = min_val
        self._alarm_lower_level_text: str = "LL"
        self._alarm_lower_level_set: bool = False

        # max level tracking
        self._cycle_max: float = curr_val
        self._cycle_max_tracking: bool = False

        # min level tracking
        self._cycle_min: float = curr_val
        self._cycle_min_tracking: bool = False

        # target tracking
        self._target_value: float = curr_val
        self._target_tracking: bool = False

        # gauge width
        self._gauge_width: int = ICDisplayConfig.LinearGaugeWidth

        # background colors
        self._back_color_light: QtGui.QColor = ICDisplayConfig.LinearGaugeBoxColorLight
        self._back_color_dark: QtGui.QColor = ICDisplayConfig.LinearGaugeBoxColorDark

        # gauge colors normal
        self._gauge_color_normal_light: QtGui.QColor = ICDisplayConfig.LinearGaugeNormalLight
        self._gauge_color_normal_dark: QtGui.QColor = ICDisplayConfig.LinearGaugeNormalDark

        # gauge colors alarmed
        self._gauge_color_alarm_light: QtGui.QColor = ICDisplayConfig.LinearGaugeErrorLight
        self._gauge_color_alarm_dark: QtGui.QColor = ICDisplayConfig.LinearGaugeErrorDark

        # alarm level text size and color
        self._alarm_text_size: int = ICDisplayConfig.LabelTextSize
        self._alarm_text_color: QtGui.QColor = ICDisplayConfig.LinearGaugeLimitsColor

        # min max line color
        self._min_max_color: QtGui.QColor = ICDisplayConfig.LinearGaugeMinMaxColor

        # target color
        self._target_color: QtGui.QColor = ICDisplayConfig.LinearGaugeTargetColor

        # sets the click-ability and focus-ability of the button
        self.clickable = True
        self.focusable = False

        # set the position of the gauge.
        self.position = position

        # override the base Size policy
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)

    ########################################################
    # properties
    ########################################################
    # get the minimum limit of the gauge bar
    @property
    def gauge_range_min(self) -> float:
        return self._gauge_range_min

    # set the minimum limit of the gauge bar
    @gauge_range_min.setter
    def gauge_range_min(self, min_val: float) -> None:
        self._gauge_range_min = min_val
        self.update()

    # get the maximum limit of the gauge bar
    @property
    def gauge_range_max(self) -> float:
        return self._gauge_range_max

    # set the minimum limit of the gauge bar
    @gauge_range_max.setter
    def gauge_range_max(self, max_val: float) -> None:
        self._gauge_range_max = max_val
        self.update()

    # get the current value
    @property
    def gauge_value(self) -> float:
        return self._gauge_val

    # set the current value
    @gauge_value.setter
    def gauge_value(self, val: float) -> None:
        if self._gauge_val != val:
            # limit gauge value to the min and max range
            if val < self._gauge_range_min:
                self._gauge_val = self._gauge_range_min
            elif val > self._gauge_range_max:
                self._gauge_val = self._gauge_range_max
            else:
                self._gauge_val = val

            # update the min value
            if self._cycle_min_tracking:
                if val < self._cycle_min:
                    self._cycle_min = val

            # update the max value
            if self._cycle_max_tracking:
                if val > self._cycle_max:
                    self._cycle_max = val

            # reset the alarm before testing
            self.alarm_activated = False

            # check for too low alarm
            if self._alarm_lower_level_set:
                if val < self._alarm_lower_level:
                    self.alarm_activated = True

            # check for too high alarm
            if self._alarm_upper_level_set:
                if val > self._alarm_upper_level:
                    self.alarm_activated = True

            self.changed.emit(val)
            self.update()

    # get the upper level alarm
    # tuple of (name, value)
    @property
    def upper_alarm(self) -> Union[tuple[str, float], tuple[None, None]]:
        if self._alarm_upper_level_set:
            return self._alarm_upper_level_text, self._alarm_upper_level
        else:
            return None, None

    # set the upper level alarm
    @upper_alarm.setter
    def upper_alarm(self, alarm: tuple[str, float]) -> None:
        # check if upper alarm level is greater than the lower alarm level
        if self._alarm_lower_level_set:
            if alarm[1] < self._alarm_lower_level:
                return

        # check if the limit value is in between the max and min values
        if self._gauge_range_min <= alarm[1] <= self._gauge_range_max:
            self._alarm_upper_level_set = True
            self._alarm_upper_level_text = alarm[0]
            self._alarm_upper_level = alarm[1]

            # check for alarm level
            if self._gauge_val > self._alarm_upper_level:
                self.alarm_activated = True
                self.changed.emit(self._gauge_val)
            self.update()

    # get the lower level alarm
    # tuple of (name, value)
    @property
    def lower_alarm(self) -> Union[tuple[str, float], tuple[None, None]]:
        if self._alarm_lower_level_set:
            return self._alarm_lower_level_text, self._alarm_lower_level
        else:
            return None, None

    # set the upper level alarm
    @lower_alarm.setter
    def lower_alarm(self, alarm: tuple[str, float]) -> None:
        # check if lower alarm level is less the upper alarm level
        if self._alarm_upper_level_set:
            if alarm[1] > self._alarm_upper_level:
                return

        # check if the limit value is in between the max and min values
        if self._gauge_range_min <= alarm[1] <= self._gauge_range_max:
            self._alarm_lower_level_set = True
            self._alarm_lower_level_text = alarm[0]
            self._alarm_lower_level = alarm[1]

            # check if alarm is active
            if self._gauge_val < self._alarm_lower_level:
                self.alarm_activated = True
                self.changed.emit(self._gauge_val)
            self.update()

    @property
    def target_value(self) -> Union[float, None]:
        if self._target_tracking:
            return self._target_value
        return None

    @target_value.setter
    def target_value(self, val: float) -> None:
        self._target_tracking = True
        self._target_value = val
        self.update()

    # gauge width
    @property
    def gauge_width(self) -> int:
        return self._gauge_width

    @gauge_width.setter
    def gauge_width(self, wd: int) -> None:
        self._gauge_width = wd
        self.update()

    # get the background container color of the bar
    @property
    def container_colors(self) -> tuple[QtGui.QColor, QtGui.QColor]:
        return self._back_color_light, self._back_color_dark

    # set the background color of the bar
    @container_colors.setter
    def container_colors(self, clrs: tuple[QtGui.QColor, QtGui.QColor]) -> None:
        self._back_color_light = clrs[0]
        self._back_color_dark = clrs[1]
        self.update()

    # get the normal gauge color
    @property
    def gauge_color_normal(self) -> tuple[QtGui.QColor, QtGui.QColor]:
        return self._gauge_color_normal_light, self._gauge_color_normal_dark

    # set the normal gauge color
    @gauge_color_normal.setter
    def gauge_color_normal(self, clr: tuple[QtGui.QColor, QtGui.QColor]) -> None:
        self._gauge_color_normal_light = clr[0]
        self._gauge_color_normal_dark = clr[1]
        self.update()

    # get the alarm gauge color
    @property
    def gauge_color_alarm(self) -> tuple[QtGui.QColor, QtGui.QColor]:
        return self._gauge_color_alarm_light, self._gauge_color_alarm_dark

    # set the normal gauge color
    @gauge_color_alarm.setter
    def gauge_color_alarm(self, clr: tuple[QtGui.QColor, QtGui.QColor]) -> None:
        self._gauge_color_alarm_light = clr[0]
        self._gauge_color_alarm_dark = clr[1]
        self.update()

    # get the alarm level text size
    @property
    def alarm_level_text_size(self) -> int:
        return self._alarm_text_size

    # set the alarm level text size
    @alarm_level_text_size.setter
    def alarm_level_text_size(self, sz: int) -> None:
        self._alarm_text_size = sz

    # get the alarm level text color
    @property
    def alarm_level_text_color(self) -> QtGui.QColor:
        return self._alarm_text_color

    # set the alarm level text color
    @alarm_level_text_color.setter
    def alarm_level_text_color(self, clr: QtGui.QColor) -> None:
        self._alarm_text_color = clr

    # min max color
    @property
    def min_max_color(self) -> QtGui.QColor:
        return self._min_max_color

    @min_max_color.setter
    def min_max_color(self, clr: QtGui.QColor) -> None:
        self._min_max_color = clr
        self.update()

    # target color
    @property
    def target_color(self) -> QtGui.QColor:
        return self._target_color

    @target_color.setter
    def target_color(self, clr: QtGui.QColor) -> None:
        self._target_color = clr
        self.update()

    ########################################################
    # functions
    ########################################################
    # start the cycle max tracking
    def start_max_tracking(self) -> None:
        self._cycle_max_tracking = True
        self._cycle_max = self._gauge_val

    # reset the cycle for max tracking
    def reset_max_tracking(self) -> None:
        self._cycle_max = self._gauge_val

    # stop the cycle max tracking
    def stop_max_tracking(self) -> None:
        self._cycle_max_tracking = False

    # start the cycle max tracking
    def start_min_tracking(self) -> None:
        self._cycle_min_tracking = True
        self._cycle_min = self._gauge_val

    # reset the cycle for max tracking
    def reset_min_tracking(self) -> None:
        self._cycle_min = self._gauge_val

    # stop the cycle max tracking
    def stop_min_tracking(self) -> None:
        self._cycle_min_tracking = False

    # estimate max width
    def estimate_max_gauge_width(self) -> int:
        # max width is dependent on the orientation of the widget
        if self.position.is_horizontal():
            return self._gauge_width + 15 + self._alarm_text_size
        else:
            # setup the font
            painter = QtGui.QPainter(self)
            fnt = painter.font()
            fnt.setPixelSize(self._alarm_text_size)
            fnt.setBold(True)

            # create the font matrices
            font_matrices = QtGui.QFontMetrics(fnt)
            width_lower = font_matrices.horizontalAdvance(self._alarm_lower_level_text)
            width_upper = font_matrices.horizontalAdvance(self._alarm_upper_level_text)
            text_width = width_upper if width_upper > width_lower else width_lower

            return self._gauge_width + 10 + text_width

    ########################################################
    # base class event overrides
    ########################################################
    # TODO: mouse click plots the history
    def on_mouse_released(self, event: QtGui.QMouseEvent) -> None:
        pass

    #######################################################
    # overrides and event handlers
    ########################################################
    # override the default paint event
    def paintEvent(self, e):
        # if hidden or transparent then nothing else to do
        if self.state in (ICWidgetState.Hidden, ICWidgetState.Transparent):
            return

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # get the size of the containing widget
        bar_width = painter.device().width()
        bar_height = painter.device().height()

        ##########################################
        # calculate dimensions
        ##########################################
        if self.position.is_horizontal():
            ##################################################
            # horizontal configurations
            ##################################################
            gauge_start_x = 0
            gauge_size_x = bar_width
            gauge_size_y = self._gauge_width

            # bar position
            bar_start_x = 2
            bar_size_x = (gauge_size_x - 4) * (self._gauge_val - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
            bar_size_y = gauge_size_y - 4

            # alarm levels
            if self._alarm_lower_level_set:
                lower_alarm_pos_x = (gauge_size_x - 4) * (self._alarm_lower_level - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
                # calculate the text position
                text_width = bar_width / 3
                lower_alarm_text_start_x = lower_alarm_pos_x - bar_width / 6
                lower_alarm_text_align = Qt.AlignCenter

            if self._alarm_upper_level_set:
                upper_alarm_pos_x = (gauge_size_x - 4) * (self._alarm_upper_level - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
                # calculate the text position
                text_width = bar_width / 3
                upper_alarm_text_start_x = upper_alarm_pos_x - bar_width / 6
                upper_alarm_text_align = Qt.AlignCenter

            ##################################################
            # top & bottom specific calculations
            ##################################################
            if self.position == ICWidgetPosition.Top:
                ##################################################
                # Top
                ##################################################
                gauge_start_y = bar_height - gauge_size_y
                bar_start_y = gauge_start_y + 2

                # min tracking
                if self._cycle_min_tracking:
                    min_pos_x = (gauge_size_x - 4) * (self._cycle_min - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
                    min_point_one = QtCore.QPointF(min_pos_x, gauge_start_y + gauge_size_y)
                    min_point_two = QtCore.QPointF(min_pos_x, gauge_start_y - 5)

                # max tracking
                if self._cycle_max_tracking:
                    max_pos_x = (gauge_size_x - 4) * (self._cycle_max - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
                    max_point_one = QtCore.QPointF(max_pos_x, gauge_start_y + gauge_size_y)
                    max_point_two = QtCore.QPointF(max_pos_x, gauge_start_y - 5)

                # target tracking
                if self._target_tracking:
                    target_pos_x = (gauge_size_x - 4) * (self._target_value - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
                    target_point_one = QtCore.QPointF(target_pos_x, gauge_start_y + gauge_size_y)
                    target_point_two = QtCore.QPointF(target_pos_x, gauge_start_y - 5)

                # lower alarm level
                if self._alarm_lower_level_set:
                    lower_alarm_point_one = QtCore.QPointF(lower_alarm_pos_x, gauge_start_y + gauge_size_y)
                    lower_alarm_point_two = QtCore.QPointF(lower_alarm_pos_x, gauge_start_y - 5)
                    lower_alarm_text_rect = QtCore.QRectF(lower_alarm_text_start_x, gauge_start_y - 15 - self._alarm_text_size,
                                                          text_width, self._alarm_text_size + 5)

                # upper alarm level
                if self._alarm_upper_level_set:
                    upper_alarm_point_one = QtCore.QPointF(upper_alarm_pos_x, gauge_start_y + gauge_size_y)
                    upper_alarm_point_two = QtCore.QPointF(upper_alarm_pos_x, gauge_start_y - 5)
                    upper_alarm_text_rect = QtCore.QRectF(upper_alarm_text_start_x, gauge_start_y - 15 - self._alarm_text_size,
                                                          text_width, self._alarm_text_size + 5)

            else:
                ##################################################
                # Bottom
                ##################################################
                gauge_start_y = 0
                bar_start_y = 2

                # min tracking
                if self._cycle_min_tracking:
                    min_pos_x = (gauge_size_x - 4) * (self._cycle_min - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
                    min_point_one = QtCore.QPointF(min_pos_x, gauge_start_y + gauge_size_y + 5)
                    min_point_two = QtCore.QPointF(min_pos_x, gauge_start_y)

                # max tracking
                if self._cycle_max_tracking:
                    max_pos_x = (gauge_size_x - 4) * (self._cycle_max - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
                    max_point_one = QtCore.QPointF(max_pos_x, gauge_start_y + gauge_size_y + 5)
                    max_point_two = QtCore.QPointF(max_pos_x, gauge_start_y)

                # target tracking
                if self._target_tracking:
                    target_pos_x = (gauge_size_x - 4) * (self._target_value - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
                    target_point_one = QtCore.QPointF(target_pos_x, gauge_start_y + gauge_size_y + 5)
                    target_point_two = QtCore.QPointF(target_pos_x, gauge_start_y)

                # lower alarm level
                if self._alarm_lower_level_set:
                    lower_alarm_point_one = QtCore.QPointF(lower_alarm_pos_x, gauge_start_y + gauge_size_y + 5)
                    lower_alarm_point_two = QtCore.QPointF(lower_alarm_pos_x, gauge_start_y)
                    lower_alarm_text_rect = QtCore.QRectF(lower_alarm_text_start_x, gauge_start_y + gauge_size_y + 10,
                                                          text_width, self._alarm_text_size + 5)

                # upper alarm level
                if self._alarm_upper_level_set:
                    upper_alarm_point_one = QtCore.QPointF(upper_alarm_pos_x, gauge_start_y + gauge_size_y + 5)
                    upper_alarm_point_two = QtCore.QPointF(upper_alarm_pos_x, gauge_start_y)
                    upper_alarm_text_rect = QtCore.QRectF(upper_alarm_text_start_x, gauge_start_y + gauge_size_y + 10,
                                                          text_width, self._alarm_text_size + 5)

        else:
            ##################################################
            # Vertical configurations
            ##################################################
            gauge_start_y = 0
            gauge_size_y = bar_height
            gauge_size_x = self._gauge_width

            # bar position
            bar_size_y = (gauge_size_y - 4) * (self._gauge_val - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
            bar_start_y = (gauge_size_y - 2) - bar_size_y
            bar_size_x = gauge_size_x - 4

            # alarm levels
            if self._alarm_lower_level_set:
                # calculate the position
                lower_alarm_pos_y = (gauge_size_y - 4) * (self._alarm_lower_level - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
                lower_alarm_pos_y = (gauge_size_y - 2) - lower_alarm_pos_y

                # calculate where to write the text
                lower_alarm_text_pos_y = lower_alarm_pos_y - 0.5 * self._alarm_text_size

                if lower_alarm_text_pos_y < 0:
                    lower_alarm_text_pos_y = 0

                if lower_alarm_text_pos_y + self._alarm_text_size + 5 > bar_height:
                    lower_alarm_text_pos_y = bar_height - self._alarm_text_size - 5

            if self._alarm_upper_level_set:
                upper_alarm_pos_y = (gauge_size_y - 4) * (self._alarm_upper_level - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
                upper_alarm_pos_y = (gauge_size_y - 2) - lower_alarm_pos_y

                # calculate where to write the text
                upper_alarm_text_pos_y = upper_alarm_pos_y - 0.5 * self._alarm_text_size

                if upper_alarm_text_pos_y < 0:
                    upper_alarm_text_pos_y = 0

                if upper_alarm_text_pos_y + self._alarm_text_size + 5 > bar_height:
                    upper_alarm_text_pos_y = bar_height - self._alarm_text_size - 5

            ##################################################
            # left and right specific calculations
            ##################################################
            if self.position == ICWidgetPosition.Left:
                ##################################################
                # Left
                ##################################################
                gauge_start_x = bar_width - gauge_size_x
                bar_start_x = gauge_start_x + 2

                # min max positions
                if self._cycle_min_tracking:
                    min_pos_y = (gauge_size_y - 4) * (self._cycle_min - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
                    min_pos_y = (gauge_size_y - 2) - min_pos_y
                    min_point_one = QtCore.QPointF(gauge_start_x + gauge_size_x, min_pos_y)
                    min_point_two = QtCore.QPointF(gauge_start_x - 5, min_pos_y)

                if self._cycle_max_tracking:
                    max_pos_y = (gauge_size_y - 4) * (self._cycle_max - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
                    max_pos_y = (gauge_size_y - 2) - max_pos_y
                    max_point_one = QtCore.QPointF(gauge_start_x + gauge_size_x, max_pos_y)
                    max_point_two = QtCore.QPointF(gauge_start_x - 5, max_pos_y)

                # target position
                if self._target_tracking:
                    target_pos_y = (gauge_size_y - 4) * (self._target_value - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
                    target_pos_y = (gauge_size_y - 2) - target_pos_y
                    target_point_one = QtCore.QPointF(gauge_start_x + gauge_size_x, target_pos_y)
                    target_point_two = QtCore.QPointF(gauge_start_x - 5, target_pos_y)

                # setup the alarm levels
                if self._alarm_lower_level_set:
                    lower_alarm_point_one = QtCore.QPointF(gauge_start_x + gauge_size_x, lower_alarm_pos_y)
                    lower_alarm_point_two = QtCore.QPointF(gauge_start_x - 5, lower_alarm_pos_y)
                    lower_alarm_text_rect = QtCore.QRectF(0, lower_alarm_text_pos_y, gauge_start_x - 10, self._alarm_text_size + 5)
                    lower_alarm_text_align = Qt.AlignRight

                if self._alarm_upper_level_set:
                    upper_alarm_point_one = QtCore.QPointF(gauge_start_x + gauge_size_x, upper_alarm_pos_y)
                    upper_alarm_point_two = QtCore.QPointF(gauge_start_x - 5, upper_alarm_pos_y)
                    upper_alarm_text_rect = QtCore.QRectF(0, upper_alarm_text_pos_y, gauge_start_x - 10, self._alarm_text_size + 5)
                    upper_alarm_text_align = Qt.AlignRight

            else:
                ##################################################
                # Right
                ##################################################
                gauge_start_x = 0
                bar_start_x = 2

                # min max positions
                if self._cycle_min_tracking:
                    min_pos_y = (gauge_size_y - 4) * (self._cycle_min - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
                    min_pos_y = (gauge_size_y - 2) - min_pos_y
                    min_point_one = QtCore.QPointF(gauge_start_x + gauge_size_x + 5, min_pos_y)
                    min_point_two = QtCore.QPointF(gauge_start_x, min_pos_y)

                if self._cycle_max_tracking:
                    max_pos_y = (gauge_size_y - 4) * (self._cycle_max - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
                    max_pos_y = (gauge_size_y - 2) - max_pos_y
                    max_point_one = QtCore.QPointF(gauge_start_x + gauge_size_x + 5, max_pos_y)
                    max_point_two = QtCore.QPointF(gauge_start_x, max_pos_y)

                # target position
                if self._target_tracking:
                    target_pos_y = (gauge_size_y - 4) * (self._target_value - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
                    target_pos_y = (gauge_size_y - 2) - target_pos_y
                    target_point_one = QtCore.QPointF(gauge_start_x + gauge_size_x + 5, target_pos_y)
                    target_point_two = QtCore.QPointF(gauge_start_x, target_pos_y)

                # setup the alarm levels
                if self._alarm_lower_level_set:
                    lower_alarm_point_one = QtCore.QPointF(gauge_start_x + gauge_size_x + 5, lower_alarm_pos_y)
                    lower_alarm_point_two = QtCore.QPointF(gauge_start_x, lower_alarm_pos_y)
                    lower_alarm_text_rect = QtCore.QRectF(gauge_start_x + gauge_size_x + 10, lower_alarm_text_pos_y,
                                                          bar_width - gauge_size_x - 10, self._alarm_text_size + 5)
                    lower_alarm_text_align = Qt.AlignLeft

                if self._alarm_upper_level_set:
                    upper_alarm_point_one = QtCore.QPointF(gauge_start_x + gauge_size_x + 5, upper_alarm_pos_y)
                    upper_alarm_point_two = QtCore.QPointF(gauge_start_x, upper_alarm_pos_y)
                    upper_alarm_text_rect = QtCore.QRectF(gauge_start_x + gauge_size_x + 10, upper_alarm_text_pos_y,
                                                          bar_width - gauge_size_x - 10, self._alarm_text_size + 5)
                    upper_alarm_text_align = Qt.AlignLeft

        ##################################################
        # paint the main rectangle
        ##################################################
        rect = QtCore.QRectF(gauge_start_x, gauge_start_y, gauge_size_x, gauge_size_y)

        if self.position.is_horizontal():
            brush = QtGui.QLinearGradient(rect.topRight(), rect.topLeft())
        else:
            brush = QtGui.QLinearGradient(rect.bottomLeft(), rect.topLeft())

        # define the filling brush
        brush.setColorAt(0, self._back_color_light)
        brush.setColorAt(1, self._back_color_dark)
        painter.setBrush(brush)

        # define the pen
        pen = QtGui.QPen(ICDisplayConfig.LinearSlideBoxColorLight)
        pen.setWidth(1)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)

        # define the path and draw
        path = QtGui.QPainterPath()
        path.setFillRule(Qt.WindingFill)
        path.addRoundedRect(rect, 10, 10)
        painter.drawPath(path)

        # leave here for frame only
        if self.state == ICWidgetState.FrameOnly:
            return

        ##################################################
        # draw the gauge bar
        ##################################################
        rect = QtCore.QRectF(bar_start_x, bar_start_y, bar_size_x, bar_size_y)

        brush = QtGui.QLinearGradient(rect.topRight(), rect.bottomLeft())

        # set the default color
        brush.setColorAt(0, self._gauge_color_normal_light)
        brush.setColorAt(1, self._gauge_color_normal_dark)

        # check if the current value is below the minimum limit
        if self._alarm_lower_level_set or self._alarm_upper_level_set:
            if self.alarm_activated:
                brush.setColorAt(0, self._gauge_color_alarm_light)
                brush.setColorAt(1, self._gauge_color_alarm_dark)

        # paint the gauge bar
        path = QtGui.QPainterPath()
        path.setFillRule(Qt.WindingFill)
        path.addRoundedRect(rect, 9, 9)
        painter.setBrush(brush)
        pen.setWidth(1)
        pen.setBrush(brush)
        painter.setPen(pen)
        painter.drawPath(path)

        ##################################################
        # draw min max tracking
        ##################################################
        pen = painter.pen()
        pen.setColor(self._min_max_color)
        pen.setWidth(4)
        painter.setPen(pen)

        if self._cycle_min_tracking:
            painter.drawLine(min_point_one, min_point_two)

        if self._cycle_max_tracking:
            painter.drawLine(max_point_one, max_point_two)

        ##################################################
        # draw target tracking
        ##################################################
        pen = painter.pen()
        pen.setColor(self._target_color)
        pen.setWidth(4)
        painter.setPen(pen)

        if self._target_tracking:
            painter.drawLine(target_point_one, target_point_two)

        ##################################################
        # draw the limits.
        ##################################################
        # setup the font and pen
        fnt = painter.font()
        fnt.setBold(True)
        fnt.setPixelSize(self._alarm_text_size)
        painter.setFont(fnt)

        # set up the pen
        pen = painter.pen()
        pen.setColor(self._alarm_text_color)
        pen.setWidth(4)
        painter.setPen(pen)

        # draw the lower level set point
        if self._alarm_lower_level_set:
            # draw the alarm level
            painter.drawLine(lower_alarm_point_one, lower_alarm_point_two)

            # setup the pen for writing the alarm text
            pen.setWidth(1)
            painter.setPen(pen)

            # draw the alarm text
            painter.drawText(lower_alarm_text_rect, lower_alarm_text_align, self._alarm_lower_level_text)

        # draw the upper level set point
        pen.setWidth(4)
        painter.setPen(pen)
        if self._alarm_upper_level_set:
            # draw the alarm level
            painter.drawLine(upper_alarm_point_one, upper_alarm_point_two)

            # setup the pen for writing the alarm text
            pen.setWidth(1)
            painter.setPen(pen)

            # draw the alarm text
            painter.drawText(upper_alarm_text_rect, upper_alarm_text_align, self._alarm_upper_level_text)


class ICLinearGauge(ICLinearAxisContainer):
    """
        Compound widget with a Gauge Bar and label for displaying the plotted value
    """

    def __init__(self, name: str, unit: str, min_val: float = 0, max_val: float = 100, display_steps: int = 5, show_title: bool = True, show_value: bool = True,
                 position: ICWidgetPosition = ICWidgetPosition.Left, widget_id: int = 0, *args, **kwargs):

        if (not show_value) and (not show_value):
            cont_type = ICLinearContainerType.BAR_NO_TITLE_NO_VALUE
        elif not show_value:
            cont_type = ICLinearContainerType.BAR_NO_VALUE
        elif not show_title:
            cont_type = ICLinearContainerType.BAR_NO_TITLE
        else:
            cont_type = ICLinearContainerType.BAR

        super(ICLinearGauge, self).__init__(cont_type, widget_id=widget_id, *args, **kwargs)

        curr_value = 0.5 * (min_val + max_val)

        # create the gauge Bar
        self.gauge_bar = ICGaugeBar(min_val, max_val, curr_value, position, widget_id)
        self.gauge_bar.changed[float].connect(self.value_changed)
        self.add_central_widget(self.gauge_bar)

        # initialise the local variables
        self.title = name
        self.value = curr_value
        self.unit = unit

        # number of steps for drawing ticks in the gauge bar
        self._display_steps: int = display_steps

        # selected values and displayed values for the scale
        self._scale_values: list[float] = []
        self._scale_displayed_values: list[str] = []

        # create the display lists
        self._scale_values, self._scale_displayed_values = ICLinearAxis.create_ticks(max_val, min_val, display_steps, "{0:.0f}")

        # add the scale bar
        self.add_first_scale_bar(name, self._scale_values, self._scale_displayed_values, ICWidgetPosition.opposite(position))

        self.vertical_gauge_width = ICDisplayConfig.LinearGaugeVerticalMaxWidth
        self.horizontal_gauge_height = ICDisplayConfig.LinearGaugeHorizontalMaxHeight

        # override the base Size policy
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)

        # call layout update to specify size
        self.on_layout_update()

    ########################################################
    # properties
    ########################################################

    ########################################################
    # functions
    ########################################################
    # override the default show event
    def showEvent(self, e):
        self.on_layout_update()

    ########################################################
    # slots
    ########################################################
    # handles the signal for value update
    # @pyqtSlot(float)
    def update_upper_alarm_level(self, new_level: float) -> None:
        nm, old_level = self.gauge_bar.upper_alarm
        self.gauge_bar.upper_alarm = (nm, new_level)

    # @pyqtSlot(float)
    def update_lower_alarm_level(self, new_level: float) -> None:
        nm, old_level = self.gauge_bar.lower_alarm
        self.gauge_bar.lower_alarm = (nm, new_level)

    ########################################################
    # base class event overrides
    ########################################################
    # change layout based on the orientation
    def on_layout_update(self) -> None:
        gauge_width = self.gauge_bar.estimate_max_gauge_width()
        if self.scale_bar_one is not None:
            scale_width = self.scale_bar_one.estimate_max_scale_width()
        if self.position.is_horizontal():
            self.size_hint = (ICDisplayConfig.LinearGaugeHorizontalWidth, ICDisplayConfig.LinearGaugeHorizontalMaxHeight)
            self.gauge_bar.size_hint = (ICDisplayConfig.LinearGaugeHorizontalWidth, gauge_width)
            if self.scale_bar_one is not None:
                self.scale_bar_one.size_hint = (ICDisplayConfig.LinearGaugeHorizontalWidth, scale_width)
        else:
            self.size_hint = (ICDisplayConfig.LinearGaugeVerticalMaxWidth, ICDisplayConfig.LinearGaugeVerticalHeight)
            self.gauge_bar.size_hint = (gauge_width, ICDisplayConfig.LinearGaugeVerticalHeight)
            if self.scale_bar_one is not None:
                self.scale_bar_one.size_hint = (scale_width, ICDisplayConfig.LinearGaugeVerticalHeight)

    def on_value_update(self, value: float) -> None:
        self.gauge_bar.gauge_value = value
