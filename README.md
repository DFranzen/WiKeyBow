# WiKeyBow
A python-fireware for the pimoroni KeyBow 12-Key Keyboard based on Raspberry Pi OS

## Features
* Wireless connections: The Keyboard only needs power, no USB-dataconnection required
* Independent button configuration: Each button can controll a different device
* http calls or bash commands: Each button can execute a different bash command. Additionally easy Configuration for http calls are available
* State indication via LED: Each device controlled by a Button tracks the state of the device (ON or OFF) and indicates the state with the color (fully configurable)
* Automatic state update for each buttons: The state indicator is automatically updated to account for cahnges from different controls

## Anti-Features
* Full Keyboard animations: Each Button only affects the color of it's own LED. There are no keyboard-wide animations
* USB-Keyboard-compatibility: The Keyboard does not transmit any control via a USB-Connection, even if it is pluged into a computer

## Feature Ideas
* Multi-press support
* Layer-switching
* Read configuration from JSON

## Installation
* Setup the build-in raspberry with raspberry OS. (Tested on Version 2021-01-11, python3 required)
* Install requirements: 
  * `sudo apt install -y python3-pip python3-rpi.gpio`
  * `sudo pip3 install apa102-pi`
* Enable SPI `sudo raspi-config` -> Interface Options -> SPI 
* Download keybow.py
* enable autostart
  * Create service script `/etc/systemd/system/WiKiBo.service`
  * insert the following code (with PATH/TO/SCRIPT adjusted)
  ```
  [Unit]
  Description=KeyBoard Listener for Button Presses and state changes
  After=network-online.target

  [Service]
  Type=simple
  User=pi
  Group=pi
  ExecStart=/usr/bin/python3 PATH/TO/SCRIPT/WiKeyBow.py

  [Install]
  WantedBy=network-online.target
  ```
  * reload deamon `systemctl daemon-reload`
  * activate using `sudo systemctl enable WiKeyBow`
* It is also needed to setup the devices, to be controlled, with a static IP.

## Configuration

For each button, three properties need to be configured: Color, State-update and KeyPress-Action. All these configurations are specified at the top of the script.
### Color
The color for each button can be configured in either of two ways:
#### Constant Color
If the property "color" is set to a Hex-Representation of an RGB-color this color is used as constant color for the button.
Example:
` "color": 0xFF00FF`
#### State-dependent Color
If the properties "colorON" and "colorOFF" are set to HEX-representations of RGB-colors, one of these colors is set to the button, depending of the current state of the controlled device ("colorON", if the device is switched on, "colorOFF" otherwise)
Example:
```
  "colorON": 0x00FF00,
  "colorOFF": 0xFF0000,
```
When specifying the color state-dependent, also a `color` can be given without state. This color is used in case the state cannot be determined. If no such default color is given, 0x000000 (LED switched off) is used as default color

### State-update
If the button is state-dependent (either for the color or for the button-action), a command needs to be specified to evaluate the state of the device. This is done in the property `state_req`. It can be either a http-GET call or a bash-command. 
Additionally a value `stateON` needs to be specified as an expected value for the ON state. To evaluate the state of a device, the command is executed and then compared to the value `stateON`.
Example:
```
        "state_req": {
            "url": "http://...",
            "stateON": '{"POWER":"ON"}',
        },
```
or 
```
        "state_req": {
            "bash": "echo ON"
            "stateON": 'ON',
        },

```


In some cases (e.g. Phillips Hue) the response from the device is too long to compare as a whole. For this case, the path to be compared can be specified as a list in the property `path`. If it is specified, WiKeyBow converts the response from the given `url` into json and follows the path. The resulting sub-json is then converted back into a string and compared with the given `stateON`.
Example:
```
        "state_req": {
            "url": "http://192.168.1.100/api/user/lights/23",
            "path": ["state","on"],
            "stateON": 'True'
        },
```
In this example, all parts of the response except `{"state": {"on": " ... "}}` are ignored.

