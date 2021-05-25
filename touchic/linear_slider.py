# -*- coding: utf-8 -*-
"""
Created on May  20 2021

@author: Prosenjit

A linear slider to graphically enter data
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from .display_config import ICDisplayConfig
from .base_widget import ICBaseWidget, ICWidgetState, ICWidgetOrientation


class ICSlider(ICBaseWidget):
    """
    A linear slider class to enter a data point using GUI
    """

    # emits the value changed
    changed = pyqtSignal(float)
    
    def __init__(self, values: list[float], current_value: float, displayed_values: list[str] = None,
                 orient: ICWidgetOrientation = ICWidgetOrientation.Horizontal, widget_id: int = 0,
                 *args, **kwargs):
        super(ICSlider, self).__init__(widget_id, *args, **kwargs)

        # setup the variables
        # list of valid values from which the user can select
        self._internal_values: list[float] = values

        # set up the displayed values
        if displayed_values is None:
            self._displayed_values: list[str] = [str(x) for x in values]
        else:
            self._displayed_values: list[str] = displayed_values

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

        # color for the slide background
        self._slide_color_light: QtGui.QColor = ICDisplayConfig.LinearSlideBoxColorLight
        self._slide_color_dark: QtGui.QColor = ICDisplayConfig.LinearSlideBoxColorDark

        # color for the slide groove
        self._groove_color_light: QtGui.QColor = ICDisplayConfig.LinearSlideColorLight
        self._groove_color_dark: QtGui.QColor = ICDisplayConfig.LinearSlideColorDark

        # color for the scale
        self._scale_color_light: QtGui.QColor = ICDisplayConfig.LinearSlideRulerColorLight
        self._scale_color_dark: QtGui.QColor = ICDisplayConfig.LinearSlideRulerColorDark

        # color of the knob
        self._knob_color_light: QtGui.QColor = ICDisplayConfig.LinearSlideKnobLight
        self._knob_color_dark: QtGui.QColor = ICDisplayConfig.LinearSlideKnobDark

        # y axis tick size and color
        self._tick_color: QtGui.QColor = ICDisplayConfig.LinearGaugeRulerColor
        self._tick_text_size: int = ICDisplayConfig.GeneralTextSize
        self._tick_index_steps: int = 0

        # redrawing scales
        self._redrawing_scales = True

        # calculate optimum ticks
        self._calculate_tick_steps()

        # click-ability and focus-ability
        self.focusable = True
        self.clickable = True

        # set the orientation of the widget
        self.orientation = orient

        # display configuration
        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

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
            gap = [abs(x - new_val) for x in self._internal_values]
            self._selected_index = gap.index(min(gap))
            self._selected_value = self._internal_values[self._selected_index]
            self.changed.emit(self._selected_value)
            self.append_history("set", self._selected_value)
            # no need to redraw scales
            self._redrawing_scales = False
            self.update()

    # displayed values
    @property
    def displayed_values(self) -> list[str]:
        return self._displayed_values

    # slider color
    @property
    def slider_colors(self) -> [QtGui.QColor, QtGui.QColor]:
        return self._slide_color_light, self._slide_color_dark

    @slider_colors.setter
    def slider_colors(self, clrs: [QtGui.QColor, QtGui.QColor]) -> None:
        self._slide_color_light = clrs[0]
        self._slide_color_dark = clrs[1]
        self.update()

    # groove colors
    @property
    def groove_colors(self) -> [QtGui.QColor, QtGui.QColor]:
        return self._groove_color_light, self._groove_color_dark

    @groove_colors.setter
    def groove_colors(self, clrs: [QtGui.QColor, QtGui.QColor]) -> None:
        self._groove_color_light = clrs[0]
        self._groove_color_dark = clrs[1]
        self.update()

    # scale colors
    @property
    def scale_colors(self) -> [QtGui.QColor, QtGui.QColor]:
        return self._scale_color_light, self._scale_color_dark

    @scale_colors.setter
    def scale_colors(self, clrs: [QtGui.QColor, QtGui.QColor]) -> None:
        self._scale_color_light = clrs[0]
        self._scale_color_dark = clrs[1]
        self.update()

    # knob colors
    @property
    def knob_colors(self) -> [QtGui.QColor, QtGui.QColor]:
        return self._knob_color_light, self._knob_color_dark

    @knob_colors.setter
    def knob_colors(self, clrs: [QtGui.QColor, QtGui.QColor]) -> None:
        self._knob_color_light = clrs[0]
        self._knob_color_dark = clrs[1]
        self.update()

    # tick color
    @property
    def tick_color(self) -> QtGui.QColor:
        return self._tick_color

    @tick_color.setter
    def tick_color(self, clr: QtGui.QColor) -> None:
        self._tick_color = clr
        self.update()

    # tick text size
    @property
    def tick_text_size(self) -> int:
        return self._tick_text_size

    @tick_text_size.setter
    def tick_text_size(self, txt_sz: int) -> None:
        self._tick_text_size = txt_sz
        self.update()

    # tick steps
    @property
    def tick_steps(self) -> int:
        return self._tick_index_steps

    @tick_steps.setter
    def tick_steps(self, stp: int) -> None:
        self._tick_index_steps = stp
        self.update()

    ########################################################
    # functions
    ########################################################
    # evaluate the optimum number of steps
    def _calculate_tick_steps(self):
        num_vals = len(self._internal_values)
        test_steps = [(8 - x) for x in range(7)]
        for step in test_steps:
            if num_vals % step == 0:
                self._tick_index_steps = int(num_vals / step)
                return
        # default steps
        self._tick_index_steps = int(num_vals / 2)

    ########################################################
    # base class event overrides
    ########################################################
    # mouse pressed event
    def on_mouse_pressed(self, event: QtGui.QMouseEvent) -> None:
        # mouse pressed event
        if event.button() & Qt.LeftButton:
            dist = event.pos() - self._knob_loc
            lsqr = QtCore.QPointF.dotProduct(dist, dist)
            if lsqr < 225:
                self._sliding = True

    # mouse moved event
    def on_mouse_moved(self, event: QtGui.QMouseEvent) -> None:
        if self._sliding:
            tmp_wdth = self.width()
            tmp_hght = self.height()
            min_slide = 20
            max_slide = (tmp_wdth - 20) if self.orientation == ICWidgetOrientation.Horizontal else (tmp_hght - 20)
            new_pos = event.pos().x() if self.orientation == ICWidgetOrientation.Horizontal else max_slide - event.pos().y()
            # if the new position is between the slide geometry
            if min_slide <= new_pos <= max_slide:
                new_val = self._internal_values[0] + (new_pos - min_slide) * \
                          (self._internal_values[-1] - self._internal_values[0]) / (max_slide - min_slide)
                gap = [abs(x - new_val) for x in self._internal_values]
                self._selected_index = gap.index(min(gap))
                self._selected_value = self._internal_values[self._selected_index]
                self.changed.emit(self._selected_value)
                # no need to redraw scales
                self._redrawing_scales = False
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
                new_pos = event.pos().x() if self.orientation == ICWidgetOrientation.Horizontal else -event.pos().y()
                knob_pos = self._knob_loc.x() if self.orientation == ICWidgetOrientation.Horizontal else -self._knob_loc.y()
                list_len = len(self._internal_values)
                if new_pos > knob_pos:
                    # increment by one pos
                    next_index = self._selected_index + 1
                    if next_index < list_len:
                        self._selected_value = self._internal_values[next_index]
                        self._selected_index = next_index
                        # no need to redraw scales
                        self._redrawing_scales = False
                        self.update()
                        self.valueChanged.emit(self._selected_value)
                        self.append_history("", self._selected_value)
                else:
                    # reduce by one pos
                    next_index = self._selected_index - 1
                    if next_index >= 0:
                        self._selected_value = self._internal_values[next_index]
                        self._selected_index = next_index
                        # no need to redraw scales
                        self._redrawing_scales = False
                        self.update()
                        self.valueChanged.emit(self._selected_value)
                        self.append_history("", self._selected_value)

    # orientation changed moved
    def on_orientation_changed(self) -> None:
        if self.orientation == ICWidgetOrientation.Horizontal:
            self.size_hint = (ICDisplayConfig.LinearSlideWidth, ICDisplayConfig.LinearSlideHeight)
            self.setMaximumSize(10000, ICDisplayConfig.LinearSlideHeight)
        else:
            self.size_hint = (ICDisplayConfig.LinearSlideHeight, ICDisplayConfig.LinearSlideWidth)
            self.setMaximumSize(ICDisplayConfig.LinearSlideHeight, 10000)
        self.update()

    ########################################################
    # overrides and event handlers
    ########################################################
    # paint the linear slide
    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.redraw(painter)

    # draw the widget
    def redraw(self, painter):
        # nothing to draw if the widget is hidden
        if self.state == ICWidgetState.Hidden:
            return

        # draw the main rectangle
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

        # reduce the drawing area to account for the selected rectangle
        tmp_wdth -= 6
        tmp_hght -= 6
        painter.translate(3, 3)

        # draw the slide background
        if self.orientation == ICWidgetOrientation.Horizontal:
            rect = QtCore.QRectF(0, tmp_hght/3, tmp_wdth, tmp_hght/3)
        else:
            rect = QtCore.QRectF(tmp_wdth/3, 0, tmp_wdth/3, tmp_hght)

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

        # draw the inner rectangle
        min_slide = 20
        max_slide = (tmp_wdth - 20) if self.orientation == ICWidgetOrientation.Horizontal else (tmp_hght - 20)
        slide_length = max_slide - min_slide
        if self.orientation == ICWidgetOrientation.Horizontal:
            rect = QtCore.QRectF(min_slide, tmp_hght/2 - 8, slide_length, 16)
            brush = QtGui.QLinearGradient(rect.topLeft(), rect.bottomLeft())
        else:
            rect = QtCore.QRectF(tmp_wdth/2 - 8, min_slide, 16, slide_length)
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

        # draw the scale
        # calculate the length of the scale
        curr_val = self._selected_value
        pos = (curr_val - self._internal_values[0])/(self._internal_values[-1] - self._internal_values[0])
        scale_len = pos * (max_slide - min_slide)

        if self.orientation == ICWidgetOrientation.Horizontal:
            rect = QtCore.QRectF(min_slide, tmp_hght/2 - 7, scale_len, 14)
            brush = QtGui.QLinearGradient(rect.topLeft(), rect.bottomRight())
        else:
            rect = QtCore.QRectF(tmp_wdth/2 - 7, max_slide - scale_len, 14, scale_len)
            brush = QtGui.QLinearGradient(rect.bottomLeft(), rect.topRight())

        # set the brush
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

        # set the brush for the knob
        if self.orientation == ICWidgetOrientation.Horizontal:
            rect = QtCore.QRectF(min_slide + scale_len - 20, tmp_hght/2 - 15, 40, 30)
            self._knob_loc = QtCore.QPointF(scale_len + min_slide, tmp_hght/2)
        else:
            rect = QtCore.QRectF(tmp_wdth/2 - 15, max_slide - scale_len - 20, 30, 40)
            self._knob_loc = QtCore.QPointF(tmp_wdth/2, max_slide - scale_len)

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

        # draw the volume background
        #poly = QtGui.QPolygonF()
        if self.orientation == ICWidgetOrientation.Horizontal:
            slide_base = tmp_hght/3 - 10
            slide_top = 10
        #    poly.append(QtCore.QPointF(min_slide, slide_base))
        #    poly.append(QtCore.QPointF(min_slide, slide_base - 10))
        #    poly.append(QtCore.QPointF(max_slide, slide_top))
        #    poly.append(QtCore.QPointF(max_slide, slide_base))
        #    poly.append(QtCore.QPointF(min_slide, slide_base))
        #    brush = QtGui.QLinearGradient(QtCore.QPointF(max_slide, slide_top), QtCore.QPointF(max_slide, slide_base))
        else:
            slide_base = 2*tmp_wdth/3 + 10
            slide_top = tmp_wdth - 10
        #    poly.append(QtCore.QPointF(slide_base, max_slide))
        #    poly.append(QtCore.QPointF(slide_base + 10, max_slide))
        #    poly.append(QtCore.QPointF(slide_top, min_slide))
        #    poly.append(QtCore.QPointF(slide_base, min_slide))
        #    poly.append(QtCore.QPointF(slide_base, max_slide))
        #    brush = QtGui.QLinearGradient(QtCore.QPointF(slide_top, min_slide), QtCore.QPointF(max_slide, slide_base))

        # select the brush
        #brush.setColorAt(0, self._groove_color_light)
        #brush.setColorAt(1, self._groove_color_dark)
        #painter.setBrush(brush)

        # select the pen
        #pen.setWidth(5)
        #pen.setBrush(brush)
        #painter.setPen(pen)

        # paint the path
        #path = QtGui.QPainterPath()
        #path.setFillRule(Qt.WindingFill)
        #path.addPolygon(poly)
        #painter.drawPath(path)

        # draw the volume foreground
        poly = QtGui.QPolygonF()
        if self.orientation == ICWidgetOrientation.Horizontal:
            slide_y = 10 + scale_len * (slide_base - 10 - slide_top) / slide_length
            poly.append(QtCore.QPointF(min_slide, slide_base))
            poly.append(QtCore.QPointF(min_slide, slide_base - 10))
            poly.append(QtCore.QPointF(min_slide + scale_len, slide_base - slide_y))
            poly.append(QtCore.QPointF(min_slide + scale_len, slide_base))
            poly.append(QtCore.QPointF(min_slide, slide_base))
            brush = QtGui.QLinearGradient(QtCore.QPointF(max_slide, slide_top), QtCore.QPointF(min_slide, slide_base))
        else:
            slide_x = 10 + scale_len * (slide_top - slide_base - 10) / slide_length
            poly.append(QtCore.QPointF(slide_base, max_slide))
            poly.append(QtCore.QPointF(slide_base + 10, max_slide))
            poly.append(QtCore.QPointF(slide_base + slide_x, max_slide - scale_len))
            poly.append(QtCore.QPointF(slide_base, max_slide - scale_len))
            poly.append(QtCore.QPointF(slide_base, max_slide))
            brush = QtGui.QLinearGradient(QtCore.QPointF(slide_top, min_slide), QtCore.QPointF(slide_base, max_slide))

        # set the brush
        brush.setColorAt(0, self._slide_color_light)
        brush.setColorAt(1, self._scale_color_dark)
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

        # check if we need to redraw scales
        if not self._redrawing_scales:
            self._redrawing_scales = True
            return

        # define the pen to draw the scale
        pen = QtGui.QPen()
        pen.setWidth(3)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setBrush(self._tick_color)
        painter.setPen(pen)

        # calculate and draw the vertical or horizontal line
        if self.orientation == ICWidgetOrientation.Vertical:
            rule_loc = tmp_wdth/3 - 7
            painter.drawLine(QtCore.QPointF(rule_loc, min_slide), QtCore.QPointF(rule_loc, max_slide))
        else:
            rule_loc = tmp_hght - (tmp_hght/3 - 7)
            painter.drawLine(QtCore.QPointF(min_slide, rule_loc), QtCore.QPointF(max_slide, rule_loc))

        # modify the font to write the scale
        fnt = painter.font()
        fnt.setPixelSize(self._tick_text_size)
        painter.setFont(fnt)

        # draw the first tick
        tick_pos = min_slide
        curr_index: int = self._tick_index_steps
        max_index = len(self._internal_values)
        incr_x = ((self._internal_values[curr_index] - self._internal_values[0]) /
                  (self._internal_values[-1] - self._internal_values[0])) * slide_length
        if self.orientation == ICWidgetOrientation.Horizontal:
            painter.drawLine(QtCore.QPointF(tick_pos, rule_loc), QtCore.QPointF(tick_pos, rule_loc + 5))
            rect = QtCore.QRectF(tick_pos, rule_loc + 7, incr_x, self._tick_text_size + 5)
            painter.drawText(rect, Qt.AlignLeft, self._displayed_values[0])
        else:
            painter.drawLine(QtCore.QPointF(rule_loc, tick_pos), QtCore.QPointF(rule_loc - 5, tick_pos))
            rect = QtCore.QRectF(0, tick_pos, rule_loc - 7, self._tick_text_size + 5)
            painter.drawText(rect, Qt.AlignRight, self._displayed_values[max_index-1])

        # draw the remaining ticks
        while curr_index < max_index:
            # calculate the location for drawing the tick
            tick_pos = ((self._internal_values[curr_index] - self._internal_values[0]) /
                        (self._internal_values[-1] - self._internal_values[0])) * slide_length + min_slide
            if self.orientation == ICWidgetOrientation.Horizontal:
                painter.drawLine(QtCore.QPointF(tick_pos, rule_loc), QtCore.QPointF(tick_pos, rule_loc + 5))
                rect = QtCore.QRectF(tick_pos - self._tick_text_size, rule_loc + 7, incr_x, self._tick_text_size + 5)
                painter.drawText(rect, Qt.AlignLeft, self._displayed_values[curr_index])
            else:
                painter.drawLine(QtCore.QPointF(rule_loc, tick_pos), QtCore.QPointF(rule_loc - 5, tick_pos))
                rect = QtCore.QRectF(0, tick_pos - 0.5 * self._tick_text_size, rule_loc - 7, self._tick_text_size + 5)
                painter.drawText(rect, Qt.AlignRight, self._displayed_values[max_index - curr_index])
            # increment index
            curr_index += self._tick_index_steps
        # draw the last tick
        tick_pos = max_slide
        if self.orientation == ICWidgetOrientation.Horizontal:
            painter.drawLine(QtCore.QPointF(tick_pos, rule_loc), QtCore.QPointF(tick_pos, rule_loc + 5))
            rect = QtCore.QRectF(tick_pos - incr_x, rule_loc + 7, incr_x, self._tick_text_size + 5)
            painter.drawText(rect, Qt.AlignRight, self._displayed_values[-1])
        else:
            painter.drawLine(QtCore.QPointF(rule_loc, tick_pos), QtCore.QPointF(rule_loc - 5, tick_pos))
            rect = QtCore.QRectF(0, tick_pos - self._tick_text_size, rule_loc - 7, self._tick_text_size + 5)
            painter.drawText(rect, Qt.AlignRight, self._displayed_values[0])


class ICLinearSlide(ICBaseWidget):
    """
    Compound widget with a slider and label for displaying the plotted value
    """
    def __init__(self, name: str, values: list[float], current_value: float, displayed_values: list[str] = None,
                 orient: ICWidgetOrientation = ICWidgetOrientation.Horizontal, widget_id: int = 0,
                 *args, **kwargs):
        super(ICLinearSlide, self).__init__(widget_id, *args, **kwargs)

        # setup the local variables
        self._name: str = name

        # the slider bar
        self.slider = ICSlider(values, current_value, displayed_values, orient, widget_id)

        # title and value text color
        self._title_color: QtGui.QColor = ICDisplayConfig.HeaderTextColor
        self._value_color: QtGui.QColor = ICDisplayConfig.ValueTextColor

        # title, value and unit text size
        self._title_size: int = ICDisplayConfig.LabelTextSize
        self._value_size: int = ICDisplayConfig.LabelTextSize

        # layout the widget
        layout = QtWidgets.QVBoxLayout()

        # add the top title
        self._title_top = QtWidgets.QLabel("", self)
        self._title_top.setStyleSheet("QLabel { background-color : " +
                                      ICDisplayConfig.QtColorToSting(self.background_color) + "; color : " +
                                      ICDisplayConfig.QtColorToSting(self._title_color) + ";}")
        self._title_top.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._title_top)

        # add the slider
        layout.addWidget(self.slider)

        # add the bottom layout
        hb_layout = QtWidgets.QHBoxLayout()

        # add the bottom title
        self._title_bot = QtWidgets.QLabel("", self)
        self._title_bot.setStyleSheet("QLabel { background-color : " +
                                      ICDisplayConfig.QtColorToSting(self.background_color) + "; color : " +
                                      ICDisplayConfig.QtColorToSting(self._title_color) + ";}")
        self._title_bot.setAlignment(Qt.AlignCenter)
        hb_layout.addWidget(self._title_bot)

        # add the value
        self._value = QtWidgets.QLabel("", self)
        self._value.setStyleSheet("QLabel { background-color : " +
                                  ICDisplayConfig.QtColorToSting(self.background_color) + "; color : " +
                                  ICDisplayConfig.QtColorToSting(self._value_color) + "; border-radius : 5px; }")
        self._value.setAlignment(Qt.AlignCenter)
        hb_layout.addWidget(self._value)

        # add the layout
        layout.addLayout(hb_layout)
        self.setLayout(layout)

        # fixed gauge width
        self._gauge_width_limit: int = ICDisplayConfig.LinearGaugeVerticalWidth         # for vertical slider
        self._gauge_height_limit: int = ICDisplayConfig.LinearGaugeHorizontalHeight     # for horizontal slider

        # set the orientation
        self.orientation = orient

        # set basic behaviour
        self.focusable = False
        self.clickable = False

        # override the base Size policy
        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

        # connect value changed event from slider
        self.slider.changed.connect(self.value_changed)

        # update the display
        self._local_update()

    ########################################################
    # properties
    ########################################################
    # get the gauge title
    @property
    def name(self) -> str:
        return self._name

    # set the gauge title
    @name.setter
    def name(self, nm: str) -> None:
        self._name = nm
        self._title_update()

    # get the slider value
    @property
    def value(self) -> float:
        return self.slider.current_value

    # set the slider value
    @value.setter
    def value(self, ft: float) -> None:
        if self.slider.current_value == ft:
            return
        self.slider.current_value = ft
        self._value_update()

    # get the color of the title
    @property
    def title_text_color(self) -> QtGui.QColor:
        return self._title_color

    # set the title color
    @title_text_color.setter
    def title_text_color(self, clr: QtGui.QColor) -> None:
        self._title_color = clr
        self._title_top.setStyleSheet("QLabel { background-color : " +
                                      ICDisplayConfig.QtColorToSting(self.background_color) + "; color : " +
                                      ICDisplayConfig.QtColorToSting(self._title_color) + ";}")
        self._title_bot.setStyleSheet("QLabel { background-color : " +
                                      ICDisplayConfig.QtColorToSting(self.background_color) + "; color : " +
                                      ICDisplayConfig.QtColorToSting(self._title_color) + ";}")
        self._title_update()

    # get the color of the title
    @property
    def value_text_color(self) -> QtGui.QColor:
        return self._value_color

    # set the title color
    @value_text_color.setter
    def value_text_color(self, clr: QtGui.QColor) -> None:
        self._value_color = clr
        self._value_bot.setStyleSheet("QLabel { background-color : " +
                                      ICDisplayConfig.QtColorToSting(self.background_color) + "; color : " +
                                      ICDisplayConfig.QtColorToSting(self._value_color) + "; border-radius : 5px; }")
        self._value_update()

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

    ########################################################
    # functions
    ########################################################
    # update title
    def _title_update(self):
        # nothing to do if hidden
        if self.state == ICWidgetState.Hidden:
            return

        # orientation determines which label to update
        if self.orientation == ICWidgetOrientation.Vertical:
            selected_title = self._title_top
        else:
            selected_title = self._title_bot

        # update the text based on the state
        if self.state in (ICWidgetState.Transparent, ICWidgetState.FrameOnly):
            selected_title.setText("<span style='font-size:" + "{}".format(self._title_size) + "pt;'>" +
                                   "</span>")
        else:
            selected_title.setText("<span style='font-size:" + "{}".format(self._title_size) + "pt;'>" +
                                   self._name + "</span>")
        # update the title
        selected_title.update()

    # update value
    def _value_update(self):
        # nothing to do if hidden
        if self.state == ICWidgetState.Hidden:
            return

        # update the value based on widget visibility state
        if self.state in (ICWidgetState.Transparent, ICWidgetState.FrameOnly):
            # set background color and do not draw
            self._value.setText("<span style='font-size:" + "{}".format(self._value_size) + "pt;'>" +
                                "</span>")
        else:
            # update the value text
            self._value.setText("<span style='font-size:" + "{}".format(self._value_size) + "pt;'>" +
                                "{:.2f}".format(self.slider.current_value) + "</span>")
        # update the label
        self._value.update()

    # update the widget
    def _local_update(self):
        # update the title text
        self._title_update()
        # update the value text
        self._value_update()
        # update the slider
        self.slider.update()
        # update self
        self.update()

    ########################################################
    # base class event overrides
    ########################################################
    # change layout based on the orientation
    def on_orientation_changed(self) -> None:
        self.slider.orientation = self.orientation
        if self.orientation == ICWidgetOrientation.Horizontal:
            self.size_hint = (ICDisplayConfig.LinearSlideWidth, ICDisplayConfig.LinearSlideHeight)
            self.setMaximumSize(10000, self.horizontal_gauge_height)
            self._title_top.hide()
            self._title_top.setMaximumSize(0, 0)
            self._title_bot.show()
            self._title_bot.setMaximumSize(10000, 10000)
        else:
            self.size_hint = (ICDisplayConfig.LinearSlideHeight, ICDisplayConfig.LinearSlideWidth)
            self.setMaximumSize(self.vertical_gauge_width, 10000)
            self._title_bot.hide()
            self._title_bot.setMaximumSize(0, 0)
            self._title_top.show()
            self._title_top.setMaximumSize(10000, 10000)
        self._local_update()

    # change the visibility of elements
    def on_state_changed(self) -> None:
        if self.state == ICWidgetState.Hidden:
            # hide both the title labels
            self._title_bot.hide()
            self._title_bot.setMaximumSize(0, 0)
            self._title_top.hide()
            self._title_top.setMaximumSize(0, 0)

            # hide the value label
            self._value.hide()
            self._value.setMaximumSize(0, 0)

            # hide the slider
            self.slider.state = ICWidgetState.Hidden
            self.slider.update()

            # hide self
            self.hide()
            self.update()
        else:
            # all other states are managed in the display update routines
            # show self
            self.show()

            # show the value display
            self._value.show()
            self._value.setMaximumSize(10000, 10000)

            # show the title based on the orientation
            self.on_orientation_changed()

            # set the gauge bar state
            self.slider.state = self.state
            self._local_update()

    ########################################################
    # slots
    ########################################################
    @pyqtSlot(float)
    def value_changed(self, val: float) -> None:
        self._value_update()
