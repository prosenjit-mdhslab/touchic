# -*- coding: utf-8 -*-
"""
Created on Wed Apr  1 09:23:22 2020

@author: prosenjit

Custom Qt Widget to show a linear gauge with min-max. The following modifiable
attributes are exposed.

"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from .display_config import ICDisplayConfig


class ICGaugeBar(QtWidgets.QWidget):
    # bar state has changed signal. it can be current value or alarm status
    changed = pyqtSignal(float)

    # shift the bar in x
    X_OFFSET = -2

    def __init__(self, min_val: float, max_val: float, curr_val: float, steps: int, *args, **kwargs):
        super(ICGaugeBar, self).__init__(*args, **kwargs)
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
        self._cycle_max = curr_val
        self._cycle_max_tracking = False

        # min level tracking
        self._cycle_min = curr_val
        self._cycle_min_tracking = False

        # number of steps for drawing ticks in the gauge bar
        self._display_steps: int = steps

        # size (width and height) hint for the
        self._width: int = ICDisplayConfig.LinearGaugeWidth
        self._height: int = ICDisplayConfig.LinearGuageHeight

        # background colors
        self._back_color_light: QtGui.QColor = ICDisplayConfig.LinearGaugeBoxColorLight
        self._back_color_dark: QtGui.QColor = ICDisplayConfig.LinearGaugeBoxColorDark

        # gauge colors
        self._gauge_color_normal_light: QtGui.QColor = ICDisplayConfig.LinearGaugeNormalLight
        self._gauge_color_normal_dark: QtGui.QColor = ICDisplayConfig.LinearGaugeNormalDark
        self._gauge_color_alarm_light: QtGui.QColor = ICDisplayConfig.LinearGaugeErrorLight
        self._gauge_color_alarm_dark: QtGui.QColor = ICDisplayConfig.LinearGaugeErrorDark

        # y axis tick color
        self._tick_color: QtGui.QColor = ICDisplayConfig.LinearGaugeRulerColor

        # y axis tick text size
        self._tick_text_size: int = ICDisplayConfig.GeneralTextSize

        # alarm level text size
        self._alarm_text_size: int = ICDisplayConfig.LabelTextSize

        # alarm level text color
        self._alarm_text_color: QtGui.QColor = ICDisplayConfig.LinearGaugeLimitsColor

        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

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

    # get the current value
    @property
    def gauge_value(self) -> float:
        return self._gauge_val

    # set the current value
    @gauge_value.setter
    def gauge_value(self, val: float) -> None:
        if self._gauge_val != val:
            self._gauge_val = val

            # update the min value
            if self._cycle_min_tracking:
                if val < self._cycle_min:
                    self._cycle_min = val

            # update the max value
            if self._cycle_max_tracking:
                if val > self._cycle_max:
                    self._cycle_max = val

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
    # tupple of (name, value)
    @property
    def upper_alarm(self) -> [str, float]:
        if self._alarm_upper_level_set:
            return self._alarm_upper_level_text, self._alarm_upper_level
        else:
            return None, None

    # set the upper level alarm
    @upper_alarm.setter
    def upper_alarm(self, alarm: [str, float]) -> None:
        # check if upper alarm level is greater than the lower alarm level
        if self._alarm_lower_level_set:
            if alarm[1] < self._alarm_lower_level:
                return
        # check if the limit value is in between the max and min values
        if self._gauge_range_min <= alarm[1] <= self._gauge_range_max:
            self._alarm_upper_level_set = True
            self._alarm_upper_level = alarm[1]
            self._alarm_upper_level_text = alarm[0]
            if self._gauge_val > self._alarm_upper_level:
                self.alarm_activated = True
                self.changed.emit(self._gauge_val)
            self.update()

    # get the lower level alarm
    # tupple of (name, value)
    @property
    def lower_alarm(self) -> [str, float]:
        if self._alarm_lower_level_set:
            return self._alarm_lower_level_text, self._alarm_lower_level
        else:
            return None, None

    # set the upper level alarm
    @lower_alarm.setter
    def lower_alarm(self, alarm: [str, float]) -> None:
        # check if lower alarm level is less the upper alarm level
        if self._alarm_upper_level_set:
            if alarm[1] > self._alarm_upper_level:
                return
        # check if the limit value is in between the max and min values
        if self._gauge_range_min <= alarm[1] <= self._gauge_range_max:
            self._alarm_lower_level_set = True
            self._alarm_lower_level = alarm[1]
            self._alarm_lower_level_text = alarm[0]
            if self._gauge_val < self._alarm_lower_level:
                self.alarm_activated = True
                self.changed.emit(self._gauge_val)
            self.update()

    # get the number of steps for drawing the ticks
    @property
    def num_steps(self) -> int:
        return self._display_steps

    # set the number of steps for drawing the ticks
    @num_steps.setter
    def num_steps(self, stp: int) -> None:
        self._display_steps = stp
        self.update()

    # get the current size hint
    @property
    def size_hint(self) -> [int, int]:
        return self._width, self._height

    # set the size hint of the widget
    @size_hint.setter
    def size_hint(self, sz: [int, int]) -> None:
        self._width = sz[0]
        self._height = sz[1]

    # get the background color of the bar
    @property
    def back_colors(self) -> [QtGui.QColor, QtGui.QColor]:
        return self._back_color_light, self._back_color_dark

    # set the background color of the bar
    @back_colors.setter
    def back_colors(self, clrs: [QtGui.QColor, QtGui.QColor]) -> None:
        self._back_color_light = clrs[0]
        self._back_color_dark = clrs[1]
        self.update()

    # get the tick text size
    @property
    def tick_text_size(self) -> int:
        return self._tick_text_size

    # set the tick text size
    @tick_text_size.setter
    def tick_text_size(self, sz: int) -> None:
        self._tick_text_size = sz

    # get the tick color
    @property
    def tick_color(self) -> QtGui.QColor:
        return self._tick_color

    # set the tick color
    @tick_color.setter
    def tick_color(self, clr: QtGui.QColor) -> None:
        self._tick_color = clr

    # get the normal gauge color
    @property
    def gauge_color_normal(self) -> [QtGui.QColor, QtGui.QColor]:
        return self._gauge_color_normal_light, self._gauge_color_normal_dark

    # set the normal gauge color
    @gauge_color_normal.setter
    def gauge_color_normal(self, clr: [QtGui.QColor, QtGui.QColor]) -> None:
        self._gauge_color_normal_light = clr[0]
        self._gauge_color_normal_dark = clr[1]
        self.update()

    # get the alarm gauge color
    @property
    def gauge_color_alarm(self) -> [QtGui.QColor, QtGui.QColor]:
        return self._gauge_color_alarm_light, self._gauge_color_alarm_dark

    # set the normal gauge color
    @gauge_color_alarm.setter
    def gauge_color_alarm(self, clr: [QtGui.QColor, QtGui.QColor]) -> None:
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

    # size hint for the layout manager
    def sizeHint(self):
        return QtCore.QSize(self._width, self._height)

    # size hint for the layout manager
    def minimumSizeHint(self):
        return QtCore.QSize(self._width, self._height)

    # override the default paint event
    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # get the size of the containing widget
        tmp_wdth = painter.device().width()
        tmp_hght = painter.device().height()

        # paint the main rectangle
        rect = QtCore.QRectF(tmp_wdth / 3 + self.X_OFFSET, 0, tmp_wdth / 3, tmp_hght)

        # define the filling brush
        brush = QtGui.QLinearGradient(rect.topLeft(), rect.bottomRight())
        brush.setColorAt(0, self._back_color_light)
        brush.setColorAt(1, self._back_color_dark)
        painter.setBrush(brush)

        # define the pen
        pen = QtGui.QPen()
        pen.setWidth(1)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setBrush(brush)
        painter.setPen(pen)

        # define the path and draw
        path = QtGui.QPainterPath()
        path.setFillRule(Qt.WindingFill)
        path.addRoundedRect(rect, 10, 10)
        painter.drawPath(path)

        # modify the pen to draw the vertical scale bar
        pen.setWidth(3)
        pen.setBrush(self._tick_color)
        painter.setPen(pen)

        # draw the vertical line
        rule_loc = (tmp_wdth / 3 + self.X_OFFSET) - 5
        painter.drawLine(QtCore.QPointF(rule_loc, 0), QtCore.QPointF(rule_loc, tmp_hght))

        # modify the font to write the scale
        fnt = painter.font()
        fnt.setPixelSize(self._tick_text_size)
        painter.setFont(fnt)

        # calculate the increments in the gauge scale and display scale
        incr = tmp_hght / self._display_steps
        txt_incr = (self._gauge_range_max - self._gauge_range_min) / self._display_steps

        # loop and draw the scales
        for n in range(self._display_steps):
            pos = tmp_hght - int(n * incr)
            painter.drawLine(QtCore.QPointF(rule_loc, pos), QtCore.QPointF(rule_loc - 5, pos))
            val = self._gauge_range_min + txt_incr * n
            if n == 0:
                rect = QtCore.QRectF(0, pos - 20, rule_loc - 7, self._tick_text_size + 5)
            else:
                rect = QtCore.QRectF(0, pos - 10, rule_loc - 7, self._tick_text_size + 5)
            painter.drawText(rect, Qt.AlignRight, "{}".format(int(val)))

        painter.drawLine(QtCore.QPointF(rule_loc, 0), QtCore.QPointF(rule_loc - 5, 0))
        rect = QtCore.QRectF(0, 0, rule_loc - 7, self._tick_text_size + 5)
        painter.drawText(rect, Qt.AlignRight, "{}".format(int(self._gauge_range_max)))

        # draw the gauge bar only if the current value between the min and max value
        if self._gauge_range_max >= self._gauge_val >= self._gauge_range_min:
            # define the gauge bar
            pos = tmp_hght * (self._gauge_val - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
            rect = QtCore.QRectF(tmp_wdth / 3 + self.X_OFFSET, tmp_hght - pos, tmp_wdth / 3, pos)

            # set the default color
            brush = QtGui.QLinearGradient(rect.topLeft(), rect.bottomRight())
            brush.setColorAt(0, self._gauge_color_normal_light)
            brush.setColorAt(1, self._gauge_color_normal_dark)

            # check if the current value is below the minimum limit
            if self._alarm_lower_level_set:
                if self._gauge_val <= self._alarm_lower_level:
                    brush.setColorAt(0, self._gauge_color_alarm_light)
                    brush.setColorAt(1, self._gauge_color_alarm_dark)

            # check if the current value is above the maximum limit
            if self._alarm_upper_level_set:
                if self._gauge_val >= self._alarm_upper_level:
                    brush.setColorAt(0, self._gauge_color_alarm_light)
                    brush.setColorAt(1, self._gauge_color_alarm_dark)

            # paint the gauge bar
            path = QtGui.QPainterPath()
            path.setFillRule(Qt.WindingFill)
            path.addRoundedRect(rect, 10, 10)
            painter.setBrush(brush)
            pen.setWidth(1)
            pen.setBrush(brush)
            painter.setPen(pen)
            painter.drawPath(path)

        # draw tracking min and max
        pen = painter.pen()
        pen.setColor(self._tick_color)
        pen.setWidth(4)
        painter.setPen(pen)
        if self._cycle_min_tracking:
            val = self._cycle_min
            pos = tmp_hght * (val - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
            painter.drawLine(QtCore.QPointF(tmp_wdth / 3 + self.X_OFFSET, tmp_hght - pos),
                             QtCore.QPointF(2 * tmp_wdth / 3 + self.X_OFFSET + 10, tmp_hght - pos))

        if self._cycle_max_tracking:
            val = self._cycle_max
            pos = tmp_hght * (val - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
            painter.drawLine(QtCore.QPointF(tmp_wdth / 3 + self.X_OFFSET, tmp_hght - pos),
                             QtCore.QPointF(2 * tmp_wdth / 3 + self.X_OFFSET + 10, tmp_hght - pos))

        # draw the limits. setup the font and pen
        fnt.setBold(True)
        fnt.setPixelSize(self._alarm_text_size)
        painter.setFont(fnt)
        pen = painter.pen()
        pen.setColor(self._alarm_text_color)

        # draw the lower level set point
        if self._alarm_lower_level_set:
            val = self._alarm_lower_level
            pos = tmp_hght * (val - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
            pen.setWidth(4)
            painter.setPen(pen)
            painter.drawLine(QtCore.QPointF(tmp_wdth / 3 + self.X_OFFSET, tmp_hght - pos),
                             QtCore.QPointF(2 * tmp_wdth / 3 + self.X_OFFSET + 10, tmp_hght - pos))
            pen.setWidth(1)
            painter.setPen(pen)
            rect = QtCore.QRectF(2 * tmp_wdth / 3 + self.X_OFFSET + 3.0, tmp_hght - pos - 20, tmp_wdth / 3,
                                 self._alarm_text_size + 5)
            painter.drawText(rect, Qt.AlignLeft, self._alarm_lower_level_text)

        # draw the upper level set point
        if self._alarm_upper_level_set:
            val = self._alarm_upper_level
            pos = tmp_hght * (val - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
            pen.setWidth(4)
            painter.setPen(pen)
            painter.drawLine(QtCore.QPointF(tmp_wdth / 3 + self.X_OFFSET, tmp_hght - pos),
                             QtCore.QPointF(2 * tmp_wdth / 3 + self.X_OFFSET + 10, tmp_hght - pos))
            pen.setWidth(1)
            painter.setPen(pen)
            rect = QtCore.QRectF(2 * tmp_wdth / 3 + self.X_OFFSET + 3.0, tmp_hght - pos - 20, tmp_wdth / 3,
                                 self._alarm_upper_level + 5)
            painter.drawText(rect, Qt.AlignLeft, self._alarm_upper_level_text)


class ICLinearGauge(QtWidgets.QWidget):

    def __init__(self, name: str, unit: str, min_val: float = 0, max_val: float = 100, display_steps: int = 5,
                 *args, **kwargs):
        super(ICLinearGauge, self).__init__(*args, **kwargs)

        # create the local variables
        self._gauge_name = name
        self._gauge_value = 0.5 * (min_val + max_val)
        self._gauge_unit = unit

        # create the Gauge Bar
        self.gauge_bar = ICGaugeBar(min_val, max_val, self._gauge_value, display_steps)
        self.gauge_bar.changed.connect(self.value_changed)

        # title and value text color
        self._title_color: QtGui.QColor = ICDisplayConfig.HeaderTextColor
        self._value_color: QtGui.QColor = ICDisplayConfig.ValueTextColor

        self._error_back_color: QtGui.QColor = ICDisplayConfig.ErrorTextBackColor
        self._error_text_color: QtGui.QColor = ICDisplayConfig.ErrorTextColor

        # title and value text size
        self._title_size: int = ICDisplayConfig.LabelTextSize
        self._value_size: int = ICDisplayConfig.LabelTextSize

        # unit text size
        self._unit_size: int = ICDisplayConfig.UnitTextSize

        # fixed gauge width
        self._gauge_width: int = ICDisplayConfig.LinearGaugeWidth

        # create the vertical layout
        layout = QtWidgets.QVBoxLayout()

        # title of the Linear Gauge
        self._title_disp = QtWidgets.QLabel("", self)
        self._title_disp.setStyleSheet("QLabel { background-color : " +
                                       ICDisplayConfig.QtColorToSting(ICDisplayConfig.BackgroundColor) + "; color : " +
                                       ICDisplayConfig.QtColorToSting(self._title_color) + ";}")
        self._title_disp.setAlignment(Qt.AlignCenter)
        self._title_disp.setText("<span style='font-size:" + "{}".format(self._title_size) + "pt;'>" +
                                 self._gauge_name + "</span> <span style='font-size:" +
                                 "{}".format(self._unit_size) + "pt;'>(" + self._gauge_unit + ")</span>")
        # add the title
        layout.addWidget(self._title_disp)

        # add the gauge
        layout.addWidget(self.gauge_bar)

        # display value below the gauge
        self._value_disp = QtWidgets.QLabel("", self)
        self._value_disp.setStyleSheet("QLabel { background-color : " +
                                       ICDisplayConfig.QtColorToSting(ICDisplayConfig.BackgroundColor) + "; color : " +
                                       ICDisplayConfig.QtColorToSting(self._value_color) +
                                       ";  border-radius : 5px;}")
        self._value_disp.setAlignment(Qt.AlignCenter)
        self._value_disp.setText("<span style='font-size:" + "{}".format(self._value_size) + "pt;'>" +
                                 "{:.2f}".format(self._gauge_value) + "</span> <span style='font-size:" +
                                 "{}".format(self._unit_size) + "pt;'>" + self._gauge_unit + "</span>")

        # add the value
        layout.addWidget(self._value_disp)

        self.setLayout(layout)

        # set the width of the gauge
        self.setFixedWidth(self._gauge_width)
        self.setStyleSheet("background-color : " +
                           ICDisplayConfig.QtColorToSting(ICDisplayConfig.BackgroundColor) + ";")

    # value changed in the
    @pyqtSlot(float)
    def value_changed(self, val: float) -> None:
        if self._gauge_value != val:
            self._gauge_value = val
        self.local_update()

    # get the gauge title
    @property
    def name(self) -> str:
        return self._gauge_name

    # set the gauge title
    @name.setter
    def name(self, nm: str) -> None:
        self._gauge_name = nm
        self.local_update()

    # get current value of the gauge
    @property
    def value(self) -> float:
        return self._gauge_value

    # set the current value of the gauge
    @value.setter
    def value(self, val: float) -> None:
        if self._gauge_value != val:
            self._gauge_value = val
        if self.gauge_bar.gauge_value != val:
            self.gauge_bar.gauge_value = val
        self.local_update()

    # get the current unit
    @property
    def unit(self) -> str:
        return self._gauge_unit

    # set the gauge unit
    @unit.setter
    def unit(self, un: str) -> None:
        self._gauge_unit = un
        self.local_update()

    # get the color of the title
    @property
    def title_text_color(self) -> QtGui.QColor:
        return self._title_color

    # set the title color
    @title_text_color.setter
    def title_text_color(self, clr: QtGui.QColor) -> None:
        self._title_color = clr
        self.local_update()

    # get the color of the title
    @property
    def value_text_color(self) -> QtGui.QColor:
        return self._value_color

    # set the title color
    @value_text_color.setter
    def value_text_color(self, clr: QtGui.QColor) -> None:
        self._value_color = clr
        self.local_update()

    # get the color of alarm text
    @property
    def alarm_colors(self) -> [QtGui.QColor, QtGui.QColor]:
        return self._error_back_color, self._error_text_color

    # set the color of alarm text
    @alarm_colors.setter
    def alarm_colors(self, clrs: [QtGui.QColor, QtGui.QColor]) -> None:
        self._error_back_color = clrs[0]
        self._error_text_color = clrs[1]
        self.local_update()

    # get the width of the gauge
    @property
    def gauge_width(self) -> int:
        return self._gauge_width

    # set the width of the gauge
    @gauge_width.setter
    def gauge_width(self, wd: int) -> None:
        self._gauge_width = wd
        self.setFixedWidth(wd)
        self.local_update()

    # get the size of the title text
    @property
    def title_size(self) -> int:
        return self._title_size

    # set the size of the title text
    @title_size.setter
    def title_size(self, sz: int) -> None:
        self._title_size = sz
        self.local_update()

    # get the size of the value text
    @property
    def value_size(self) -> int:
        return self._value_size

    # set the size of the title text
    @value_size.setter
    def value_size(self, sz: int) -> None:
        self._value_size = sz
        self.local_update()

    # get the size of the title text
    @property
    def unit_size(self) -> int:
        return self._unit_size

    # set the size of the title text
    @unit_size.setter
    def unit_size(self, sz: int) -> None:
        self._unit_size = sz
        self.local_update()

    # update the widget
    def local_update(self):
        # update the title text
        self._title_disp.setStyleSheet("QLabel { background-color : " +
                                       ICDisplayConfig.QtColorToSting(ICDisplayConfig.BackgroundColor) + "; color : " +
                                       ICDisplayConfig.QtColorToSting(self._title_color) + ";}")
        self._title_disp.setAlignment(Qt.AlignCenter)
        self._title_disp.setText("<span style='font-size:" + "{}".format(self._title_size) + "pt;'>" +
                                 self._gauge_name + "</span> <span style='font-size:" + "{}".format(self._unit_size) +
                                 "pt;'>(" + self._gauge_unit + ")</span>")
        self._title_disp.update()
        # update the value text
        if self.gauge_bar.alarm_activated:
            self._value_disp.setStyleSheet("QLabel { background-color : " +
                                           ICDisplayConfig.QtColorToSting(self._error_back_color) +
                                           "; color : " +
                                           ICDisplayConfig.QtColorToSting(self._error_text_color) +
                                           "; border-radius : 5px; }")
        else:
            self._value_disp.setStyleSheet("QLabel { background-color : " +
                                           ICDisplayConfig.QtColorToSting(ICDisplayConfig.BackgroundColor) +
                                           "; color : " +
                                           ICDisplayConfig.QtColorToSting(self._value_color) +
                                           "; border-radius : 5px; }")

        self._value_disp.setText("<span style='font-size:" + "{}".format(self._value_size) + "pt;'>" +
                                 "{:.2f}".format(self._gauge_value) + "</span> <span style='font-size:" +
                                 "{}".format(self._unit_size) + "pt;'>" + self._gauge_unit + "</span>")
        self._value_disp.update()
        self.gauge_bar.update()

    # handles the signal for value update
    @pyqtSlot(float)
    def set_value(self, val: float) -> None:
        self.value = val

    @pyqtSlot(float)
    def update_upper_alarm_level(self, new_level: float) -> None:
        nm, old_level = self.gauge_bar.upper_alarm
        self.gauge_bar.upper_alarm = (nm, new_level)

    @pyqtSlot(float)
    def update_lower_alarm_level(self, new_level: float) -> None:
        nm, old_level = self.gauge_bar.lower_alarm
        self.gauge_bar.lower_alarm = (nm, new_level)
