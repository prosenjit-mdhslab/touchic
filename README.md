# touchic
A simple touch based gui for small instruments. Developed using Python and PyQt. The aim was to have a simple lightweight library for integration with single board computer systems. This code has been tested on Raspberry Pi with a 7 in touchscreen. This has also been tested on desktop computer running Linux or Windows.

The package consists of a group of Python classes for 
1. Capturing user inputs through a touchscreen
2. Displaying realtime data and measured quantities

The screenshot below shows basic buttons and labels. The components and their functionality is described below.

<p align="center">
  <img src="https://raw.githubusercontent.com/prosenjit-mdhslab/touchic/main/doc/Screenshot%20from%202021-05-13%2020-28-54.png"/>
</p>

## 1. Text Label 
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
1. `name`: name of the parameter displayed on the text label
2. `value`: value of the parameter
3. `name_text_size`: font size of the displayed name
4. `name_text_color`: color of the font used to display the name
5. `value_text_size`: font size of the displayed value
6. `value_text_color`: color of the font used to display the value
7. `border_color`: border color for the widget. This is specified using `QtGui.QColor`
8. `back_colors`: a tupple pair of colors (_light shade_, _dark shade_). This pair is used to graident render the background of the widget.
```python
# set new background colors
lbl.back_colors = (QtGui.QColor(200, 200, 200), QtGui.QColor(100, 100, 100)) 
```

## 2. Clock Label
This is used to display the time. The clock label is defined by `ICClockLabel`. The class inherits `ICTextLabel`. The `.value` property of the `ICTextLabel` class stores the current time. The displayed time is updated using a timer.
```python
clk_lbl = ICClockLabel("Time")
# get current time
current_time = clk_lbl.value
```

## 3. Basic Button
Two basic buttons are shown in the figure above. The `ICBaseButton` class inherits the `QWidget` class. The puropse of the class is to capture the click events. The button is created by calling 
```python
# constructor ICBaseButton(name: str, button_id: int)
but = ICBaseButton("Ok", 0)
```

### 3.1 Properties
The following properties are implemented by the class
1. `name`: the name displayed on the button. This is a *string* datatype.
2. `button_id`: the *id* of the button. This is an *integer*. The *id* is used to identify in case multiple buttons have the same name.
3. `clickable`: defines if the button will emit a clicked signal. This is a *boolean* property.
4. `state`: the state of the button. The different states of a button are defined in the `ICWidgetState` *Enum*. The different possible states are
+ `VisibleEnabled` --> The button is visible and enabled. By *default* the button is clickable in this state. However this behaviour can be changed by modifying the `clickable` property.
+ `VisibleDisabled` --> The button is visible but disablyed ("grayed"). By *default* the button is not clickable in this state. A disabled button is shown in the image below.
+ `FrameOnly` --> Only the frame of the button is visible. The name of the button is not rendered. By *default* the button is clickable in this state. A frame only button is shown in the image below.
+ `Transparent` --> The button is rendered using the background color. Hence the button is not visible but occupies the space. By *default* the button is not clickable in this state.
+ `Hidden` --> The button is hidden. By *default* the button is not clickable in this state.
<p align="center">
  <img src="https://raw.githubusercontent.com/prosenjit-mdhslab/touchic/main/doc/Screenshot%20from%202021-05-14%2006-22-04.png"/>
</p>

5. `text_size`: font size of the button name
6. `text_colors`: color of the font used to display the button name. A tupple of color pairs is used to **set** or **get** the (_enabled_, _disabled_) colors. 
7. `button_colors`: color pair (_light shade_, _dark shade_) used to graident render the background of the button

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

## 4. Toggle Button
A toggle button is a state maintaining button. They represent the mechanical swithces. One example is an start-stop switch for any instrument. The toggle button class `ICToggleButton` inherits the `ICBaseButton` class. The toggle button shows a _label_ on the top left. It is used to indicate what type of parameter is being toggled. The main text in the centre changes with the state. There is a LED button to distinguish the two states as shown in the images below.
<p align="center">
  <img src="https://raw.githubusercontent.com/prosenjit-mdhslab/touchic/main/doc/Screenshot%20from%202021-05-14%2006-55-25.png"/>
  <img src="https://raw.githubusercontent.com/prosenjit-mdhslab/touchic/main/doc/Screenshot%20from%202021-05-14%2006-55-34.png"/>
</p>

The toggle button can be created by
```python
# ICToggleButton(label: str, off_text: str, on_text: str, init_state: bool, led_type: ICToggleType)
btn = ICToggleButton("Operation", "Pause", "Resume", False, ICToggleType.ToggleNormal)
```

### 4.1 Properties
The follwoing properties are available to modify the button behaviour
1. `state`: a boolean property to **get** or **set** the current state of the toggle button
2. `label`: the label displayed on the top left of the button
3. `on_off_text`: a string tupple of (_on text_, _off text_) to be displayed in the button
4. `type`: used determine the color of the LED used. This can be used to specify the sevrity level of the toggle button. The different types are specified by the `ICToggleType` _Enum_. Toggle type gives an easy way of switching LED colors. LED colors can be independently changed as described below. Type can be also used for moudlating behaviour. Available types are
+ _ToggleNormal_
+ _AlarmCritical_
+ _AlarmNormal_
+ _AlarmInformation_
5. `on_off_led_color`: a tupple specifying color of the led (_on state_: `QtGui.QColor`, _off state_: `QtGui.QColor`) 
6. `label_text_size`: font size of the label text 
7. `label_text_color`: color of the label displayed on the button
8. `led_position`: position of the LED. It is specified by the `ICLEDPosition` _Enum_. LED can be placed at `.Top`, `.Bottom`, `.Left`, and `Right`.  

### 4.2 Events
The toggle button emits the `toggled` signal. There are two variants
1. If the _button id_ is define then the emitted signal passes `.state` and `.button_id`
2. If the _button id_ is not defined then the emitted signal passes the `.state` of the toggle button.

