# touchic
A simple touch based gui for small instruments. Developed using Python and PyQt. The aim was to have a simple lightweight library for integration with single board computer systems. This code has been tested on Raspberry Pi with a 7 in touchscreen. This has also been tested on desktop computer running Linux or Windows.

The package consists of a group of Python classes for 
1. Capturing user inputs through a touchscreen
2. Displaying realtime data and measured quantities

The screenshot below shows basic buttons and labels. The components and their functionality is described below.

<p align="center">
  <img src="https://raw.githubusercontent.com/prosenjit-mdhslab/touchic/main/doc/Screenshot%20from%202021-05-13%2020-28-54.png"/>
</p>

## 1. Text Label (text_label.py)
Unlike conventional text labels, the puropose of the text label is to display process parameters. Hence they are designed for display __name__ and __value__ pair. In the image above the __name__ (*Message*) is shown in the top left. The __value__ (*Hello World*) is shown right. The text label is defined in `ICTextLabel` class. A text label can be created by calling its constructor. The class inherits from the `QWidget`.
```python
lbl = ICTextLabel("Message", "Hello World")
# get the name of the label
print (lbl.name)
# set a new value of the label
lbl.value = str(1.25)
```

### 1.1 Properties
The class exposes several properties to **get** and **set** displayed values, its apperance and behaviour. The follwoing properties are exposed
|Property             |   Description  |
|---------------------|----------------|
|`name` | Name of the parameter displayed on the text label|
|`value` | Value of the parameter|
|`name_text_size` | Font size of the displayed name|
|`name_text_color` | Color of the font used to display the name|
|`value_text_size` | Font size of the displayed value|
|`value_text_color` | Color of the font used to display the value|
|`border_color` | Border color for the widget. This is specified using `QtGui.QColor`|
|`back_colors` | A tupple pair of colors (__light shade__: *QtGui.QColor*, __dark shade__: *QtGui.QColor*). This pair is used to graident render the background of the widget.|

```python
# set new background colors
lbl.back_colors = (QtGui.QColor(200, 200, 200), QtGui.QColor(100, 100, 100)) 
```

## 2. Clock Label (clock_label.py)
This is used to display the time. The clock label is defined by `ICClockLabel`. The class inherits `ICTextLabel`. The `.value` property of the `ICTextLabel` class stores the current time. The displayed time is updated using a timer.
```python
clk_lbl = ICClockLabel("Time")
# get current time
current_time = clk_lbl.value
```

## 3. Basic Button (base_button.py)
Two basic buttons are shown in the figure above. The `ICBaseButton` class inherits the `QWidget` class. The puropse of the class is to capture the click events. The button is created by calling 
```python
# constructor ICBaseButton(name: str, button_id: int)
but = ICBaseButton("Ok", 0)
```

### 3.1 Properties
The following properties are implemented by the class
|Property             |   Description  |
|---------------------|----------------|
|`name`  | The name displayed on the button. This is a *string* datatype. |
|`button_id`  | The *id* of the button. This is an *integer*. The *id* is used to identify in case multiple buttons have the same name. |
|`clickable`  | Defines if the button can be clicked and will emit a clicked signal. This is a *boolean* property. |
|`text_size`  | Font size of the button name |
|`text_colors`  | Color of the font used to display the button name. A tupple of color pairs is used to **set** or **get** the (_enabled_, _disabled_) colors. |
|`button_colors`  | Color pair (__light shade__: *QtGui.QColor*, __dark shade__: *QtGui.QColor*) used to graident render the background of the button. |
|`state`  | The state of the button. The different states of a button are defined in the `ICWidgetState` *Enum*. |

<p align="center">
  <img src="https://raw.githubusercontent.com/prosenjit-mdhslab/touchic/main/doc/Screenshot%20from%202021-05-14%2006-22-04.png"/>
</p>

The different possible states defined in `ICWidgetState` are

|State                |   Description  |
|---------------------|----------------|
| `VisibleEnabled` | The button is visible and enabled. By *default* the button is clickable in this state. However this behaviour can be changed by modifying the `clickable` property. |
| `VisibleDisabled` | The button is visible but disablyed ("grayed"). By *default* the button is not clickable in this state. A disabled button is shown in the image below. |
| `FrameOnly` | Only the frame of the button is visible. The name of the button is not rendered. By *default* the button is clickable in this state. A frame only button is shown in the image below. |
| `Transparent` | The button is rendered using the background color. Hence the button is not visible but occupies the space. By *default* the button is not clickable in this state. |
| `Hidden` | The button is hidden. By *default* the button is not clickable in this state. |

### 3.2 Events
On clicking the button emits __clicked__ event. The clicked event has two formats
1. If the `.button_id` is defined then the raised event passes both `.name` and `.button_id` with the event
2. If the `.button_id` is not defined then the raised event passes `.name` only
```python
# in the user code the event can be captured by connecting to the event
but.clicked.connect(on_ok_click)

# the function to be called in the case of a button click event
@pyqtSlot(str, int)
def on_ok_click(name: str, id: int):
  print("button clicked")

```

