# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 17:20:01 2020

@author: Prosenjit

This displays a name value pair for a parameter.
# TODO: clickable & focusable button will allow a popup of a graph showing its history
"""

from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from typing import Union
from math import sqrt
from .display_config import ICDisplayConfig
from .base_widget import ICBaseWidget, ICWidgetState


class ICRotaryGauge(ICBaseWidget):
    """
        Basic rotary gauge to display a value
    """
    changed = pyqtSignal(float)

    def __init__(self, min_val: float, max_val: float, name: str, value: Union[int, float], unit: str, widget_id: int = 0, *args, **kwargs):
        super(ICRotaryGauge, self).__init__(widget_id, *args, **kwargs)

        # minimum and maximum value of the gauge bar
        self._gauge_range_min: float = min_val
        self._gauge_range_max: float = max_val

        # name and value of the parameter to be displayed in the text label
        self._name: str = name
        self._value: Union[int, float] = value
        self._unit: str = unit

        # has the current value lead to an alarm
        self.alarm_activated = False

        # upper alarm level for the gauge
        self._alarm_upper_level: float = 0
        self._alarm_upper_level_set: bool = False

        # lower alarm level for the gauge
        self._alarm_lower_level: float = 0
        self._alarm_lower_level_set: bool = False

        # max level tracking
        self._cycle_max: float = value
        self._cycle_max_tracking: bool = False

        # min level tracking
        self._cycle_min: float = value
        self._cycle_min_tracking: bool = False

        # target tracking
        self._target_value: float = value
        self._target_tracking: bool = False

        # format for the gauge label
        self._text_format = "{0:.1f}"

        # size of the text
        self._name_text_size: int = ICDisplayConfig.LabelTextSize
        self._value_text_size: int = ICDisplayConfig.LabelValueSize
        self._unit_text_size: int = ICDisplayConfig.UnitTextSize

        # colors
        self._container_color_light: QtGui.QColor = ICDisplayConfig.LabelBackLightColor
        self._container_color_dark: QtGui.QColor = ICDisplayConfig.LabelBackDarkColor

        # border color
        self._container_border_color: QtGui.QColor = ICDisplayConfig.LabelBorderColor

        # gauge colors normal
        self._gauge_color_normal_light: QtGui.QColor = ICDisplayConfig.LinearSlideRulerColorLight
        self._gauge_color_normal_dark: QtGui.QColor = ICDisplayConfig.LinearSlideRulerColorDark

        # gauge colors alarmed
        self._gauge_color_alarm_light: QtGui.QColor = ICDisplayConfig.LinearGaugeErrorLight
        self._gauge_color_alarm_dark: QtGui.QColor = ICDisplayConfig.LinearGaugeErrorDark

        # font colors
        self._name_color: QtGui.QColor = ICDisplayConfig.LabelNameColor
        self._value_color: QtGui.QColor = ICDisplayConfig.LabelValueColor

        # min max line color
        self._min_max_color: QtGui.QColor = ICDisplayConfig.RotaryGaugeMinMaxColor

        # target color
        self._target_color: QtGui.QColor = ICDisplayConfig.RotaryGaugeTargetColor

        # alarm level color
        self._alarm_color: QtGui.QColor = ICDisplayConfig.RotaryGaugeLimitsColor

        # sets the click-ability and focus-ability of the button
        self.clickable = True
        self.focusable = True

        # set size of the text label
        self.size_hint = (ICDisplayConfig.RotaryGaugeWidth, ICDisplayConfig.RotaryGaugeHeight)

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

    # get the name of the parameter
    @property
    def name(self) -> str:
        return self._name

    # set the name of the parameter
    @name.setter
    def name(self, nm: str) -> None:
        self._name = nm
        self.update()

    # get the parameter value
    @property
    def value(self) -> Union[int, float]:
        return self._value

    # update the parameter value
    @value.setter
    def value(self, val: Union[int, float]) -> None:
        if val > self._gauge_range_max:
            self._value = self._gauge_range_max
        elif val < self._gauge_range_min:
            self.value = self._gauge_range_min
        else:
            self._value = val

        # update the min value
        if self._cycle_min_tracking:
            if val < self._cycle_min:
                self._cycle_min = val

        # update the max value
        if self._cycle_max_tracking:
            if val > self._cycle_max:
                self._cycle_max = val

        self.alarm_activated = False
        if self._alarm_upper_level_set:
            if val > self._alarm_upper_level:
                self.alarm_activated = True

        if self._alarm_lower_level_set:
            if val < self._alarm_lower_level:
                self.alarm_activated = True

        self.update()

    # get the name of the parameter
    @property
    def unit(self) -> str:
        return self._unit

    # set the name of the parameter
    @unit.setter
    def unit(self, nm: str) -> None:
        self._name = nm
        self.update()

    @property
    def upper_alarm(self) -> Union[float, None]:
        if self._alarm_upper_level_set:
            return self._alarm_upper_level
        else:
            return None

    # set the upper level alarm
    @upper_alarm.setter
    def upper_alarm(self, alarm: float) -> None:
        # check if upper alarm level is greater than the lower alarm level
        if self._alarm_lower_level_set:
            if alarm < self._alarm_lower_level:
                return

        # check if the limit value is in between the max and min values
        if self._gauge_range_min <= alarm <= self._gauge_range_max:
            self._alarm_upper_level_set = True
            self._alarm_upper_level = alarm

            # check for alarm level
            if self._value > self._alarm_upper_level:
                self.alarm_activated = True
                self.changed.emit(self._value)

            self.update()

    @property
    def lower_alarm(self) -> Union[float, None]:
        if self._alarm_lower_level_set:
            return self._alarm_lower_level
        else:
            return None

    # set the upper level alarm
    @lower_alarm.setter
    def lower_alarm(self, alarm: float) -> None:
        # check if upper alarm level is lower than the upper alarm level
        if self._alarm_upper_level_set:
            if alarm > self._alarm_upper_level:
                return

        # check if the limit value is in between the max and min values
        if self._gauge_range_min <= alarm <= self._gauge_range_max:
            self._alarm_lower_level_set = True
            self._alarm_lower_level = alarm

            # check for alarm level
            if self._value < self._alarm_lower_level:
                self.alarm_activated = True
                self.changed.emit(self._value)

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

    # text format
    @property
    def text_format(self) -> str:
        return self._text_format

    @text_format.setter
    def text_format(self, fmt: str) -> None:
        self._text_format = fmt
        self.update()

    # text size
    @property
    def name_text_size(self) -> int:
        return self._name_text_size

    @name_text_size.setter
    def name_text_size(self, sz: int) -> None:
        self._name_text_size = sz
        self.update()

    # text size
    @property
    def value_text_size(self) -> int:
        return self._value_text_size

    @value_text_size.setter
    def value_text_size(self, sz: int) -> None:
        self._value_text_size = sz
        self.update()

    # text size
    @property
    def unit_text_size(self):
        return self._unit_text_size

    @unit_text_size.setter
    def unit_text_size(self, sz: int) -> None:
        self._unit_text_size = sz
        self.update()

    # get the background container color of the bar
    @property
    def container_colors(self) -> tuple[QtGui.QColor, QtGui.QColor]:
        return self._container_color_light, self._container_color_dark

    # set the background color of the bar
    @container_colors.setter
    def container_colors(self, clrs: tuple[QtGui.QColor, QtGui.QColor]) -> None:
        self._container_color_light = clrs[0]
        self._container_color_dark = clrs[1]
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

    # target color
    @property
    def alarm_color(self) -> QtGui.QColor:
        return self._alarm_color

    @target_color.setter
    def target_color(self, clr: QtGui.QColor) -> None:
        self._alarm_color = clr
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

    ########################################################
    # overrides and event handlers
    ########################################################
    # redraw the widget
    def redraw(self, painter: QtGui.QPainter, event) -> None:
        # if the button is hidden then there is nothing to draw
        if self._state == ICWidgetState.Hidden:
            return

        ########################################
        # draw the label area
        ########################################
        temp_width = painter.device().width()
        temp_height = painter.device().height()

        # define the rectangle to draw the button
        rect = QtCore.QRectF(3, 3, temp_width - 6, temp_height - 6)

        # path to be drawn
        path = QtGui.QPainterPath()
        path.setFillRule(Qt.WindingFill)
        path.addRoundedRect(rect, 10, 10)

        # brush to fill the area
        brush = QtGui.QLinearGradient(rect.topLeft(), rect.bottomRight())
        if self._state == ICWidgetState.Transparent:
            brush.setColorAt(0, self.background_color)
            brush.setColorAt(1, self.background_color)
        else:
            brush.setColorAt(0, self._container_color_dark)
            brush.setColorAt(1, self._container_color_light)

        painter.setBrush(brush)

        # define the border pen
        if self._state == ICWidgetState.Transparent:
            pen = QtGui.QPen(self.background_color)
        else:
            pen = QtGui.QPen(self._container_border_color)

        if self.in_focus:
            pen.setWidth(3)
        else:
            pen.setWidth(1)

        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)

        # draw the rectangle
        painter.drawPath(path)

        ########################################
        # draw the text only if the button is visible
        ########################################
        if self._state in (ICWidgetState.VisibleEnabled, ICWidgetState.VisibleDisabled):
            # adjust the coordinate system for the border
            painter.translate(3, 3)
            temp_height -= 6
            temp_width -= 6

            ########################################
            # draw the name and unit
            ########################################
            fnt = painter.font()
            fnt.setBold(True)
            fnt.setPixelSize(self._name_text_size)
            painter.setFont(fnt)
            pen.setColor(self._name_color)
            painter.setPen(pen)
            half_width = 0.5 * temp_width
            rect = QtCore.QRectF(0, temp_height - (self._name_text_size + 5), half_width, self._name_text_size + 5)
            painter.drawText(rect, Qt.AlignRight, str(self._name))

            # draw the unit
            fnt.setPixelSize(self._unit_text_size)
            painter.setFont(fnt)
            rect = QtCore.QRectF(half_width, temp_height - (self._unit_text_size + 5), half_width, self._unit_text_size + 5)
            painter.drawText(rect, Qt.AlignLeft, " ({})".format(self._unit))

            # adjust for remaining height
            temp_height -= max(self._name_text_size, self._unit_text_size)

            ########################################
            # draw the value
            ########################################
            fnt.setPixelSize(self._value_text_size)
            painter.setFont(fnt)
            pen.setColor(self._value_color)
            painter.setPen(pen)

            # calculate dimension for the text and rotary gauge
            font_matrices = QtGui.QFontMetrics(fnt)
            text_size = font_matrices.horizontalAdvance(str(self._value))
            box_length = sqrt(2) * (max(text_size, self._value_text_size + 5) + 5)

            # draw the value
            rect = QtCore.QRectF(10, (temp_height - (self._value_text_size + 5))/2, temp_width - 20, self._value_text_size + 5)
            painter.drawText(rect, Qt.AlignCenter, self._text_format.format(self._value))

            ########################################
            # main gauge
            ########################################
            # create the gradient
            half_height = 0.5 * temp_height
            gradient = QtGui.QConicalGradient(half_width, half_height, 90)
            if self.alarm_activated:
                gradient.setColorAt(0, self._gauge_color_alarm_light)
                gradient.setColorAt(1, self._gauge_color_alarm_dark)
            else:
                gradient.setColorAt(0, self._gauge_color_normal_light)
                gradient.setColorAt(1, self._gauge_color_normal_dark)

            painter.setBrush(gradient)
            pen.setBrush(gradient)
            painter.setPen(pen)

            # calculate the path
            path = QtGui.QPainterPath()
            path.setFillRule(Qt.OddEvenFill)
            theta = 360 * (self._value - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)

            # smaller radius
            half_box_length = box_length/2
            rect = QtCore.QRectF(half_width - half_box_length, half_height - half_box_length, box_length, box_length)
            path.moveTo(half_width, half_height - half_box_length)
            path.arcTo(rect, 90, -theta)
            pos = path.currentPosition()

            # bigger radius
            bigger_box_half_length = min(half_width, half_height) - 10
            rect_big = QtCore.QRectF(half_width - bigger_box_half_length, half_height - bigger_box_half_length,
                                     2 * bigger_box_half_length, 2 * bigger_box_half_length)
            new_x = half_width + (pos.x() - half_width) * bigger_box_half_length / half_box_length
            new_y = half_height + (pos.y() - half_height) * bigger_box_half_length / half_box_length
            path.lineTo(new_x, new_y)
            path.arcTo(rect_big, 90 - theta, theta)
            path.closeSubpath()

            # paint the gauge
            painter.drawPath(path)

            # draw gauge border
            pen = QtGui.QPen(self._container_border_color)
            pen.setWidth(1)
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(QtGui.QBrush())
            painter.drawEllipse(rect)
            painter.drawEllipse(rect_big)

            ########################################
            # target line
            ########################################
            if self._target_tracking:
                theta = 360 * (self._target_value - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)

                # calculate the path
                path = QtGui.QPainterPath()
                path.arcMoveTo(rect, 90 - theta)
                pos = path.currentPosition()
                new_x = half_width + (pos.x() - half_width) * bigger_box_half_length / half_box_length
                new_y = half_height + (pos.y() - half_height) * bigger_box_half_length / half_box_length
                path.lineTo(new_x, new_y)

                # set up the pen
                pen.setColor(self._target_color)
                pen.setWidth(2)
                painter.setPen(pen)
                painter.drawPath(path)

            ########################################
            # min max lines
            ########################################
            if self._cycle_min_tracking:
                theta = 360 * (self._cycle_min - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)

                # calculate the path
                path = QtGui.QPainterPath()
                path.arcMoveTo(rect, 90 - theta)
                pos = path.currentPosition()
                new_x = half_width + (pos.x() - half_width) * bigger_box_half_length / half_box_length
                new_y = half_height + (pos.y() - half_height) * bigger_box_half_length / half_box_length
                path.lineTo(new_x, new_y)

                # set up the pen
                pen.setColor(self._min_max_color)
                pen.setWidth(2)
                painter.setPen(pen)
                painter.drawPath(path)

            if self._cycle_max_tracking:
                theta = 360 * (self._cycle_max - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)

                # calculate the path
                path = QtGui.QPainterPath()
                path.arcMoveTo(rect, 90 - theta)
                pos = path.currentPosition()
                new_x = half_width + (pos.x() - half_width) * bigger_box_half_length / half_box_length
                new_y = half_height + (pos.y() - half_height) * bigger_box_half_length / half_box_length
                path.lineTo(new_x, new_y)

                # set up the pen
                pen.setColor(self._min_max_color)
                pen.setWidth(2)
                painter.setPen(pen)
                painter.drawPath(path)

            ########################################
            # upper and lower alarm lines
            ########################################
            if self._alarm_lower_level_set:
                theta = 360 * (self._alarm_lower_level - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)

                # calculate the path
                path = QtGui.QPainterPath()
                path.arcMoveTo(rect, 90 - theta)
                pos = path.currentPosition()
                new_x = half_width + (pos.x() - half_width) * bigger_box_half_length / half_box_length
                new_y = half_height + (pos.y() - half_height) * bigger_box_half_length / half_box_length
                path.lineTo(new_x, new_y)

                # set up the pen
                pen.setColor(self._alarm_color)
                pen.setWidth(2)
                painter.setPen(pen)
                painter.drawPath(path)

            if self._alarm_upper_level_set:
                theta = 360 * (self._alarm_upper_level - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)

                # calculate the path
                path = QtGui.QPainterPath()
                path.arcMoveTo(rect, 90 - theta)
                pos = path.currentPosition()
                new_x = half_width + (pos.x() - half_width) * bigger_box_half_length / half_box_length
                new_y = half_height + (pos.y() - half_height) * bigger_box_half_length / half_box_length
                path.lineTo(new_x, new_y)

                # set up the pen
                pen.setColor(self._alarm_color)
                pen.setWidth(2)
                painter.setPen(pen)
                painter.drawPath(path)

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.redraw(painter, e)
