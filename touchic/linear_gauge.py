# -*- coding: utf-8 -*-
"""
Created on May  19 2021

@author: Prosenjit

Custom Qt Widget to show a linear gauge with min-max. The following modifiable
attributes are exposed.
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from .display_config import ICDisplayConfig
from .base_widget import ICBaseWidget, ICWidgetState, ICWidgetOrientation, ICWidgetPosition
from .linear_axis import ICLinearAxis


class ICGaugeBar(ICBaseWidget):
    """
    Class for a custom widget to draw a colored bar.
    Length of the colored bar is proportional to the value.
    """

    # bar state has changed signal. it can be current value or alarm status
    changed = pyqtSignal(float)

    def __init__(self, min_val: float, max_val: float, curr_val: float, widget_id: int = 0,
                 orientation: ICWidgetOrientation = ICWidgetOrientation.Vertical, *args, **kwargs):
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
        self._cycle_max = curr_val
        self._cycle_max_tracking = False

        # min level tracking
        self._cycle_min = curr_val
        self._cycle_min_tracking = False

        # position of the scale bar
        self._position = ICWidgetPosition.Bottom \
            if orientation == ICWidgetOrientation.Horizontal \
            else ICWidgetPosition.Left

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
        self._min_max_color: QtGui.QColor = ICDisplayConfig.LinearGaugeRulerColor

        # sets the click-ability and focus-ability of the button
        self.clickable = True
        self.focusable = True

        # set the orientation
        self.orientation = orientation

        # override the base Size policy
        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

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
            # limit gaugle value to the min and max range
            if self._gauge_val < self._gauge_range_min:
                self._gauge_val = self._gauge_range_min
            elif self._gauge_val > self._gauge_range_max:
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
            self._alarm_lower_level_text = alarm[0]
            self._alarm_lower_level = alarm[1]

            # check if alarm is active
            if self._gauge_val < self._alarm_lower_level:
                self.alarm_activated = True
                self.changed.emit(self._gauge_val)
            self.update()

    # get the current scale position
    @property
    def position(self) -> ICWidgetPosition:
        return self._position

    @position.setter
    def position(self, pos: ICWidgetPosition) -> None:
        if self.orientation == ICWidgetOrientation.Horizontal:
            if pos in (ICWidgetPosition.Top, ICWidgetPosition.Bottom):
                self._position = pos
                self.update()
        else:
            if pos in (ICWidgetPosition.Left, ICWidgetPosition.Right):
                self._position = pos
                self.update()

    # get the background container color of the bar
    @property
    def container_colors(self) -> [QtGui.QColor, QtGui.QColor]:
        return self._back_color_light, self._back_color_dark

    # set the background color of the bar
    @container_colors.setter
    def container_colors(self, clrs: [QtGui.QColor, QtGui.QColor]) -> None:
        self._back_color_light = clrs[0]
        self._back_color_dark = clrs[1]
        self.update()

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

    # min max color
    @property
    def min_max_color(self) -> QtGui.QColor:
        return self._min_max_color

    @min_max_color.setter
    def min_max_color(self, clr: QtGui.QColor) -> None:
        self._min_max_color = clr
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
    # base class event overrides
    ########################################################
    # TODO: mouse click plots the history
    def on_mouse_released(self, event: QtGui.QMouseEvent) -> None:
        pass

    # on orientation change fix the position
    def on_orientation_changed(self) -> None:
        if self.orientation == ICWidgetOrientation.Horizontal:
            if self._position not in (ICWidgetPosition.Top, ICWidgetPosition.Bottom):
                self._position = ICWidgetPosition.Bottom
                self.update()
        else:
            if self._position not in (ICWidgetPosition.Left, ICWidgetPosition.Right):
                self._position = ICWidgetPosition.Right
                self.update()

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
        tmp_wdth = painter.device().width()
        tmp_hght = painter.device().height()

        # if widget is in focus then draw the focus selector
        if self.in_focus:
            # overall widget rect
            rect = QtCore.QRectF(1, 1, tmp_wdth - 2, tmp_hght - 2)

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

        # readjust the width and height
        tmp_wdth -= 6
        tmp_hght -= 6

        # move origin to 3,3
        painter.translate(3, 3)

        # paint the main rectangle
        vert_gauge_bar_width = 0.5 * tmp_wdth
        horz_gauge_bar_height = 0.5 * tmp_hght
        if self.orientation == ICWidgetOrientation.Vertical:
            if self.position == ICWidgetPosition.Left:
                rect = QtCore.QRectF(0, 0, vert_gauge_bar_width, tmp_hght)
            else:
                rect = QtCore.QRectF(vert_gauge_bar_width, 0, vert_gauge_bar_width, tmp_hght)
            brush = QtGui.QLinearGradient(rect.topRight(), rect.topLeft())
        else:
            if self.position == ICWidgetPosition.Bottom:
                rect = QtCore.QRectF(0, horz_gauge_bar_height, tmp_wdth, horz_gauge_bar_height)
            else:
                rect = QtCore.QRectF(0, 0, tmp_wdth, horz_gauge_bar_height)
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

        # draw the gauge bar only if the current value between the min and max value
        if self._gauge_range_max >= self._gauge_val >= self._gauge_range_min:
            # define the gauge bar
            if self.orientation == ICWidgetOrientation.Vertical:
                pos = (tmp_hght - 4) * (self._gauge_val - self._gauge_range_min) / (
                        self._gauge_range_max - self._gauge_range_min)
                if self.position == ICWidgetPosition.Left:
                    rect = QtCore.QRectF(2, tmp_hght - 2 - pos, vert_gauge_bar_width - 4, pos)
                else:
                    rect = QtCore.QRectF(2 + vert_gauge_bar_width, tmp_hght - 2 - pos, vert_gauge_bar_width - 4, pos)
                brush = QtGui.QLinearGradient(rect.topLeft(), rect.bottomRight())
            else:
                pos = (tmp_wdth - 4) * (self._gauge_val - self._gauge_range_min) / (
                        self._gauge_range_max - self._gauge_range_min)
                if self.position == ICWidgetPosition.Bottom:
                    rect = QtCore.QRectF(2, horz_gauge_bar_height + 2, pos, horz_gauge_bar_height - 4)
                else:
                    rect = QtCore.QRectF(2, 2, pos, horz_gauge_bar_height - 4)
                brush = QtGui.QLinearGradient(rect.topRight(), rect.bottomLeft())

            # set the default color
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
        pen.setColor(self._min_max_color)
        pen.setWidth(4)
        painter.setPen(pen)

        # min tracking
        if self._cycle_min_tracking:
            val = self._cycle_min
            if self.orientation == ICWidgetOrientation.Vertical:
                pos = (tmp_hght - 4) * (val - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
                if self.position == ICWidgetPosition.Left:
                    painter.drawLine(QtCore.QPointF(0, tmp_hght - 2 - pos),
                                     QtCore.QPointF(vert_gauge_bar_width + 5, tmp_hght - 2 - pos))
                else:
                    painter.drawLine(QtCore.QPointF(vert_gauge_bar_width - 5, tmp_hght - 2 - pos),
                                     QtCore.QPointF(tmp_wdth, tmp_hght - 2 - pos))
            else:
                pos = (tmp_wdth - 4) * (val - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
                if self.position == ICWidgetPosition.Bottom:
                    painter.drawLine(QtCore.QPointF(pos + 2, tmp_hght),
                                     QtCore.QPointF(pos + 2, tmp_hght - horz_gauge_bar_height - 5))
                else:
                    painter.drawLine(QtCore.QPointF(pos + 2, 0),
                                     QtCore.QPointF(pos + 2, horz_gauge_bar_height + 5))

        # max tracking
        if self._cycle_max_tracking:
            val = self._cycle_max
            if self.orientation == ICWidgetOrientation.Vertical:
                pos = (tmp_hght - 4) * (val - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
                if self.position == ICWidgetPosition.Left:
                    painter.drawLine(QtCore.QPointF(0, tmp_hght - 2 - pos),
                                     QtCore.QPointF(vert_gauge_bar_width + 5, tmp_hght - 2 - pos))
                else:
                    painter.drawLine(QtCore.QPointF(vert_gauge_bar_width - 5, tmp_hght - 2 - pos),
                                     QtCore.QPointF(tmp_wdth, tmp_hght - 2 - pos))
            else:
                pos = (tmp_wdth - 4) * (val - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)
                if self.position == ICWidgetPosition.Bottom:
                    painter.drawLine(QtCore.QPointF(pos + 2, tmp_hght),
                                     QtCore.QPointF(pos + 2, tmp_hght - horz_gauge_bar_height - 5))
                else:
                    painter.drawLine(QtCore.QPointF(pos + 2, 0),
                                     QtCore.QPointF(pos + 2, horz_gauge_bar_height + 5))

        # draw the limits. setup the font and pen
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
            val = self._alarm_lower_level
            if self.orientation == ICWidgetOrientation.Vertical:
                pos = (tmp_hght - 4) * (val - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)

                # calculate where to write the text
                text_y_pos = tmp_hght - 2 - pos
                if text_y_pos < 0:
                    text_y_pos = 0
                if text_y_pos + self._alarm_text_size + 5 > tmp_hght:
                    text_y_pos = tmp_hght - self._alarm_text_size - 5

                if self.position == ICWidgetPosition.Left:
                    painter.drawLine(QtCore.QPointF(0, tmp_hght - 2 - pos),
                                     QtCore.QPointF(vert_gauge_bar_width + 5, tmp_hght - 2 - pos))
                    rect = QtCore.QRectF(vert_gauge_bar_width + 7.0, text_y_pos, vert_gauge_bar_width,
                                         self._alarm_text_size + 5)

                    # setup the pen for writing the alarm text
                    pen.setWidth(1)
                    painter.setPen(pen)
                    painter.drawText(rect, Qt.AlignLeft, self._alarm_lower_level_text)

                else:
                    painter.drawLine(QtCore.QPointF(vert_gauge_bar_width - 5, tmp_hght - 2 - pos),
                                     QtCore.QPointF(tmp_wdth, tmp_hght - 2 - pos))
                    # setup the pen for writing the alarm text
                    pen.setWidth(1)
                    painter.setPen(pen)
                    rect = QtCore.QRectF(0, text_y_pos, vert_gauge_bar_width - 7.0, self._alarm_text_size + 5)
                    painter.drawText(rect, Qt.AlignRight, self._alarm_lower_level_text)
            else:
                pos = (tmp_wdth - 4) * (val - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)

                if self.position == ICWidgetPosition.Bottom:
                    rect = QtCore.QRectF(pos, tmp_hght - horz_gauge_bar_height - (self._alarm_text_size + 7),
                                         tmp_wdth / 3, self._alarm_text_size + 5)
                    painter.drawLine(QtCore.QPointF(pos + 2, tmp_hght),
                                     QtCore.QPointF(pos + 2, tmp_hght - horz_gauge_bar_height - 5))
                else:
                    rect = QtCore.QRectF(pos, horz_gauge_bar_height + 7, tmp_wdth / 3, self._alarm_text_size + 5)
                    painter.drawLine(QtCore.QPointF(pos + 2, 0), QtCore.QPointF(pos + 2, horz_gauge_bar_height + 5))

                # setup the pen for writing the alarm text
                pen.setWidth(1)
                painter.setPen(pen)
                painter.drawText(rect, Qt.AlignLeft, self._alarm_lower_level_text)

        # draw the upper level set point
        pen.setWidth(4)
        painter.setPen(pen)
        if self._alarm_upper_level_set:
            val = self._alarm_upper_level
            if self.orientation == ICWidgetOrientation.Vertical:
                pos = (tmp_hght - 4) * (val - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)

                # calculate where to write the text
                text_y_pos = tmp_hght - 2 - pos
                if text_y_pos < 0:
                    text_y_pos = 0
                if text_y_pos + self._alarm_text_size + 5 > tmp_hght:
                    text_y_pos = tmp_hght - self._alarm_text_size - 5

                if self.position == ICWidgetPosition.Left:
                    rect = QtCore.QRectF(vert_gauge_bar_width + 7.0, text_y_pos, vert_gauge_bar_width,
                                         self._alarm_upper_level + 5)
                    painter.drawLine(QtCore.QPointF(0, tmp_hght - 2 - pos),
                                     QtCore.QPointF(vert_gauge_bar_width + 5, tmp_hght - 2 - pos))

                    # setup the pen for writing the alarm text
                    pen.setWidth(1)
                    painter.setPen(pen)
                    painter.drawText(rect, Qt.AlignLeft, self._alarm_upper_level_text)

                else:
                    rect = QtCore.QRectF(0, text_y_pos, vert_gauge_bar_width - 7, self._alarm_upper_level + 5)
                    painter.drawLine(QtCore.QPointF(vert_gauge_bar_width - 5, tmp_hght - 2 - pos),
                                     QtCore.QPointF(tmp_wdth, tmp_hght - 2 - pos))

                    # setup the pen for writing the alarm text
                    pen.setWidth(1)
                    painter.setPen(pen)
                    painter.drawText(rect, Qt.AlignRight, self._alarm_upper_level_text)

            else:
                pos = (tmp_wdth - 4) * (val - self._gauge_range_min) / (self._gauge_range_max - self._gauge_range_min)

                # position
                text_width = tmp_wdth / 3
                start_x = pos - tmp_wdth / 3
                if start_x < 0:
                    start_x = 0
                    text_width = pos

                if self.position == ICWidgetPosition.Bottom:
                    rect = QtCore.QRectF(start_x, tmp_hght - horz_gauge_bar_height - (self._alarm_text_size + 7),
                                         text_width, self._alarm_text_size + 5)
                    painter.drawLine(QtCore.QPointF(pos + 2, tmp_hght),
                                     QtCore.QPointF(pos + 2, tmp_hght - horz_gauge_bar_height - 5))
                else:
                    rect = QtCore.QRectF(start_x, horz_gauge_bar_height + 7, text_width, self._alarm_text_size + 5)
                    painter.drawLine(QtCore.QPointF(pos + 2, 0), QtCore.QPointF(pos + 2, horz_gauge_bar_height + 5))

                # setup the pen and write the alarm text
                pen.setWidth(1)
                painter.setPen(pen)
                painter.drawText(rect, Qt.AlignRight, self._alarm_upper_level_text)


class ICLinearGauge(ICBaseWidget):
    """
    Compound widget with a Gauge Bar and label for displaying the plotted value
    """
    LAYOUT_MAP = {
        ICWidgetOrientation.Vertical: {
            ICWidgetPosition.Left: {
                "title": (0, 0, 1, 3),
                "value": (4, 0, 1, 3),
                "scale": (2, 0, 1, 1),
                "gauge": (2, 1, 1, 2)
            },
            ICWidgetPosition.Right: {
                "title": (0, 0, 1, 3),
                "value": (4, 0, 1, 3),
                "scale": (2, 2, 1, 1),
                "gauge": (2, 0, 1, 2)
            }
        },
        ICWidgetOrientation.Horizontal: {
            ICWidgetPosition.Bottom: {
                "title": (4, 0, 1, 1),
                "value": (4, 1, 1, 1),
                "scale": (3, 0, 1, 3),
                "gauge": (1, 0, 2, 3)
            },
            ICWidgetPosition.Top: {
                "title": (4, 0, 1, 1),
                "value": (4, 1, 1, 1),
                "scale": (1, 0, 1, 3),
                "gauge": (2, 0, 2, 3)
            }
        }

    }

    def __init__(self, name: str, unit: str, min_val: float = 0, max_val: float = 100, display_steps: int = 5,
                 orientation: ICWidgetOrientation = ICWidgetOrientation.Vertical, widget_id: int = 0, *args, **kwargs):
        super(ICLinearGauge, self).__init__(widget_id, *args, **kwargs)

        # create the local variables
        self._gauge_name = name
        self._gauge_value = 0.5 * (min_val + max_val)
        self._gauge_unit = unit

        # create the gauge Bar
        self.gauge_bar = ICGaugeBar(min_val, max_val, self._gauge_value, widget_id, orientation)
        self.gauge_bar.changed.connect(self.value_changed)

        # number of steps for drawing ticks in the gauge bar
        self._display_steps: int = display_steps

        # format for the axis label
        self._axis_label_format = "{0:.0f}"

        # selected values and displayed values for the scale
        self._scale_values: list[float] = []
        self._scale_displayed_values: list[str] = []

        # create the display lists
        self._create_display_lists()

        # create the scale bar
        if orientation == ICWidgetOrientation.Horizontal:
            scale_width = ICDisplayConfig.LinearGaugeHorizontalWidth
            scale_height = ICDisplayConfig.LinearGaugeHorizontalHeight / 3
            self._scale_position: ICWidgetPosition = ICWidgetPosition.Bottom
        else:
            scale_width = ICDisplayConfig.LinearGaugeVerticalWidth / 3
            scale_height = ICDisplayConfig.LinearGaugeVerticalHeight
            self._scale_position: ICWidgetPosition = ICWidgetPosition.Left

        # create the scale bar
        self.scale_bar: ICLinearAxis = ICLinearAxis(self._scale_values, self._scale_displayed_values,
                                                    scale_width, scale_height, orientation, widget_id)

        # set the position for the scale bar
        self.scale_bar.position = self._scale_position

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

        # last alarm status
        self._alarmed = False

        # create the grid layout
        self._layout: QtWidgets.QGridLayout = QtWidgets.QGridLayout()

        # add title of the linear Gauge
        self._title_display = QtWidgets.QLabel("", self)
        self._title_display.setStyleSheet("QLabel { background-color : " +
                                          ICDisplayConfig.QtColorToSting(self.background_color) + "; color : " +
                                          ICDisplayConfig.QtColorToSting(self._title_color) + ";}")

        # display value below the gauge
        self._value_display = QtWidgets.QLabel("", self)
        self._value_display.setStyleSheet("QLabel { background-color : " +
                                          ICDisplayConfig.QtColorToSting(self.background_color) +
                                          "; color : " +
                                          ICDisplayConfig.QtColorToSting(self._value_color) +
                                          "; border-radius : 5px; }")

        # set the layout
        self.setLayout(self._layout)

        # fixed gauge width
        self._gauge_width_limit: int = ICDisplayConfig.LinearGaugeVerticalWidth
        self._gauge_height_limit: int = ICDisplayConfig.LinearGaugeHorizontalHeight

        # set the parameters for the base class
        self.focusable = False
        self.clickable = False

        # set the orientation
        self.orientation = orientation

        # set default size hint
        self._change_size_hints(self.orientation)

        # setup the layout
        self._setup_display(self.orientation, self.scale_position)

        # override the base Size policy
        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

        # update the display
        self._local_update()

    ########################################################
    # properties
    ########################################################
    # get the gauge title
    @property
    def name(self) -> str:
        return self._gauge_name

    # set the gauge title
    @name.setter
    def name(self, nm: str) -> None:
        self._gauge_name = nm
        self._title_update()

    # get current value of the gauge
    @property
    def value(self) -> float:
        return self._gauge_value

    # set the current value of the gauge
    @value.setter
    def value(self, val: float) -> None:
        # first set the value for the gauge where limit check takes place
        if self.gauge_bar.gauge_value != val:
            self.gauge_bar.gauge_value = val
        # local value should be the gauge bar value
        self._gauge_value = self.gauge_bar.gauge_value
        self._value_update()

    # get the current unit
    @property
    def unit(self) -> str:
        return self._gauge_unit

    # set the gauge unit
    @unit.setter
    def unit(self, un: str) -> None:
        self._gauge_unit = un
        self._local_update()

    # scale bar position
    @property
    def scale_position(self) -> ICWidgetPosition:
        return self._scale_position

    @scale_position.setter
    def scale_position(self, pos: ICWidgetPosition) -> None:
        # if same as the previous position then nothing to do
        if self._scale_position == pos:
            return

        # check validity as per orientation and set position
        if self.orientation == ICWidgetOrientation.Vertical:
            if pos in (ICWidgetPosition.Left, ICWidgetPosition.Right):
                self._scale_position = pos
                self.scale_bar.position = pos
                self.gauge_bar.position = pos
                self._setup_display(self.orientation, self.scale_position)
        else:
            if pos in (ICWidgetPosition.Top, ICWidgetPosition.Bottom):
                self._scale_position = pos
                self.scale_bar.position = pos
                self.gauge_bar.position = pos
                self._setup_display(self.orientation, self.scale_position)

    # get the number of steps for drawing the ticks
    @property
    def num_steps(self) -> int:
        return self._display_steps

    # set the number of steps for drawing the ticks
    @num_steps.setter
    def num_steps(self, stp: int) -> None:
        if stp >= 2:
            self._display_steps = stp
            self.update()

    @property
    def scale_values(self) -> list[float]:
        return self._scale_values

    @property
    def scale_displayed_values(self) -> list[str]:
        return self._scale_displayed_values

    # axis label format
    @property
    def axis_label_format(self) -> str:
        return self._axis_label_format

    @axis_label_format.setter
    def axis_label_format(self, fmt: str) -> None:
        self._axis_label_format = fmt
        self.update()

    # get the color of the title
    @property
    def title_text_color(self) -> QtGui.QColor:
        return self._title_color

    # set the title color
    @title_text_color.setter
    def title_text_color(self, clr: QtGui.QColor) -> None:
        self._title_color = clr
        self._title_update()

    # get the color of the title
    @property
    def value_text_color(self) -> QtGui.QColor:
        return self._value_color

    # set the title color
    @value_text_color.setter
    def value_text_color(self, clr: QtGui.QColor) -> None:
        self._value_color = clr
        self._value_update()

    # get the color of alarm text
    @property
    def alarm_colors(self) -> [QtGui.QColor, QtGui.QColor]:
        return self._error_back_color, self._error_text_color

    # set the color of alarm text
    @alarm_colors.setter
    def alarm_colors(self, clrs: [QtGui.QColor, QtGui.QColor]) -> None:
        self._error_back_color = clrs[0]
        self._error_text_color = clrs[1]
        self._value_update()

    # get the maximum width of the vertical gauge
    @property
    def vertical_gauge_width(self) -> int:
        return self._gauge_width_limit

    # set the maximum width of the vertical gauge
    @vertical_gauge_width.setter
    def vertical_gauge_width(self, wd: int) -> None:
        self._gauge_width_limit = wd
        self.on_orientation_changed()
        self._local_update()

    # get the maximum height of the horizontal gauge
    @property
    def horizontal_gauge_height(self) -> int:
        return self._gauge_height_limit

    # set the maximum height of the horizontal gauge
    @horizontal_gauge_height.setter
    def horizontal_gauge_height(self, ht: int) -> None:
        self._gauge_height_limit = ht
        self.on_orientation_changed()
        self._local_update()

    # get the size of the title text
    @property
    def title_size(self) -> int:
        return self._title_size

    # set the size of the title text
    @title_size.setter
    def title_size(self, sz: int) -> None:
        self._title_size = sz
        self._title_update()

    # get the size of the value text
    @property
    def value_size(self) -> int:
        return self._value_size

    # set the size of the title text
    @value_size.setter
    def value_size(self, sz: int) -> None:
        self._value_size = sz
        self._value_update()

    # get the size of the title text
    @property
    def unit_size(self) -> int:
        return self._unit_size

    # set the size of the title text
    @unit_size.setter
    def unit_size(self, sz: int) -> None:
        self._unit_size = sz
        self._local_update()

    ########################################################
    # functions
    ########################################################
    # change size hints
    def _change_size_hints(self, orientation: ICWidgetOrientation) -> None:
        if orientation == ICWidgetOrientation.Horizontal:
            self.gauge_bar.size_hint = (ICDisplayConfig.LinearGaugeHorizontalWidth,
                                        2 * ICDisplayConfig.LinearGaugeHorizontalHeight / 3)
            self.scale_bar.size_hint = (ICDisplayConfig.LinearGaugeHorizontalWidth,
                                        ICDisplayConfig.LinearGaugeHorizontalHeight / 3)
            self.size_hint = (ICDisplayConfig.LinearGaugeHorizontalWidth,
                              ICDisplayConfig.LinearGaugeHorizontalHeight)
        else:
            self.gauge_bar.size_hint = (2 * ICDisplayConfig.LinearGaugeVerticalWidth / 3,
                                        ICDisplayConfig.LinearGaugeVerticalHeight)
            self.scale_bar.size_hint = (ICDisplayConfig.LinearGaugeVerticalWidth / 3,
                                        ICDisplayConfig.LinearGaugeVerticalHeight)
            self.size_hint = (ICDisplayConfig.LinearGaugeVerticalWidth,
                              ICDisplayConfig.LinearGaugeVerticalHeight)

    # setup display
    def _setup_display(self, orientation: ICWidgetOrientation, position: ICWidgetPosition) -> None:
        # get the layout map
        o_mp = self.LAYOUT_MAP[orientation]
        p_mp = o_mp[position]

        # place the title
        index = self._layout.indexOf(self._title_display)
        if index >= 0:
            _ = self._layout.takeAt(index)
        x = p_mp["title"]
        self._layout.addWidget(self._title_display, x[0], x[1], x[2], x[3])

        # place the value
        index = self._layout.indexOf(self._value_display)
        if index >= 0:
            _ = self._layout.takeAt(index)
        x = p_mp["value"]
        self._layout.addWidget(self._value_display, x[0], x[1], x[2], x[3])

        # place the scale
        index = self._layout.indexOf(self.scale_bar)
        if index >= 0:
            _ = self._layout.takeAt(index)
        x = p_mp["scale"]
        self._layout.addWidget(self.scale_bar, x[0], x[1], x[2], x[3])

        # place the gauge
        index = self._layout.indexOf(self.gauge_bar)
        if index >= 0:
            _ = self._layout.takeAt(index)
        x = p_mp["gauge"]
        self._layout.addWidget(self.gauge_bar, x[0], x[1], x[2], x[3])

    # create the value and displayed value lists
    def _create_display_lists(self) -> None:
        max_value = self.gauge_bar.gauge_range_max
        min_value = self.gauge_bar.gauge_range_min

        # if required allocate memory
        if len(self._scale_values) != (self._display_steps + 1):
            self._scale_values = (self._display_steps + 1) * [0.0]
            self._scale_displayed_values = (self._display_steps + 1) * [""]

        # fix the variables
        self._scale_values[0] = min_value
        self._scale_displayed_values[0] = self._axis_label_format.format(min_value)

        # loop
        index = 1
        step_value = (max_value - min_value) / self._display_steps
        while index < self._display_steps:
            self._scale_values[index] = self._scale_values[index - 1] + step_value
            self._scale_displayed_values[index] = self._axis_label_format.format(self._scale_values[index])
            index += 1

        self._scale_values[self._display_steps] = max_value
        self._scale_displayed_values[self._display_steps] = self._axis_label_format.format(max_value)

    # update title
    def _title_update(self) -> None:
        # nothing to do if hidden
        if self.state == ICWidgetState.Hidden:
            return

        # update the text based on the state
        self._title_display.setStyleSheet("QLabel { background-color : " +
                                          ICDisplayConfig.QtColorToSting(self.background_color) + "; color : " +
                                          ICDisplayConfig.QtColorToSting(self._title_color) + ";}")
        self._title_display.setAlignment(Qt.AlignCenter)
        if self.state in (ICWidgetState.Transparent, ICWidgetState.FrameOnly):
            self._title_display.setText("<span style='font-size:" + "{}".format(self._title_size) + "pt;'>" +
                                        "</span> <span style='font-size:" + "{}".format(self._unit_size) +
                                        "pt;'></span>")
        else:
            self._title_display.setText("<span style='font-size:" + "{}".format(self._title_size) + "pt;'>" +
                                        self._gauge_name + "</span> <span style='font-size:" +
                                        "{}".format(self._unit_size) + "pt;'>(" + self._gauge_unit + ")</span>")
        # update the title
        self._title_display.update()

    # update value
    def _value_update(self):
        # nothing to do if hidden
        if self.state == ICWidgetState.Hidden:
            return

        # update the value based on widget visibility state
        self._value_display.setAlignment(Qt.AlignCenter)
        if self.state in (ICWidgetState.Transparent, ICWidgetState.FrameOnly):
            # set background color and do not draw
            self._value_display.setStyleSheet("QLabel { background-color : " +
                                              ICDisplayConfig.QtColorToSting(self.background_color) +
                                              "; color : " +
                                              ICDisplayConfig.QtColorToSting(self._value_color) +
                                              "; border-radius : 5px; }")
            self._value_display.setText("<span style='font-size:" + "{}".format(self._value_size) + "pt;'>" +
                                        "</span> <span style='font-size:" + "{}".format(
                self._unit_size) + "pt;'></span>")
        else:
            # select format based on  alarm state
            if self.gauge_bar.alarm_activated != self._alarmed:
                self._alarmed = self.gauge_bar.alarm_activated
                if self.gauge_bar.alarm_activated:
                    self._value_display.setStyleSheet("QLabel { background-color : " +
                                                      ICDisplayConfig.QtColorToSting(self._error_back_color) +
                                                      "; color : " +
                                                      ICDisplayConfig.QtColorToSting(self._error_text_color) +
                                                      "; border-radius : 5px; }")
                else:
                    self._value_display.setStyleSheet("QLabel { background-color : " +
                                                      ICDisplayConfig.QtColorToSting(self.background_color) +
                                                      "; color : " +
                                                      ICDisplayConfig.QtColorToSting(self._value_color) +
                                                      "; border-radius : 5px; }")
            # update the value text
            self._value_display.setText("<span style='font-size:" + "{}".format(self._value_size) + "pt;'>" +
                                        "{:.2f}".format(self._gauge_value) + "</span> <span style='font-size:" +
                                        "{}".format(self._unit_size) + "pt;'>" + self._gauge_unit + "</span>")
        # update the label
        self._value_display.update()

    # update the widget
    def _local_update(self):
        # update the title text
        self._title_update()
        # update the value text
        self._value_update()
        # update the gauge bar
        self.gauge_bar.update()
        # update the scale bar
        self.scale_bar.update()
        # update self
        self.update()

    ########################################################
    # slots
    ########################################################
    # handles the signal for value update
    @pyqtSlot(float)
    def update_upper_alarm_level(self, new_level: float) -> None:
        nm, old_level = self.gauge_bar.upper_alarm
        self.gauge_bar.upper_alarm = (nm, new_level)

    @pyqtSlot(float)
    def update_lower_alarm_level(self, new_level: float) -> None:
        nm, old_level = self.gauge_bar.lower_alarm
        self.gauge_bar.lower_alarm = (nm, new_level)

    # handles the signal for value update
    @pyqtSlot(float)
    def value_changed(self, val: float) -> None:
        self.value = val

    ########################################################
    # base class event overrides
    ########################################################
    # change layout based on the orientation
    def on_orientation_changed(self) -> None:
        self.gauge_bar.orientation = self.orientation
        self.scale_bar.orientation = self.orientation

        # set the size based on the orientation
        if self.orientation == ICWidgetOrientation.Horizontal:
            self.setMaximumSize(10000, self._gauge_height_limit)
        else:
            self.setMaximumSize(self._gauge_width_limit, 10000)

        # copy position from the scale bar
        self._scale_position = self.scale_bar.position
        self._setup_display(self.orientation, self.scale_position)
        self._local_update()

    # change the visibility of elements
    def on_state_changed(self) -> None:
        if self.state == ICWidgetState.Hidden:
            # hide the title label
            self._title_display.hide()
            self._title_display.setMaximumSize(0, 0)
            # hide the value label
            self._value_display.hide()
            self._value_display.setMaximumSize(0, 0)
            # hide the gauge bar
            self.gauge_bar.state = ICWidgetState.Hidden
            self.gauge_bar.update()
            # hide the scale bae
            self.scale_bar.state = ICWidgetState.Hidden
            self.scale_bar.update()
            # hide self
            self.hide()
            self.update()
        else:
            # all other states are managed in the display update routines
            # show self
            self.show()
            # show the value display
            self._value_display.show()
            self._value_display.setMaximumSize(10000, 10000)
            # show the title display
            self._title_display.show()
            self._title_display.setMaximumSize(10000, 10000)
            if self.orientation == ICWidgetOrientation.Vertical:
                self.setMaximumSize(self._gauge_width_limit, 10000)
            else:
                self.setMaximumSize(10000, self._gauge_height_limit)
            # set the gauge bar state
            self.gauge_bar.state = self.state
            # set the scale bar state
            self.scale_bar.state = self.state
            # update the screen
            self._local_update()
