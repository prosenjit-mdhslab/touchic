# -*- coding: utf-8 -*-
"""
Created on May 18 2021

@author: Prosenjit

This a base class for most widgets
TODO: History should be truned off by default
"""

from enum import Enum, Flag
from collections import deque
from weakref import WeakValueDictionary
from datetime import datetime, timedelta
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from .display_config import ICDisplayConfig


class ICWidgetState(Enum):
    """
    Enum of widget display states. Determines how they are rendered.
    Also determines their response to user inputs
    """
    VisibleEnabled = 0
    VisibleDisabled = 1
    FrameOnly = 2
    Transparent = 3
    Hidden = 4


class ICWidgetPosition(Flag):
    """
        Enum for positioning of LED or other components within a widget
    """
    Bottom = 1
    Top = 2
    Left = 4
    Right = 8

    @classmethod
    def opposite(cls, pos):
        if pos == cls.Top:
            return cls.Bottom
        elif pos == cls.Bottom:
            return cls.Top
        elif pos == cls.Right:
            return cls.Left
        else:
            return cls.Right

    def is_horizontal(self) -> bool:
        return ICWidgetPosition.Bottom in self or ICWidgetPosition.Top in self

    def is_vertical(self) -> bool:
        return ICWidgetPosition.Right in self or ICWidgetPosition.Left in self


class ICWidgetHistory:
    """
    Class maintaining history of events and values for a widget
    """
    def __init__(self, tm: datetime, ev: str, val: float):
        self.event_time = tm
        self.event = ev
        self.value = val

    def __eq__(self, other):
        if isinstance(other, ICWidgetHistory):
            return ((self.event_time == other.event_time) and
                    (self.event == other.event) and
                    (self.value == self.value))
        else:
            return NotImplemented


