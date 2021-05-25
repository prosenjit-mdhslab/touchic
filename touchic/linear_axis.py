# -*- coding: utf-8 -*-
"""
Created on May 24 2021

@author: Prosenjit

A linear axis for use with different widgets
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from .display_config import ICDisplayConfig
from .base_widget import ICBaseWidget, ICWidgetState, ICWidgetOrientation, ICWidgetPosition


class ICLinearAxis(ICBaseWidget):
    """
        A linear axis class for use with different GUI widgets
    """
    AXIS_OFFSET = 0

    def __init__(self, values: list[float], displayed_values: list[str], width: int, height: int,
                 orient: ICWidgetOrientation = ICWidgetOrientation.Horizontal, widget_id: int = 0,
                 *args, **kwargs):
        super(ICLinearAxis, self).__init__(widget_id, *args, **kwargs)

        # setup local variables
        self._values: list[float] = values
        self._displayed_values: list[str] = displayed_values

        # should we draw the text labels
        self._drawing_labels: bool = True

        # position of the axis label
        self._position: ICWidgetPosition = ICWidgetPosition.Bottom

        # tick color and text size
        self._tick_color: QtGui.QColor = ICDisplayConfig.LinearGaugeRulerColor
        self._tick_text_size: int = ICDisplayConfig.GeneralTextSize

        # margin left out on both sides of the scale
        self._margin: int = 0

        # provide the initial size hint
        self.size_hint = (width, height)

        # click-ability and focus-ability
        self.focusable = False
        self.clickable = False

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
    # values get
    @property
    def values(self) -> list[float]:
        return self._values

    # displayed values  get
    @property
    def displayed_values(self) -> list[str]:
        return self._displayed_values

    # are we drawing the labels
    @property
    def drawing_labels(self) -> bool:
        return self._drawing_labels

    @drawing_labels.setter
    def drawing_labels(self, cond: bool) -> None:
        self._drawing_labels = cond
        self.update()

    # position of the axis
    @property
    def position(self) -> ICWidgetPosition:
        return self._position

    @position.setter
    def position(self, pos: ICWidgetPosition) -> None:
        # set position appropriate to the orientation
        if self.orientation == ICWidgetOrientation.Horizontal:
            if pos in (ICWidgetPosition.Bottom, ICWidgetPosition.Top):
                self._position = pos
                self.update()
        else:
            if pos in (ICWidgetPosition.Left, ICWidgetPosition.Right):
                self._position = pos
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

    # margin from the edge of the widget
    @property
    def margin(self) -> int:
        return self._margin

    @margin.setter
    def margin(self, x: int) -> None:
        self._margin = x
        self.update()

    ########################################################
    # override base class event handlers
    ########################################################
    def on_orientation_changed(self) -> None:
        # set up the default position for the orientation
        if self.orientation == ICWidgetOrientation.Horizontal:
            if self._position not in (ICWidgetPosition.Bottom, ICWidgetPosition.Top):
                self._position = ICWidgetPosition.Bottom
        else:
            if self._position not in (ICWidgetPosition.Left, ICWidgetPosition.Right):
                self._position = ICWidgetPosition.Left
        self.update()

    ########################################################
    # override event handlers
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

        # translate and fix the dimensions
        painter.translate(3, 3)
        tmp_hght -= 6
        tmp_wdth -= 6

        # modify the pen to draw the vertical or horizontal scale bar
        pen = QtGui.QPen()
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setWidth(3)
        pen.setBrush(self._tick_color)
        painter.setPen(pen)

        # calculate and draw the vertical or horizontal line
        min_slide = self._margin
        if self.orientation == ICWidgetOrientation.Vertical:
            max_slide = tmp_hght - self._margin
            if self.position == ICWidgetPosition.Left:
                rule_loc = (tmp_wdth - self.AXIS_OFFSET)
                painter.drawLine(QtCore.QPointF(rule_loc, min_slide),
                                 QtCore.QPointF(rule_loc, max_slide))
            elif self.position == ICWidgetPosition.Right:
                rule_loc = self.AXIS_OFFSET
                painter.drawLine(QtCore.QPointF(rule_loc, min_slide),
                                 QtCore.QPointF(rule_loc, max_slide))
        else:
            max_slide = tmp_wdth - self._margin
            if self.position == ICWidgetPosition.Bottom:
                rule_loc = self.AXIS_OFFSET
                painter.drawLine(QtCore.QPointF(min_slide, rule_loc),
                                 QtCore.QPointF(max_slide, rule_loc))
            elif self.position == ICWidgetPosition.Top:
                rule_loc = tmp_hght - self.AXIS_OFFSET
                painter.drawLine(QtCore.QPointF(min_slide, rule_loc),
                                 QtCore.QPointF(max_slide, rule_loc))

        # modify the font to write the scale
        fnt = painter.font()
        fnt.setPixelSize(self._tick_text_size)
        painter.setFont(fnt)

        # draw the ticks
        curr_index = 0
        max_index = len(self._values)

        # length of slide in pixels
        slide_length = max_slide - min_slide

        # space between the ticks in pixels
        delta_x = ((self._values[1] - self._values[0]) / (self._values[-1] - self._values[0])) * slide_length

        # draw the ticks
        while curr_index < max_index:
            # calculate the location for drawing the tick
            tick_pos = ((self._values[curr_index] - self._values[0]) /
                        (self._values[-1] - self._values[0])) * slide_length + min_slide

            if self.orientation == ICWidgetOrientation.Horizontal:
                if self.position == ICWidgetPosition.Bottom:
                    # draw the tick
                    painter.drawLine(QtCore.QPointF(tick_pos, rule_loc), QtCore.QPointF(tick_pos, rule_loc + 5))

                    # if text is enabled then draw the text
                    if self._drawing_labels:
                        if curr_index == 0:
                            tick_pos_c = tick_pos
                            align = Qt.AlignLeft
                        elif curr_index == (max_index -1):
                            tick_pos_c = tick_pos - delta_x
                            align = Qt.AlignRight
                        else:
                            tick_pos_c = tick_pos - 0.5 * delta_x
                            align = Qt.AlignCenter

                        rect = QtCore.QRectF(tick_pos_c, rule_loc + 7, delta_x, self._tick_text_size + 5)
                        painter.drawText(rect, align, self._displayed_values[curr_index])

                elif self.position == ICWidgetPosition.Top:
                    # draw the tick
                    painter.drawLine(QtCore.QPointF(tick_pos, rule_loc), QtCore.QPointF(tick_pos, rule_loc - 5))

                    # if text is enabled then draw the text
                    if self._drawing_labels:
                        # if text is enabled then draw the text
                        if self._drawing_labels:
                            if curr_index == 0:
                                tick_pos_c = tick_pos
                                align = Qt.AlignLeft
                            elif curr_index == (max_index - 1):
                                tick_pos_c = tick_pos - delta_x
                                align = Qt.AlignRight
                            else:
                                tick_pos_c = tick_pos - 0.5 * delta_x
                                align = Qt.AlignCenter

                        rect = QtCore.QRectF(tick_pos_c, rule_loc - 12 - self._tick_text_size,
                                             delta_x, self._tick_text_size + 5)
                        painter.drawText(rect, align, self._displayed_values[curr_index])

            else:
                if self.position == ICWidgetPosition.Left:
                    # draw the tick
                    painter.drawLine(QtCore.QPointF(rule_loc, tick_pos), QtCore.QPointF(rule_loc - 5, tick_pos))

                    # if text is enabled then draw the text
                    if self._drawing_labels:
                        start_y = tick_pos
                        start_y = start_y if curr_index == 0 else (start_y - 0.5 * self._tick_text_size)
                        start_y = (start_y - 0.5 * self._tick_text_size - 3) if curr_index == max_index - 1 else start_y
                        rect = QtCore.QRectF(0, start_y, rule_loc - 7, self._tick_text_size + 5)
                        painter.drawText(rect, Qt.AlignRight, self._displayed_values[max_index - 1 - curr_index])
                elif self.position == ICWidgetPosition.Right:
                    # draw the tick
                    painter.drawLine(QtCore.QPointF(rule_loc, tick_pos), QtCore.QPointF(rule_loc + 5, tick_pos))

                    # if text is enabled then draw the text
                    if self._drawing_labels:
                        start_y = tick_pos
                        start_y = start_y if curr_index == 0 else (start_y - 0.5 * self._tick_text_size)
                        start_y = (start_y - 0.5 * self._tick_text_size - 3) if curr_index == max_index - 1 else start_y
                        rect = QtCore.QRectF(7, start_y, tmp_wdth - rule_loc - 7, self._tick_text_size + 5)
                        painter.drawText(rect, Qt.AlignLeft, self._displayed_values[max_index - 1 - curr_index])

            # increment the index
            curr_index += 1