### Button-action
Finally the action for each button press needs to be specified in the block `keydown`. It contains `url`, `header` and `body`. The values `url` and `body` can either be specified constantly as `body` / `url` or state-dependent as `bodyON` / `urlON` (values in case the device is currently ON) and `bodyOFF` / `urlOFF` (value in case the device id currently OFF). All combinations are possible. If a dependent value is specified, the state of the devce is evaluated first. If the result is ON, a value with suffix ON will be used, otherwise the value with the suffix OFF is used. 
Example:
```
        "keydown": {
            "url": "http://192.168.0.100/api/",
            "header": {"content-type": "application/json"},
            "body": "{}"
        }
```
or 
```
        "keydown": {
            "url": "http://192.168.0.100/api/",
            "header": {"content-type": "application/json"},
            "bodyON": "{\"on\":false}"
            "bodyOFF": "{\"on\":true}"
        }
```

or 
```
        "keydown": {
            "urlON": "http://192.168.0.100/cm?cmnd=Power%20Off",
            "urlOFF": "http://192.168.1.100/cm?cmnd=Power%20On",
            "header": {"content-type": "application/json"},
            "body": "{}"
        }
```

Alternatively the button-action can be specified as a bash command with the propterty `bash`. It is executed in a bash shell and the output is ignored. Again this property can be split into `bashON` and `bashOFF`, one of which will be executed depending on the current state of the device.
Example:
```
        "keydown": {
            "bashON": "python3 /home/pi/tplink_smartplug.py -t 192.168.1.100 -c off",
            "bashOFF": "python3 /home/pi/tplink_smartplug.py -t 192.168.1.100 -c on"
        }
```