class ICBaseWidget(QtWidgets.QWidget):
    """
    Base widget for all (or most) widgets
    """

    # instances dictionary for accessing all active widgets and accessing their event history
    _instances = WeakValueDictionary()
    _instance_number: int = 0

    def __init__(self, widget_id: int = 0, *args, **kwargs):
        super(ICBaseWidget, self).__init__(*args, **kwargs)

        # add the widget to the class level dictionary
        ICBaseWidget._instance_number += 1
        ICBaseWidget._instances[ICBaseWidget._instance_number] = self

        # store the instance id
        self._instance_id: int = ICBaseWidget._instance_number

        # id of the widget
        self._widget_id: int = widget_id

        # sets the click-ability of the button
        self._clickable: bool = False

        # set the visibility of the button
        self._state: ICWidgetState = ICWidgetState.VisibleEnabled

        # set the widget orientation
        self._position: ICWidgetPosition = ICWidgetPosition.Bottom

        # focus-ability and in/out state management
        self._focusable: bool = False
        self._in_focus: bool = False

        # maintain history
        self._enable_history: bool = False
        self._history_len: int = 20
        self._history = deque(maxlen=self._history_len)

        # time of last event
        self._last_event_time: datetime = datetime.now()

        # append timeout for consecutive events
        self._event_append_timeout: int = 0

        # background color
        self._background_color: QtGui.QColor = ICDisplayConfig.BackgroundColor

        # in focus color
        self._in_focus_color: QtGui.QColor = ICDisplayConfig.InFocusColor

        # minimum width of the window
        self._width_min: int = 0

        # minimum height of the window
        self._height_min: int = 0

        # setup visual effects
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

        # background color of the button
        self.setStyleSheet("background-color : " + ICDisplayConfig.QtColorToSting(self._background_color) + ";")

    ########################################################
    # properties
    ########################################################
    # returns the id of the button.
    # if it is not defined then None is returned
    @property
    def widget_id(self) -> int:
        return self._widget_id

    # set the button id. once set it cannot be reset to none
    # button id is always greater than zero
    @widget_id.setter
    def widget_id(self, wid: int) -> None:
        if wid > 0:
            self._widget_id = wid
            self.update()

    # return if the button is clickable
    @property
    def clickable(self) -> bool:
        return self._clickable

    # set the click-ability of the button
    # if enabled the button will emit the clicked signal
    @clickable.setter
    def clickable(self, click_able: bool) -> None:
        self._clickable = click_able

    # get the visibility of the button
    @property
    def state(self) -> ICWidgetState:
        return self._state

    # set the visibility of the button
    @state.setter
    def state(self, st: ICWidgetState) -> None:
        if self._state != st:
            self._state = st
            if self._state in (ICWidgetState.Hidden, ICWidgetState.Transparent, ICWidgetState.VisibleDisabled):
                self._clickable = False
            else:
                self._clickable = True
            self.on_state_changed()
            self.update()

    # get the position of the component or widget with respect to other widgets
    # this only maintains the property here. actual rendering is class dependent.
    @property
    def position(self) -> ICWidgetPosition:
        return self._position

    # set the orientation of the widget
    @position.setter
    def position(self, pos: ICWidgetPosition) -> None:
        if self._position != pos:
            self._position = pos
            self.on_position_changed()
            self.update()

    # get focusable property
    @property
    def focusable(self) -> bool:
        return self._focusable

    # set the focusable property
    @focusable.setter
    def focusable(self, focus: bool) -> None:
        self._focusable = focus
        if self._focusable:
            self.setFocusPolicy(Qt.StrongFocus)
        else:
            self.setFocusPolicy(Qt.NoFocus)

    # read only "in focus" state
    @property
    def in_focus(self) -> bool:
        return self._in_focus

    # get the length of history maintained by the widget
    @property
    def history_length(self) -> int:
        return self._history_len

    # set the new length for the activity history
    # the history deque is resized
    # current history is copied to the resized
    @history_length.setter
    def history_length(self, new_len: int) -> None:
        new_history = deque(self._history, maxlen=new_len)
        self._history.clear()
        self._history = new_history
        self._history_len = new_len

    # read only property history
    @property
    def history(self) -> deque:
        return self._history

    # last event time readonly
    @property
    def last_event_time(self) -> datetime:
        return self._last_event_time

    # append timeout
    @property
    def history_append_interval_millis(self) -> int:
        return self._event_append_timeout

    @history_append_interval_millis.setter
    def history_append_interval_millis(self, tm: int) -> None:
        self._event_append_timeout = tm

    # get background colour
    @property
    def background_color(self) -> QtGui.QColor:
        return self._background_color

    # set background color
    @background_color.setter
    def background_color(self, clr: QtGui.QColor) -> None:
        self._background_color = clr
        self.update()

    # get background colour
    @property
    def focus_color(self) -> QtGui.QColor:
        return self._in_focus_color

    # set background color
    @focus_color.setter
    def focus_color(self, clr: QtGui.QColor) -> None:
        self._in_focus_color = clr
        self.update()

    # get size hint
    @property
    def size_hint(self) -> tuple[int, int]:
        return self._width_min, self._height_min

    # set size hint
    @size_hint.setter
    def size_hint(self, sz: tuple[int, int]) -> None:
        self._width_min = sz[0]
        self._height_min = sz[1]

    ########################################################
    # functions
    ########################################################
    # append to event history
    def append_history(self, desc: str, val: float) -> None:
        t_now = datetime.now()
        interval = (t_now - self._last_event_time)/timedelta(milliseconds=1)
        if interval > self.history_append_interval_millis:
            self._last_event_time = t_now
            self._history.append(ICWidgetHistory(t_now, desc, val))

    # clear the event history
    def clear_history(self) -> None:
        self._history.clear()

    # dhow the history
    def display_history(self) -> None:
        pass

    # class method to get access to all the active instances
    @classmethod
    def instances(cls):
        return cls._instances.values()

    ########################################################
    # methods to be overridden by subclasses
    ########################################################
    # mouse pressed event
    def on_mouse_pressed(self, event: QtGui.QMouseEvent) -> None:
        pass

    # mouse move event
    def on_mouse_moved(self, event: QtGui.QMouseEvent) -> None:
        pass

    # mouse release event
    def on_mouse_released(self, event: QtGui.QMouseEvent) -> None:
        pass

    # focus change event
    def on_focus_changed(self, event: QtGui.QFocusEvent) -> None:
        pass

    # wheel rotated
    def on_wheel_rotated(self, event: QtGui.QWheelEvent) -> None:
        pass

    # position changed
    def on_position_changed(self) -> None:
        pass

    # state changed
    def on_state_changed(self) -> None:
        pass

    ########################################################
    # overrides and event handlers
    ########################################################
    # size hint for the layout manager
    def sizeHint(self) -> QtCore.QSize:
        if self._state == ICWidgetState.Hidden:
            return QtCore.QSize(0, 0)
        else:
            return QtCore.QSize(self._width_min, self._height_min)

    # minimum size hint for the layout manager
    def minimumSizeHint(self) -> QtCore.QSize:
        if self._state == ICWidgetState.Hidden:
            return QtCore.QSize(0, 0)
        else:
            return QtCore.QSize(self._width_min, self._height_min)

    # handle the focus in event
    def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
        if self._focusable:
            self._in_focus = True
            self.on_focus_changed(event)
            self.update()

    # handle the focus out event
    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        if self._focusable:
            self._in_focus = False
            self.on_focus_changed(event)
            self.update()

    # mouse press event
    def mousePressEvent(self, event) -> None:
        if self._clickable:
            self.on_mouse_pressed(event)

    # mouse move event
    def mouseMoveEvent(self, event) -> None:
        if self._clickable:
            self.on_mouse_moved(event)

    # mouse release event
    def mouseReleaseEvent(self, event) -> None:
        if self._clickable:
            self.on_mouse_released(event)

    # wheel rotate event
    def wheelEvent(self, a0: QtGui.QWheelEvent) -> None:
        if self._clickable:
            self.on_wheel_rotated(a0)
