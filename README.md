# WiKeyBow
12-Button fully programmable wireless Keyboard Firmware

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

## Configuration

## Examples
### TP-Link kasa

### Tasmota

## Comparison to other KeyBow firmwares

### Official KeyBow firmware
The official KeyBow firmware (https://github.com/pimoroni/keybow-firmware) tries to achieve a different goal. Rather than a wireless Keyboard, which can control multiple devices, the official firmware implements a wired keyboard, which can control one device.
#### Advantages WiKeyBow
* WiKeyBow can control multiple devices at once
* Control-actions are more flexible
* WiKeyBow does not need to be pluged into a computer
#### Advantages official firmware
* no additional setup required to send simple keypresses
* Boot-time is significantly quicker
* smaller image size

### KiWi
Kiwi (https://github.com/mrusme/kiwi) is another attmept to make the KeyBow wireless. Rather than based on Raspberry OS, it is based on the microcontroller OS Nerves. Button-actions are limited to http requests and the LED-Matrix can only be updated all-at-once.
#### Advantages WiKeyBow
* Control each LED individually (without changing or switching of the other LEDs)
* Bash command as button-actions in addition to http calls
* [possible subjective] DHCP-Server not available, while KiWi is running
#### Advantages KiWi
* slightly quicker start-up time
* Full keyboard animations
* smaller Image-size
