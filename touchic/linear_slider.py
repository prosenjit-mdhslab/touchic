# -*- coding: utf-8 -*-
"""
Created on May  20 2021

@author: Prosenjit

A linear slider to graphically enter data
TODO: Popup dialog
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from typing import Union
from math import sqrt
from .display_config import ICDisplayConfig
from .base_widget import ICBaseWidget, ICWidgetState, ICWidgetPosition
from .linear_axis import ICLinearAxis, ICLinearAxisContainer, ICLinearContainerType
from .config_button import ICConfigDialogTemplate


class ICSlider(ICBaseWidget):
    """
    A linear slider class to enter a data point using GUI
    """

    # emits the value changed
    changed = pyqtSignal(float)
    
    def __init__(self, values: list[float], current_value: float, position: ICWidgetPosition = ICWidgetPosition.Bottom, widget_id: int = 0, *args, **kwargs):
        super(ICSlider, self).__init__(widget_id, *args, **kwargs)

        # setup the variables
        # list of valid values from which the user can select
        self._internal_values: list[float] = values

        # set up the current selected value
        if current_value in values:
            self._selected_value: float = current_value
            self._selected_index: int = values.index(current_value)
        else:
            self._selected_value: float = values[0]
            self._selected_index: int = 0

        # local variable for sliding variable
        self._sliding: bool = False
        self._slided: bool = False
        self._knob_loc = None

        # has the current value lead to an alarm
        self.alarm_activated = False

        # upper alarm level for the gauge
        self._alarm_upper_level: float = values[0]
        self._alarm_upper_level_set: bool = False

        # lower alarm level for the gauge
        self._alarm_lower_level: float = values[-1]
        self._alarm_lower_level_set: bool = False

        # color for the slide background
        self._slide_color_light: QtGui.QColor = ICDisplayConfig.LinearSlideBoxColorLight
        self._slide_color_dark: QtGui.QColor = ICDisplayConfig.LinearSlideBoxColorDark

        # color for the slide groove
        self._groove_color_light: QtGui.QColor = ICDisplayConfig.LinearSlideColorLight
        self._groove_color_dark: QtGui.QColor = ICDisplayConfig.LinearSlideColorDark

        # color for the scale
        self._scale_color_light: QtGui.QColor = ICDisplayConfig.LinearSlideRulerColorLight
        self._scale_color_dark: QtGui.QColor = ICDisplayConfig.LinearSlideRulerColorDark

        # scale colors alarmed
        self._scale_color_alarm_light: QtGui.QColor = ICDisplayConfig.LinearSlideRulerAlarmColorLight
        self._scale_color_alarm_dark: QtGui.QColor = ICDisplayConfig.LinearSlideRulerAlarmColorDark

        # color of the knob
        self._knob_color_light: QtGui.QColor = ICDisplayConfig.LinearSlideKnobLight
        self._knob_color_dark: QtGui.QColor = ICDisplayConfig.LinearSlideKnobDark

        # click-ability and focus-ability
        self.focusable = False
        self.clickable = True

        # set the orientation of the widget
        self.position = position

        # display configuration
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)

    ########################################################
    # properties
    ########################################################
    # read only value list
    @property
    def values(self) -> list[float]:
        return self._internal_values

    # current value
    @property
    def current_value(self) -> float:
        return self._selected_value

    # set the new current value
    # finds the nearest valid entry from the set list
    @current_value.setter
    def current_value(self, new_val: float) -> None:
        if self._selected_value == new_val:
            return
        # the set value should be between min and max
        if self._internal_values[0] <= new_val <= self._internal_values[-1]:

            # find a valid value closest to the new value
            gap = [abs(x - new_val) for x in self._internal_values]
            self._selected_index = gap.index(min(gap))
            self._selected_value = self._internal_values[self._selected_index]

            self.alarm_activated = False
            # check for alarm levels
            if self._alarm_lower_level_set:
                if self._selected_value < self._alarm_lower_level:
                    self.alarm_activated = True

            if self._alarm_upper_level_set:
                if self._selected_value > self._alarm_upper_level:
                    self.alarm_activated = True

            # notify listeners about the change
            self.changed.emit(self._selected_value)
            self.append_history("set", self._selected_value)
            self.update()

    # slider color
    @property
    def slider_colors(self) -> tuple[QtGui.QColor, QtGui.QColor]:
        return self._slide_color_light, self._slide_color_dark

    @slider_colors.setter
    def slider_colors(self, clrs: tuple[QtGui.QColor, QtGui.QColor]) -> None:
        self._slide_color_light = clrs[0]
        self._slide_color_dark = clrs[1]
        self.update()

    # groove colors
    @property
    def groove_colors(self) -> tuple[QtGui.QColor, QtGui.QColor]:
        return self._groove_color_light, self._groove_color_dark

    @groove_colors.setter
    def groove_colors(self, clrs: tuple[QtGui.QColor, QtGui.QColor]) -> None:
        self._groove_color_light = clrs[0]
        self._groove_color_dark = clrs[1]
        self.update()

    # scale colors
    @property
    def scale_colors(self) -> tuple[QtGui.QColor, QtGui.QColor]:
        return self._scale_color_light, self._scale_color_dark

    @scale_colors.setter
    def scale_colors(self, clrs: tuple[QtGui.QColor, QtGui.QColor]) -> None:
        self._scale_color_light = clrs[0]
        self._scale_color_dark = clrs[1]
        self.update()

    # alarm colors
    @property
    def scale_alarm_colors(self) -> tuple[QtGui.QColor, QtGui.QColor]:
        return self._scale_color_alarm_light, self._scale_color_alarm_dark

    @scale_alarm_colors.setter
    def scale_alarm_colors(self, clrs: tuple[QtGui.QColor, QtGui.QColor]) -> None:
        self._scale_color_alarm_light = clrs[0]
        self._scale_color_alarm_dark = clrs[1]
        self.update()

    # knob colors
    @property
    def knob_colors(self) -> tuple[QtGui.QColor, QtGui.QColor]:
        return self._knob_color_light, self._knob_color_dark

    @knob_colors.setter
    def knob_colors(self, clrs: tuple[QtGui.QColor, QtGui.QColor]) -> None:
        self._knob_color_light = clrs[0]
        self._knob_color_dark = clrs[1]
        self.update()

        # get the upper level alarm
        # tuple of (name, value)

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
        if self._internal_values[0] <= alarm <= self._internal_values[-1]:
            self._alarm_upper_level_set = True
            self._alarm_upper_level = alarm

            # check for alarm level
            if self._selected_value > self._alarm_upper_level:
                self.alarm_activated = True
                self.changed.emit(self._selected_value)
            self.update()

    # get the lower level alarm
    # tuple of (name, value)
    @property
    def lower_alarm(self) -> Union[float, None]:
        if self._alarm_lower_level_set:
            return self._alarm_lower_level
        else:
            return None

    # set the upper level alarm
    @lower_alarm.setter
    def lower_alarm(self, alarm: float) -> None:
        # check if lower alarm level is less the upper alarm level
        if self._alarm_upper_level_set:
            if alarm > self._alarm_upper_level:
                return

        # check if the limit value is in between the max and min values
        if self._internal_values[0] <= alarm <= self._internal_values[-1]:
            self._alarm_lower_level_set = True
            self._alarm_lower_level = alarm

            # check if alarm is active
            if self._selected_value < self._alarm_lower_level:
                self.alarm_activated = True
                self.changed.emit(self._selected_value)
            self.update()

    ########################################################
    # functions
    ########################################################

    ########################################################
    # base class event overrides
    ########################################################
    # mouse pressed event
    def on_mouse_pressed(self, event: QtGui.QMouseEvent) -> None:
        # mouse pressed event
        if event.button() & Qt.LeftButton:
            dist = event.pos() - self._knob_loc
            len_square = QtCore.QPointF.dotProduct(dist, dist)
            if len_square < 225:
                self._sliding = True

    # mouse moved event
    def on_mouse_moved(self, event: QtGui.QMouseEvent) -> None:
        if self._sliding:
            tmp_width = self.width()
            tmp_height = self.height()
            min_slide = 20
            max_slide = (tmp_width - 20) if self.position.is_horizontal() else (tmp_height - 20)
            new_pos = event.pos().x() if self.position.is_horizontal() else max_slide - event.pos().y()
            # if the new position is between the slide geometry
            if min_slide <= new_pos <= max_slide:
                new_val = self._internal_values[0] + (new_pos - min_slide) * (self._internal_values[-1] - self._internal_values[0]) / (max_slide - min_slide)

                # find the closest value in the valid values list
                gap = [abs(x - new_val) for x in self._internal_values]
                self._selected_index = gap.index(min(gap))
                self._selected_value = self._internal_values[self._selected_index]

                self.alarm_activated = False
                # check for alarm levels
                if self._alarm_lower_level_set:
                    if self._selected_value < self._alarm_lower_level:
                        self.alarm_activated = True

                if self._alarm_upper_level_set:
                    if self._selected_value > self._alarm_upper_level:
                        self.alarm_activated = True

                # notify listeners about the change
                self.changed.emit(self._selected_value)
                self.update()
                self._slided = True

    # mouse released event
    def on_mouse_released(self, event: QtGui.QMouseEvent) -> None:
        if event.button() & Qt.LeftButton:
            if self._sliding:
                self._sliding = False
                # check if sliding took place. append the new value to history
                if self._slided:
                    self.append_history("user", self._selected_value)
                    self._slided = False
            else:
                # handle click event
                new_pos = event.pos().x() if self.position.is_horizontal() else -event.pos().y()
                knob_pos = self._knob_loc.x() if self.position.is_horizontal() else -self._knob_loc.y()
                list_len = len(self._internal_values)
                if new_pos > knob_pos:
                    # increment by one pos
                    next_index = self._selected_index + 1
                    if next_index < list_len:
                        self._selected_value = self._internal_values[next_index]
                        self._selected_index = next_index

                        self.alarm_activated = False
                        # check for alarm levels
                        if self._alarm_lower_level_set:
                            if self._selected_value < self._alarm_lower_level:
                                self.alarm_activated = True

                        if self._alarm_upper_level_set:
                            if self._selected_value > self._alarm_upper_level:
                                self.alarm_activated = True

                        self.update()
                        self.changed.emit(self._selected_value)
                        self.append_history("", self._selected_value)
                else:
                    # reduce by one pos
                    next_index = self._selected_index - 1
                    if next_index >= 0:
                        self._selected_value = self._internal_values[next_index]
                        self._selected_index = next_index

                        self.alarm_activated = False
                        # check for alarm levels
                        if self._alarm_lower_level_set:
                            if self._selected_value < self._alarm_lower_level:
                                self.alarm_activated = True

                        if self._alarm_upper_level_set:
                            if self._selected_value > self._alarm_upper_level:
                                self.alarm_activated = True

                        self.update()
                        self.changed.emit(self._selected_value)
                        self.append_history("", self._selected_value)

    ########################################################
    # overrides and event handlers
    ########################################################
    # paint the linear slide
    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.redraw(painter)

    # draw the widget
    def redraw(self, painter) -> None:
        # nothing to draw if the widget is hidden
        if self.state == ICWidgetState.Hidden:
            return

        # get window dimension
        temp_width = painter.device().width()
        temp_height = painter.device().height()

        # current position
        curr_val = self._selected_value
        pos = (curr_val - self._internal_values[0]) / (self._internal_values[-1] - self._internal_values[0])

        volume_p_one = QtCore.QPointF(0, 0)
        volume_p_two = QtCore.QPointF(0, 0)
        volume_p_three = QtCore.QPointF(0, 0)
        volume_p_four = QtCore.QPointF(0, 0)

        #######################################
        # calculate dimensions
        #######################################
        if self.position.is_horizontal():
            # slider back ground dimensions
            slider_size_x = temp_width
            slider_size_y = temp_height / 2
            slider_start_x = 0

            # groove dimensions
            groove_start_x = 0.35 * slider_size_y
            groove_size_x = temp_width - 2 * groove_start_x
            groove_size_y = 0.3 * slider_size_y

            # scale dimensions
            scale_start_x = groove_start_x + 1
            scale_size_x = pos * (groove_size_x - 2)
            scale_size_y = groove_size_y - 2

            # knob dimensions
            knob_size_x = 0.6 * slider_size_y
            knob_size_y = 0.5 * slider_size_y
            knob_start_x = scale_start_x + scale_size_x - knob_size_x / 2

            # volume dimensions
            volume_p_one.setX(scale_start_x)
            volume_p_two.setX(volume_p_one.x())
            volume_p_three.setX(scale_start_x + scale_size_x)
            volume_p_four.setX(volume_p_three.x())
            volume_min_height = 0.1 * slider_size_y

            # top and bottom specific numbers
            if self.position == ICWidgetPosition.Top:
                slider_start_y = slider_size_y
                groove_start_y = (3 * slider_size_y - groove_size_y) / 2
                knob_start_y = (3 * slider_size_y - knob_size_y) / 2

                volume_p_one.setY(slider_start_y - 0.2 * slider_size_y)
                volume_p_two.setY(volume_p_one.y() - volume_min_height)
                volume_p_three.setY(volume_p_two.y() - 0.6 * slider_size_y * pos)
                volume_p_four.setY(volume_p_one.y())
                max_volume_pos = volume_p_two.y() - 0.6 * slider_size_y

            else:
                slider_start_y = 0
                groove_start_y = (slider_size_y - groove_size_y) / 2
                knob_start_y = (slider_size_y - knob_size_y) / 2

                volume_p_one.setY(slider_size_y + 0.2 * slider_size_y)
                volume_p_two.setY(volume_p_one.y() + volume_min_height)
                volume_p_three.setY(volume_p_two.y() + 0.6 * slider_size_y * pos)
                volume_p_four.setY(volume_p_one.y())
                max_volume_pos = volume_p_two.y() + 0.6 * slider_size_y

            scale_start_y = groove_start_y + 1
        else:
            # slider back ground dimensions
            slider_size_x = temp_width / 2
            slider_size_y = temp_height
            slider_start_y = 0

            # groove dimensions
            groove_start_y = 0.35 * slider_size_x
            groove_size_y = temp_height - 2 * groove_start_y
            groove_size_x = 0.3 * slider_size_x

            # scale dimensions
            scale_size_y = pos * (groove_size_y - 2)
            scale_start_y = (groove_start_y + groove_size_y - 1) - scale_size_y
            scale_size_x = groove_size_x - 2

            # knob dimensions
            knob_size_x = 0.5 * slider_size_x
            knob_size_y = 0.6 * slider_size_x
            knob_start_y = scale_start_y - knob_size_y / 2

            # volume dimensions
            volume_p_one.setY(scale_start_y + scale_size_y)
            volume_p_two.setY(volume_p_one.y())
            volume_p_three.setY(scale_start_y)
            volume_p_four.setY(volume_p_three.y())
            volume_min_height = 0.1 * slider_size_x

            # left and right specific numbers
            if self.position == ICWidgetPosition.Left:
                slider_start_x = slider_size_x
                groove_start_x = (3 * slider_size_x - groove_size_x) / 2
                knob_start_x = (3 * slider_size_x - knob_size_x) / 2

                volume_p_one.setX(slider_start_x - 0.2 * slider_size_x)
                volume_p_two.setX(volume_p_one.x() - volume_min_height)
                volume_p_three.setX(volume_p_two.x() - 0.6 * slider_size_x * pos)
                volume_p_four.setX(volume_p_one.x())
                max_volume_pos = volume_p_two.x() - 0.6 * slider_size_x
            else:
                slider_start_x = 0
                groove_start_x = (slider_size_x - groove_size_x) / 2
                knob_start_x = (slider_size_x - knob_size_x) / 2

                volume_p_one.setX(slider_size_x + 0.2 * slider_size_x)
                volume_p_two.setX(volume_p_one.x() + volume_min_height)
                volume_p_three.setX(volume_p_two.x() + 0.6 * slider_size_x * pos)
                volume_p_four.setX(volume_p_one.x())
                max_volume_pos = volume_p_two.x() + 0.6 * slider_size_x

            scale_start_x = groove_start_x + 1

        # set the knob location
        self._knob_loc = QtCore.QPointF(knob_start_x + knob_size_x / 2, knob_start_y + knob_size_y / 2)

        #########################################################
        # draw the slide background
        #########################################################
        rect = QtCore.QRectF(slider_start_x, slider_start_y, slider_size_x, slider_size_y)

        # set the brush
        brush = QtGui.QLinearGradient(rect.topLeft(), rect.bottomRight())
        brush.setColorAt(0, self._slide_color_light)
        brush.setColorAt(1, self._slide_color_dark)
        painter.setBrush(brush)

        # set the pen
        pen = QtGui.QPen()
        pen.setWidth(1)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setBrush(brush)
        painter.setPen(pen)

        # draw the path
        path = QtGui.QPainterPath()
        path.setFillRule(Qt.WindingFill)
        path.addRoundedRect(rect, 10, 10)
        painter.drawPath(path)

        #########################################################
        # draw the groove
        #########################################################
        rect = QtCore.QRectF(groove_start_x, groove_start_y, groove_size_x, groove_size_y)

        if self.position.is_horizontal():
            brush = QtGui.QLinearGradient(rect.topLeft(), rect.bottomLeft())
        else:
            brush = QtGui.QLinearGradient(rect.topLeft(), rect.topRight())

        # set the brush
        brush.setColorAt(0, self._groove_color_dark)
        brush.setColorAt(1, self._groove_color_light)
        painter.setBrush(brush)

        # set the pen
        pen.setBrush(brush)
        painter.setPen(pen)

        # draw the groove
        path = QtGui.QPainterPath()
        path.setFillRule(Qt.WindingFill)
        path.addRoundedRect(rect, 5, 5)
        painter.drawPath(path)

        #########################################################
        # draw the scale
        #########################################################
        rect = QtCore.QRectF(scale_start_x, scale_start_y, scale_size_x, scale_size_y)

        if self.position.is_horizontal():
            brush = QtGui.QLinearGradient(QtCore.QPointF(groove_start_x, groove_start_y),
                                          QtCore.QPointF(groove_start_x + groove_size_x, groove_start_y))
        else:
            brush = QtGui.QLinearGradient(QtCore.QPointF(groove_start_x, groove_start_y + groove_size_y),
                                          QtCore.QPointF(groove_start_x, groove_start_y))

        # set the brush
        if self.alarm_activated:
            brush.setColorAt(0, self._scale_color_alarm_dark)
            brush.setColorAt(1, self._scale_color_alarm_light)
        else:
            brush.setColorAt(0, self._scale_color_dark)
            brush.setColorAt(1, self._scale_color_light)
        painter.setBrush(brush)

        # set the brush
        pen.setBrush(brush)
        painter.setPen(pen)

        # draw the scale
        path = QtGui.QPainterPath()
        path.setFillRule(Qt.WindingFill)
        path.addRoundedRect(rect, 5, 5)
        painter.drawPath(path)

        #########################################################
        # draw the knob
        #########################################################
        rect = QtCore.QRectF(knob_start_x, knob_start_y, knob_size_x, knob_size_y)

        # set the brush for the knob
        brush = QtGui.QLinearGradient(rect.topLeft(), rect.bottomLeft())
        brush.setColorAt(0, self._knob_color_light)
        brush.setColorAt(1, self._knob_color_dark)
        painter.setBrush(brush)

        # set the pen
        pen = QtGui.QPen(QtGui.QColor(66, 66, 66))
        pen.setWidth(2)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)

        # draw the knob
        path = QtGui.QPainterPath()
        path.setFillRule(Qt.WindingFill)
        path.addRoundedRect(rect, 7, 7)
        painter.drawPath(path)

        #########################################################
        # draw the volume
        #########################################################
        # draw the volume polygon
        poly = QtGui.QPolygonF()
        poly.append(volume_p_one)
        poly.append(volume_p_two)
        poly.append(volume_p_three)
        poly.append(volume_p_four)
        poly.append(volume_p_one)

        if self.position.is_horizontal():
            brush = QtGui.QLinearGradient(QtCore.QPointF(volume_p_one.x() + (groove_size_x - 2), max_volume_pos),
                                          QtCore.QPointF(volume_p_one.x(), volume_p_one.y()))
        else:
            brush = QtGui.QLinearGradient(QtCore.QPointF(max_volume_pos, volume_p_one.y() - (groove_size_y - 2)),
                                          QtCore.QPointF(volume_p_one.x(), volume_p_one.y()))

        # set the brush
        if self.alarm_activated:
            brush.setColorAt(1, self._scale_color_alarm_dark)
            brush.setColorAt(0, self._scale_color_alarm_light)
        else:
            brush.setColorAt(1, self._scale_color_dark)
            brush.setColorAt(0, self._scale_color_light)
        painter.setBrush(brush)

        # set the pen
        pen.setWidth(5)
        pen.setBrush(brush)
        painter.setPen(pen)

        # draw the polygon path
        path = QtGui.QPainterPath()
        path.setFillRule(Qt.WindingFill)
        path.addPolygon(poly)
        painter.drawPath(path)


class ICLinearSlide(ICLinearAxisContainer):
    """
    Compound widget with a slider and label for displaying the plotted value
    """
    def __init__(self, name: str, unit: str, values: list[float], current_value: float, displayed_values: list[str] = None, display_steps: int = 5,
                 show_title: bool = True, show_value: bool = True, position: ICWidgetPosition = ICWidgetPosition.Top, widget_id: int = 0, *args, **kwargs):

        if (not show_value) and (not show_value):
            cont_type = ICLinearContainerType.BAR_NO_TITLE_NO_VALUE
        elif not show_value:
            cont_type = ICLinearContainerType.BAR_NO_VALUE
        elif not show_title:
            cont_type = ICLinearContainerType.BAR_NO_TITLE
        else:
            cont_type = ICLinearContainerType.BAR

        super(ICLinearSlide, self).__init__(cont_type, widget_id, *args, **kwargs)

        # setup the local variables
        self._name: str = name

        # the slider bar
        self.slider: ICSlider = ICSlider(values, current_value, position, widget_id)
        self.slider.changed.connect(self.value_changed)
        self.add_central_widget(self.slider)

        # initialise the local variables
        self.title = name
        self.value = current_value
        self.unit = unit

        # number of steps for drawing ticks in the gauge bar
        self._display_steps: int = display_steps

        # selected values and displayed values for the scale
        self._scale_values: list[float] = values
        self._scale_displayed_values: list[str] = displayed_values

        # create the display lists
        axis_scale_values, axis_scale_displayed_values = ICLinearAxis.select_ticks(values, displayed_values, display_steps)

        # add the scale bar
        self.add_first_scale_bar(name, axis_scale_values, axis_scale_displayed_values, ICWidgetPosition.opposite(position))

        self.vertical_gauge_width = ICDisplayConfig.LinearGaugeVerticalMaxWidth
        self.horizontal_gauge_height = ICDisplayConfig.LinearGaugeHorizontalMaxHeight

        # override the base Size policy
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)

        # call layout update to specify size
        self.on_layout_update()

    ########################################################
    # properties
    ########################################################
    @property
    def scale_values(self) -> list[float]:
        return self._scale_values

    @property
    def scale_displayed_values(self) -> list[str]:
        return self._scale_displayed_values

    ########################################################
    # functions
    ########################################################
    # override the default paint event
    def showEvent(self, e):
        self.on_layout_update()

    ########################################################
    # base class event overrides
    ########################################################
    # change layout based on the orientation
    def on_layout_update(self) -> None:
        if self.scale_bar_one is not None:
            scale_width = self.scale_bar_one.estimate_max_scale_width()

        if self.position.is_horizontal():
            self.size_hint = (ICDisplayConfig.LinearGaugeHorizontalWidth, ICDisplayConfig.LinearGaugeHorizontalMaxHeight)
            if self.scale_bar_one is not None:
                gauge_width = ICDisplayConfig.LinearGaugeHorizontalMaxHeight - scale_width
            else:
                gauge_width = ICDisplayConfig.LinearGaugeHorizontalMaxHeight
            self.slider.size_hint = (ICDisplayConfig.LinearGaugeHorizontalWidth, gauge_width)
            if self.scale_bar_one is not None:
                self.scale_bar_one.size_hint = (ICDisplayConfig.LinearGaugeHorizontalWidth, scale_width)

        else:
            self.size_hint = (ICDisplayConfig.LinearGaugeVerticalMaxWidth, ICDisplayConfig.LinearGaugeVerticalHeight)
            if self.scale_bar_one is not None:
                gauge_width = ICDisplayConfig.LinearGaugeVerticalMaxWidth - scale_width
            else:
                gauge_width = ICDisplayConfig.LinearGaugeVerticalMaxWidth
            self.slider.size_hint = (gauge_width, ICDisplayConfig.LinearGaugeVerticalHeight)
            if self.scale_bar_one is not None:
                self.scale_bar_one.size_hint = (scale_width, ICDisplayConfig.LinearGaugeVerticalHeight)

    def on_value_update(self, value: float) -> None:
        self.slider.current_value = value

    ########################################################
    # functions
    ########################################################

    ########################################################
    # base class event overrides
    ########################################################

    ########################################################
    # slots
    ########################################################
    # @pyqtSlot(float)
    def value_changed(self, val: float) -> None:
        self.value = val


class ICLinearSlideDialog(ICConfigDialogTemplate):
    """
        A helper dialog class to for linear slide
    """

    def __init__(self, name: str, unit: str, values: list[float], current_value: float, displayed_values: list[str] = None, display_steps: int = 5,
                 show_title: bool = True, show_value: bool = True, position: ICWidgetPosition = ICWidgetPosition.Top, widget_id: int = 0, *args, **kwargs):
        super(ICLinearSlideDialog, self).__init__(*args, **kwargs)

        # gauge colors normal
        self._gauge_color_normal_light: QtGui.QColor = ICDisplayConfig.LinearGaugeNormalLight
        self._gauge_color_normal_dark: QtGui.QColor = ICDisplayConfig.LinearGaugeNormalDark

        # gauge colors alarmed
        self._gauge_color_alarm_light: QtGui.QColor = ICDisplayConfig.LinearGaugeErrorLight
        self._gauge_color_alarm_dark: QtGui.QColor = ICDisplayConfig.LinearGaugeErrorDark

        layout = QtWidgets.QVBoxLayout()

        self._linear_slide: ICLinearSlide = ICLinearSlide(name, unit, values, current_value, displayed_values, display_steps,
                                                          show_title, show_value, position, widget_id)
        layout.addWidget(self._linear_slide)

        layout.addLayout(self.generate_ok_cancel_buttons())

        self.setLayout(layout)

    ########################################
    # property
    ########################################
    @property
    def linear_slide(self) -> ICLinearSlide:
        return self._linear_slide

        # get the normal gauge color

    @property
    def gauge_color_normal(self) -> tuple[QtGui.QColor, QtGui.QColor]:
        return self._gauge_color_normal_light, self._gauge_color_normal_dark

    # set the normal gauge color
    @gauge_color_normal.setter
    def gauge_color_normal(self, clr: tuple[QtGui.QColor, QtGui.QColor]) -> None:
        self._gauge_color_normal_light = clr[0]
        self._gauge_color_normal_dark = clr[1]

    # get the alarm gauge color
    @property
    def gauge_color_alarm(self) -> tuple[QtGui.QColor, QtGui.QColor]:
        return self._gauge_color_alarm_light, self._gauge_color_alarm_dark

    # set the normal gauge color
    @gauge_color_alarm.setter
    def gauge_color_alarm(self, clr: tuple[QtGui.QColor, QtGui.QColor]) -> None:
        self._gauge_color_alarm_light = clr[0]
        self._gauge_color_alarm_dark = clr[1]

    ####################################
    # Callback functions
    ####################################
    # called when ok is clicked
    def on_ok_clicked(self) -> None:
        # selected values
        self._value = self._linear_slide.value
        # selected display value
        index = self._linear_slide.scale_values.index(self._value)
        self._display_value = self._linear_slide.scale_displayed_values[index]

    # draw the ring
    def draw_additional(self, painter: QtGui.QPainter, width: int, height: int, keep_out_width: int, keep_out_height: int) -> None:
        # create the gradient
        half_height = 0.5 * height
        half_width = 0.5 * width

        # setup the brush
        gradient = QtGui.QConicalGradient(half_width, half_height, 90)

        if self._linear_slide.slider.alarm_activated:
            gradient.setColorAt(0, self._gauge_color_alarm_light)
            gradient.setColorAt(1, self._gauge_color_alarm_dark)
        else:
            gradient.setColorAt(0, self._gauge_color_normal_light)
            gradient.setColorAt(1, self._gauge_color_normal_dark)

        painter.setBrush(gradient)

        # setup the pen
        pen = QtGui.QPen()
        pen.setBrush(gradient)
        painter.setPen(pen)

        # calculate the path
        path = QtGui.QPainterPath()
        path.setFillRule(Qt.OddEvenFill)
        theta = 360 * (self._linear_slide.value - self._linear_slide.slider.values[0]) / \
                (self._linear_slide.slider.values[-1] - self._linear_slide.slider.values[0])

        # smaller radius
        box_length = sqrt(2) * (max(keep_out_width, keep_out_height))
        half_box_length = box_length / 2
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