## 4. Toggle Button (toggle_button.py)
A toggle button is a state maintaining button. They represent the mechanical swithces. One example is an start-stop switch for any instrument. The toggle button class `ICToggleButton` inherits the `ICBaseButton` class. The toggle button shows a _label_ on the top left. It is used to indicate what type of parameter is being toggled. The main text in the centre changes with the state. There is a LED button to distinguish the two states as shown in the images below.
<p align="center">
  <img src="https://raw.githubusercontent.com/prosenjit-mdhslab/touchic/main/doc/Screenshot%20from%202021-05-14%2006-55-25.png"/>
  <img src="https://raw.githubusercontent.com/prosenjit-mdhslab/touchic/main/doc/Screenshot%20from%202021-05-14%2006-55-34.png"/>
</p>

The toggle button can be created by
```python
# ICToggleButton(label: str, off_text: str, on_text: str, init_state: bool, led_type: ICLEDType)
btn = ICToggleButton("Operation", "Pause", "Resume", False, ICLEDType.ToggleNormal)
```

### 4.1 Properties
The follwoing properties are available to modify the button behaviour
|Property             |   Description  |
|---------------------|----------------|
|`state` | A boolean property to **get** or **set** the current state of the toggle button. |
|`label` | Label displayed on the top left of the button. |
|`on_off_text` | A string tupple of (__on text__: *str*, __off text__: *str*) to be displayed in the button. |
|`led_type` | Used to determine the color of the LED used. This can be used to specify the sevrity level of the toggle button. The different types are specified by the `ICLEDType` _Enum_. LED type gives an easy way of switching LED colors. LED colors can be independently changed as described below. Type can be also used for moudlating behaviour. Available types are <ul><li>_ToggleNormal_</li><li>_AlarmCritical_</li><li>_AlarmNormal_</li><li>_AlarmInformation_</li></ul> |
|`on_off_led_color`  |  A tupple specifying color of the led (__on state__: *QtGui.QColor*, __off state__: *QtGui.QColor*) |
|`label_text_size` | Font size of the label text. |
|`label_text_color` | Color of the label displayed on the button. |
|`led_position` | Position of the LED. It is specified by the `ICLEDPosition` _Enum_. LED can be placed at `.Top`, `.Bottom`, `.Left`, and `Right`.  |

### 4.2 Events
The toggle button emits the `toggled` signal. There are two variants
1. If the _button id_ is define then the emitted signal passes `.state` and `.button_id`
2. If the _button id_ is not defined then the emitted signal passes the `.state` of the toggle button.

## 5. Alarm Widget (alarm_widget.py)
Alarms and error messages are an integral part of any instrument control panel. This widget provides a simple way of showing alarms and error codes. The widget consists of a text which displays the error message with the time at which the alarm was raised. The widget also incorporates a toggle button to acknowledge and silent the alarma as seen in the image below. In the image below, three alarm widgets have been added in the dialog box.
<p align="center">
  <img src="https://raw.githubusercontent.com/prosenjit-mdhslab/touchic/main/doc/Screenshot%20from%202021-05-15%2011-00-34.png"/>
</p>

The alarm widget is created in the activated state
```python
# ICAlarmWidget(alarm_id: int, alarm_message: str, alarm_description: str, led_type: ICLEDType)
alrm1 = ICAlarmWidget(0, "critical alarm", "This is a critical alarm.", ICLEDType.AlarmCritical)
```

### 5.1 Properties
The widget can be manipulated using the following properties exposed by the class
|Property             |   Description  |
|---------------------|----------------|
|`alarm_id` | The id of the alarm. It is an integer. This is not displayed. |
|`alarm_text` | A short descriptive text that is displayed on the widget. |
|`alarm_description` | A more descriptive text that helps the user to resolve the problem. This is displayed in a popup dialog that is shown once the user acknowledges the alarm. The popup dialog allows the user to decide if they want to silenece the alarm or leave it in the active state. |
|`alarm_status` | A readonly property showing the current status of the alarm. The return type is `ICAlarmStatus` _Enum_. The possible values are _Active_, _Acknowledged_, or _Inactive_. |
|`alarm_type` | This is of the `ICLEDType`. Sets the severity level of the alarm. The color of the alarm and the LED is linked to the alarm severity. Changing the alarm severity changes teh colors. The colors can be changed independently as well. |
|`raised_time` | Time at which the alarm was raised. This is readonly property. The return type is datetime. |
|`acknowledged_time` | Time at which the alarm was acknowledged. This is a readonly property. The return type is datetime. |
|`reactivation_time` | After an alarm is acknowledged it becomes inactive a specified period. The time after which the alarm can be reactivated is given by this parameter. |
|`message_text_size` | Font size of the message text. |
|`message_font_color` | Color of the message font. |
|`message_back_color` | Background color of the message text. |
|`acknowledge_button` | Toggle button used for acknowledging the alarm. |

