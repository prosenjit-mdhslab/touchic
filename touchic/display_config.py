# -*- coding: utf-8 -*-
"""
Created on Sun Apr 19 17:53:58 2020

@author: prosenjit

This is the base class for the default constants (colors, font size, etc.) used for
rendering the controls.  These can be overridden by changing them at the object level.

TODO: Implement local color class
"""
from PyQt6 import QtGui


class ICDisplayConfig:
    # Overall background
    BackgroundColor = QtGui.QColor(38, 50, 56)
    InFocusColor = QtGui.QColor(255, 87, 34)

    # Tab settings
    TabWidth = "100"
    TabHeight = "25"
    TabFontSize = "12"
    
    # Text label configurations
    TextLabelWidth = 200
    TextLabelHeight = 65
    # background color
    LabelBackLightColor = QtGui.QColor(23, 32, 42)
    LabelBackDarkColor = QtGui.QColor(3, 12, 22)
    # border color
    LabelBorderColor = QtGui.QColor(92, 107, 192)
    # text size
    LabelNameSize = 12
    LabelValueSize = 20
    # text color
    LabelNameColor = QtGui.QColor(176, 190, 197)
    LabelValueColor = QtGui.QColor(118, 255, 0)

    # Clock label configurations
    ClockLabelSize = 17
    ClockLabelColor = QtGui.QColor(249, 231, 159)

    # Configuration for buttons
    ButtonTextSize = 20
    ButtonTextColorEnabled = QtGui.QColor(38, 50, 56)
    ButtonTextColorDisabled = QtGui.QColor(117, 117, 117)
    # Raised
    ButtonColorLightRaised = QtGui.QColor(238, 238, 238)
    ButtonColorDarkRaised = QtGui.QColor(97, 97, 97)
    # Depressed
    ButtonColorLightDepressed = QtGui.QColor(97, 97, 97)
    ButtonColorDarkDepressed = QtGui.QColor(189, 189, 189)

    # Button suggested width and height
    ButtonMinWidth = 120
    ButtonMinHeight = 60
    
    # Param button specialisation
    ParamButtonMinHeight = 110
    ParamDisplayTextSize = 18
    ParamButtonLabelTextSize = 12
    ParamButtonLabelColor = QtGui.QColor("black")
    
    # Radio Button
    RadioButtonHeight = 50
    RadioButtonWidth = 150
    RadioBoxBorderColor = QtGui.QColor(236, 239, 241)
    RadioBoxFillColor = QtGui.QColor(144, 164, 174)
    RadioBoxTextColor = QtGui.QColor(255, 241, 118)

    ###############################################################
    # Linear Slide
    ###############################################################
    LinearSlideWidth = 400
    LinearSlideHeight = 150
    # slide background color
    LinearSlideBoxColorLight = QtGui.QColor(238, 238, 238)
    LinearSlideBoxColorDark = QtGui.QColor(157, 157, 157)
    # color of the groove
    LinearSlideColorLight = QtGui.QColor(117, 117, 117)
    LinearSlideColorDark = QtGui.QColor(33, 33, 33)
    # color of the ruler
    LinearSlideRulerColorDark = QtGui.QColor(1, 87, 155)
    LinearSlideRulerColorLight = QtGui.QColor(79, 195, 247)
    # color of the ruler during alarm
    LinearSlideRulerAlarmColorDark = QtGui.QColor(136, 14, 79)
    LinearSlideRulerAlarmColorLight = QtGui.QColor(248, 187, 208)
    # color of the knob
    LinearSlideKnobLight = QtGui.QColor(176, 190, 197)
    LinearSlideKnobDark = QtGui.QColor(55, 71, 79)

    ###############################################################
    # General Text Sizes and Colors
    ###############################################################
    LabelTextSize = 14
    GeneralTextSize = 12
    UnitTextSize = 10
    HeaderTextColor = QtGui.QColor(129, 212, 250)
    ValueTextColor = QtGui.QColor(0, 255, 153)
    ValueTextColorObj = QtGui.QColor(0, 255, 153)
    ErrorTextBackColor = QtGui.QColor(176, 58, 46)
    ErrorTextColor = QtGui.QColor(249, 231, 159)

    ###############################################################
    # Linear Gauge
    ###############################################################
    # Horizontal dimensions
    LinearGaugeHorizontalWidth = 350
    LinearGaugeHorizontalMaxHeight = 175
    # Vertical dimensions
    LinearGaugeVerticalHeight = 350
    LinearGaugeVerticalMaxWidth = 150

    # Gauge Width in Pixels
    LinearGaugeWidth = 40

    # Default colors for the Gauge
    # Gauge container
    LinearGaugeBoxColorLight = QtGui.QColor(117, 117, 117)
    LinearGaugeBoxColorDark = QtGui.QColor(33, 33, 33)
    # Gauge bar normal
    LinearGaugeNormalLight = QtGui.QColor(204, 255, 144)
    LinearGaugeNormalDark = QtGui.QColor(51, 105, 30)
    # Gauge bar Error
    LinearGaugeErrorLight = QtGui.QColor(248, 187, 208)
    LinearGaugeErrorDark = QtGui.QColor(136, 14, 79)
    LinearGaugeRulerColor = QtGui.QColor(249, 231, 159)
    # limits
    LinearGaugeLimitsColor = QtGui.QColor(255, 87, 34)
    LinearGaugeMinMaxColor = QtGui.QColor(255, 241, 118)
    LinearGaugeTargetColor = QtGui.QColor(225, 190, 231)

    ###############################################################
    # Plots
    ###############################################################
    PlotWidth = 450
    PlotHeight = 150
    PlotBufferSpace = 0.1

    # default colors
    DefaultPlotFaceColor = QtGui.QColor('#1C2833')
    DefaultPlotSelectedColor = QtGui.QColor('#FF3333')

    # marker colors
    DefaultPlotYMarkerColor = QtGui.QColor('#D98880')
    DefaultPlotXMarkerColor = QtGui.QColor('#DDCC36')

    ###############################################################
    # Toggle Button and LEDs
    ###############################################################
    # Toggle button
    ToggleButtonMinHeight = 80

    # LED Colors
    ToggleOffColor = QtGui.QColor(0, 0, 31)
    ToggleOnColor = QtGui.QColor(0, 0, 204)
    AlarmCriticalOffColor = QtGui.QColor(31, 0, 0)
    AlarmCriticalOnColor = QtGui.QColor(204, 0, 0)
    AlarmNormalOffColor = QtGui.QColor(31, 17, 0)
    AlarmNormalOnColor = QtGui.QColor(204, 102, 0)
    AlarmInformationOffColor = QtGui.QColor(0, 31, 17)
    AlarmInformationOnColor = QtGui.QColor(0, 204, 102)

    ###############################################################
    # Alphanumeric Input
    ###############################################################
    DataInputNumericWidth = 350
    DataInputNumericHeight = 390

    DataInputAlphabetWidth = 650
    DataInputAlphabetHeight = 260

    ###############################################################
    # Rotary Gauge
    ###############################################################
    RotaryGaugeHeight = 150
    RotaryGaugeWidth = 150

    # limits
    RotaryGaugeLimitsColor = QtGui.QColor(255, 125, 125)
    RotaryGaugeMinMaxColor = QtGui.QColor(255, 241, 118)
    RotaryGaugeTargetColor = QtGui.QColor(225, 190, 231)

    @staticmethod
    def QtColorToSting(clr: QtGui.QColor):
        return "rgb({0}, {1}, {2})".format(clr.red(), clr.green(), clr.blue())
