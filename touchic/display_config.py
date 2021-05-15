# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 17:53:58 2020

@author: prosenjit

This is the base class for the default constants (colors, font size, etc.) used for
rendering the controls.  These can be overridden by changing them at the object level.
"""
from PyQt5 import QtGui


class ICDisplayConfig:
    # Overall background
    BackgroundColor = QtGui.QColor(28, 40, 51)
    
    # Tab settings
    TabWidth = "100"
    TabHeight = "25"
    TabFontSize = "12"
    
    # Text label configurations
    TextLabelWidth = 200
    TextLabelHeight = 65
    LabelBackLightColor = QtGui.QColor(23, 32, 42)
    LabelBackDarkColor = QtGui.QColor(3, 12, 22) 
    LabelBorderColor = QtGui.QColor(92, 107, 192)
    LabelNameSize = 15
    LabelValueSize = 20
    LabelNameColor = QtGui.QColor(129, 212, 250)
    LabelValueColor = QtGui.QColor(0, 255, 0)

    # Clock label configurations
    ClockLabelSize = 17
    ClockLabelColor = QtGui.QColor(249, 231, 159)

    # Configuration for buttons
    ButtonTextSize = 20
    ButtonTextColorEnabled = QtGui.QColor(100, 30, 22)
    ButtonTextColorDisabled = QtGui.QColor(100, 100, 100)
    ButtonColorLight = QtGui.QColor(174, 214, 241)
    ButtonColorDark = QtGui.QColor(27, 79, 114)
    
    # Button suggested width and height
    ButtonMinWidth = 120
    ButtonMinHeight = 60
    
    # Param button specialisation
    ParamButtonMinHeight = 80
    ParamDisplayTextSize = 20
    ParamButtonLabelTextSize = 15
    ParamButtonLabelColor = QtGui.QColor("black")
    
    # Radio Button
    RadioButtonSize = 50
    RadioBoxColor = QtGui.QColor(0, 255, 153)
    
    # Toggle button
    ToggleButtonMinHeight = 80
    ToggleOnColor = QtGui.QColor(50, 255, 50)
    ToggleOffColor = QtGui.QColor(0, 32, 0)
    
    # Linear Slide
    LinearSlideWidth = 600
    LinearSlideHeight = 120
    LinearSlideBoxColor = QtGui.QColor("lightGray")
    LinearSlideColorLight = QtGui.QColor(128, 128, 128)
    LinearSlideColorDark = QtGui.QColor(48, 48, 48)
    LinearSlideRulerColorDark = QtGui.QColor(1, 87, 155)
    LinearSlideRulerColorLight = QtGui.QColor(79, 195, 247)
    LinearSLideKnobLight = QtGui.QColor(118, 215, 196)
    LinearSlideKnobDark = QtGui.QColor(17, 120, 100)
    
    # General Text Sizes and Colors
    LabelTextSize = 14
    GeneralTextSize = 12
    UnitTextSize = 10
    HeaderTextColor = QtGui.QColor(129, 212, 250)
    ValueTextColor = QtGui.QColor(0, 255, 153)
    ValueTextColorObj = QtGui.QColor(0, 255, 153)
    ErrorTextBackColor = QtGui.QColor(176, 58, 46)
    ErrorTextColor = QtGui.QColor(249, 231, 159)
    
    # Linear Gauge
    LinearGaugeWidth = 150
    LinearGuageHeight = 300
    LinearGaugeBoxColorLight = QtGui.QColor(128, 128, 128)
    LinearGaugeBoxColorDark = QtGui.QColor(48, 48, 48)
    LinearGaugeNormalLight = QtGui.QColor(220, 237, 200)
    LinearGaugeNormalDark = QtGui.QColor(51, 105, 30)
    LinearGaugeErrorLight = QtGui.QColor(248, 187, 208)
    LinearGaugeErrorDark = QtGui.QColor(136, 14, 79)
    LinearGaugeRulerColor = QtGui.QColor(249, 231, 159)
    LinearGaugeLimitsColor = QtGui.QColor(255, 87, 34)
    
    # Plots
    PlotWidth = 450
    PlotHeight = 120
    PlotBufferSpace = 0.1

    # Alarms
    AlarmCriticalOffColor = QtGui.QColor(32, 5, 5)
    AlarmCriticalOnColor = QtGui.QColor(255, 25, 25)
    AlarmNormalOffColor = QtGui.QColor(100, 34, 0) 
    AlarmNormalOnColor = QtGui.QColor(220, 118, 51)
    AlarmInformationOffColor = QtGui.QColor(4, 88, 71)
    AlarmInformationOnColor = QtGui.QColor(72, 201, 176)


    @staticmethod
    def QtColorToSting(clr: QtGui.QColor):
        return "rgb({0}, {1}, {2})".format(clr.red(), clr.green(), clr.blue())