### 5.2 Events
The widget emits the `acknowledged` event, when the alarm is acknowledged by the user. The event passes the __alarm id__ as its parameter.

## 6. Linear Gauge (linear_gauge.py)
A linear gauge is used to graphically display changing values of parameters. In the animation below, we show its use for tracking pressure. The `ICLinearGauge` allows definiation of two alarm limits, an upper limit and a lower limit. It also allows tracking of cycle maximum and cycle minimum. This is again a compound widget, which consists of the 
+ gauge bar defined in the class `ICGaugeBar` 
+ a title label at the top, and
+ a value label at the bottom

<p align="center">
  <img src="https://raw.githubusercontent.com/prosenjit-mdhslab/touchic/main/doc/Peek%202021-05-15%2012-52.gif"/>
</p>

The code below shows creation and manipulation of a linear gauge

```python
# ICLinearGauge(name: str, unit: str, min_val: float, max_val: float, display_steps: int)
# min_val is the minimum value displayed on the bar
# max_val is the maximum value displayed on the bar
gauge = ICLinearGauge("Pressure", "Pa", 0, 120, 6)

# gauge.gauge_bar is of type ICGaugeBar and implements the gauge bar 
gauge.gauge_bar.lower_alarm = ("low", 20)
gauge.gauge_bar.upper_alarm = ("high", 100)

# set the value of the gauge bar
gauge.value = 40

# start cycle max and min tracking 
gauge.gauge_bar.start_max_tracking()
gauge.gauge_bar.start_min_tracking()
```

### 6.1 Properties (ICLinearGauge)
The following properties are avaiable from the `ICLinearGauge` object
|Property             |   Description  |
|---------------------|----------------|
|`name`  | Specifies the name of the parameter that is is being displayed. |
|`value` | Current value of the parameter. This is used to draw the gauge bar. This property will automatically update the value in the `.gauge_bar`. |
|`unit`  | Unit of the parameter being displayed. |
|`title_size` | Font size for the parameter name displayed at the top. |
|`title_text_color` | Color of the font used to show the name of the parameter. |
|`value_size`  | Font size for displaying the current value at the bottom. |
|`value_text_color` | Color of the text for displaying the current value. |
|`alarm_colors`  | A tupple of color pair (__background color__: *QtGui.QColor*, __text color__: *QtGui.QColor*) to be used to display the value when the current value is not with the specified lower and upper limit. |
|`unit_size` | Font size of the unit text. |

### 6.2 Properties (ICGaugeBar)
The `ICLinearGauge` object initiates a `ICGaugeBar` object to represent the gauge bar. The following properties are implemented and can be accessed through the `.gauge_bar` member. The `ICGaugeBar` object can also be used independently in a GUI. 
|Property             |   Description  |
|---------------------|----------------|
|`gauge_range_min`    | Minimum value to be shown in the gauge bar. |
|`gauge_range_max`    | Maximum value to be shown in the gauge bar. |
|`gauge_value`        | Current value used to determine the level shown by the gauge bar. |
|`upper_alarm`        | A tupple of (__name__: _str_, __value__: _float_) pair to define the upper alarm level. |
|`lower_alarm`        | A tupple of (__name__: _str_, __value__: _float_) pair to define the lower alarm level. |
|`alarm_level_text_size`  | Size of the font used to display the alarm level description text. |
|`alarm_level_text_color` | Color of the font used to render the alarm level text. |
|`num_steps`          | Number of steps in the scale (ruler) of the gauge bar. |
|`tick_text_size`     | Font size of the text used to display the scale (y-axis) text. |
|`tick_color`         | Color of the font used to display the scale (y-axis) text. |
|`back_colors`        | Color pair (__light shade__: _QtGui.QColor_, __dark shade__: _QtGui.QColor_) used to render the gauge background. |
|`gauge_color_normal` | Color pair (__light shade__: _QtGui.QColor_, __dark shade__: _QtGui.QColor_) used to render the gauge bar when the current value is between the specified lower and upper limit. |
|`gauge_color_alarm`  | Color pair (__light shade__: _QtGui.QColor_, __dark shade__: _QtGui.QColor_) used to render the gauge bar when the current value is outside the specified lower and upper limit (alarm condition). |

### 6.3 Functions (ICGaugeBar)
Min and max tracking are enabled through fuctions. To track cycle maximum, every cycle the tracking can be reset to restart the tracking.

|Function             |   Description  |
|---------------------|----------------|
|`start_max_tracking()` | The gauge bar can track the max level observed. This function needs to be called to enable the max tracking. |
|`reset_max_tracking()` | This function resets the tracked max value to the current value. |
|`stop_max_tracking()`  | Stop tracking the max level. |
|`start_min_tracking()` | Start tracing the min level. |
|`reset_min_tracking()` | Reset the tracked min value to the current value. |
|`stop_min_tracking()`  | Stop tracking the min level. |

### 6.4 Events (ICGaugeBar)
A value change event is emitted by this class. `changed` event passes the current value.