## Examples
### TP-Link kasa
To control a Kasa-device, the auxiliary script tplink-smartplug.py (https://github.com/softScheck/tplink-smartplug) is used. The following example shows how to use it in WiKeyBow. The script needs to be played in the home-driectory, or the path in state_req and keydown needs to be adjusted. Also adjust the IP of the device as needed.

```
    "key_1_in_row_2": {
        "name": "Kasa Lamp",
        "state_req": {
            "bash": "python3 /home/pi/tplink_smartplug.py -t 192.168.1.100 -c info | grep -oE .relay_state.:[0-9]| grep -o [0-9]\
",
            "stateON": '1',
        },
        "colorON" : 0x00FF00,
        "colorOFF": 0xFF0000,
        "keydown": {
            "bashON": "python3 /home/pi/tplink_smartplug.py -t 192.168.1.100 -c off",
            "bashOFF": "python3 /home/pi/tplink_smartplug.py -t 192.168.1.100 -c on"
        }

    },
```

### Tasmota
Here is a full example configuration for a button controlling a Tasmota device. The IP of the Tasmota-device needs to be adjusted.
```
    "key_1_in_row_4": {
        "name": "Tasmota Lamp",
        "state_req": {
            "url": "http://192.168.0.100/cm?cmnd=status/power",
            "stateON": '{"POWER":"ON"}',
        },
        "colorON" : 0x00FF00,
        "colorOFF": 0xFF0000,
        "keydown": {
            "urlON": "http://192.168.0.100/cm?cmnd=Power%20Off",
            "urlOFF": "http://192.168.0.100/cm?cmnd=Power%20On",
            "header": {"content-type": "application/json"},
            "body": "{}"
        }

    }
```

### Philips Hue
(This setup is in part borrowed from Kiwi (https://github.com/mrusme/kiwi)
Find the IP address of your Philips Hue Bridge on your network and create a dedicated user:

```
curl -X "POST" "http://YOUR-HUE-BRIDGE-IP-HERE/api" \
     -H 'Content-Type: application/json; charset=utf-8' \
     -d $'{
          "devicetype": "WiKeyBow#wikeybow"
        }'
```

This request will return an auto-generated username. With this you can then check all your connected lights:

```
curl "http://YOUR-HUE-BRIDGE-IP-HERE/api/YOUR-GENERATED-USERNAME-HERE/lights" \
     -H 'Content-Type: application/json; charset=utf-8' \
     -d $'{}'
```

After you've identified the light you'd like to turn on/off, note down its ID and configure the button as follows:


```
    "key_1_in_row_4": {
        "name": "Philips HUE Lamp",
        "state_req": {
            "url": "http://YOUR-HUE-BRIDGE-IP-HERE/api/YOUR-GENERATED-USERNAME-HERE/lights/ID",
            "path": ["state","on"],
            "stateON": 'True'
        },
        "colorON" : 0x00FF00,
        "colorOFF": 0xFF0000,
        "keydown": {
            "url": "http://YOUR-HUE-BRIDGE-IP-HERE/api/YOUR-GENERATED-USERNAME-HERE/lights/ID",
            "header": {"content-type": "application/json"},
            "bodyON": "{\"on\":false}",
            "bodyOFF": "{\"on\":true}"
        }
    },
```

### Linux Computer: XDoTool via SSH
Most of the features, which the official KeyBow firmware accomplishes via a USB cable, can be done wirelessly with this implementation on a linux computer. However it takes a bit of setup:
* Install `xdotool` on the Linux computer: `sudo apt -y install xdotool`
* Enable ssh server on the Linux computer: `sudo apt install openssh-server`
* Enable passwordless access on the raspberry pi: 
```
ssh-keygen
ssh-copy-id <usernameOfComputer>@<ipOfComputer>
```
With this setup the following example sends the mute-mic button (and shows the mute status of the default mic):
```
    "key_2_in_row_4": {
        "name": "Mic Mute",
        "colorON": 0xff4000,
        "colorOFF": 0x40ff00,
        "state_req": {"state_req": {
            "bash": "ssh <usernameOfComputer@<ipOfComputer> \"pactl list sources | grep -A 10 \$(pactl info | grep 'Default Source:' | cut -f3 -d' ') | grep 'Mute'| sed -e 's/^[[:space:]]*//'\"",
            "stateON": "Mute: yes"
        },
        "keydown": {
            "bash": "ssh <usernameOfComputer@<ipOfComputer> \"export DISPLAY=:0; xdotool key XF86AudioMicMute\""
        }
        
    },
```

## Comparison to other KeyBow firmwares

### Official KeyBow firmware
The official KeyBow firmware (https://github.com/pimoroni/keybow-firmware) tries to achieve a different goal. Rather than a wireless Keyboard, which can control multiple devices, the official firmware implements a wired keyboard, which can control one device.
#### Advantages WiKeyBow
* WiKeyBow can control multiple devices at once
* Control-actions are more flexible
* WiKeyBow does not need to be pluged into a computer
* WiKeyBow can be modified on the Raspberry Pi without additional development tools and wirelessly
#### Advantages official firmware
* no additional setup required to send simple keypresses
* Boot-time is significantly quicker
* smaller image size

### XeBow
The nerves-based firmware (https://github.com/ElixirSeattle/xebow) implements a USB-firmware in a joined framework with similar keyboards. Like the official KeyBow firmware it tries to achieve a different goal than WiKeyBow

### KiWi
Kiwi (https://github.com/mrusme/kiwi) is another attmept to make the KeyBow wireless. Rather than based on Raspberry OS, it is based on the microcontroller OS Nerves. Button-actions are limited to http requests and the LED-Matrix can only be updated all-at-once.
#### Advantages WiKeyBow
* Control each LED individually (without changing or switching of the other LEDs)
* Bash command as button-actions in addition to http calls
* WiKeyBow can be modified on the Raspberry Pi without additional development tools
* [possible subjective] KiWi is somehow blocking DHCP-Server on router while running, WiKeyBow has no inteference.
#### Advantages KiWi
* slightly quicker start-up time
* Full keyboard animations
* smaller Image-size
