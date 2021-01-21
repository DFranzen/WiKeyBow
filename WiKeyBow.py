#!/usr/bin/python3

from apa102_pi.driver import apa102
import RPi.GPIO as GPIO

import requests
import subprocess
import threading
from time import sleep

keyNames = ["key_1_in_row_1", "key_1_in_row_2","key_1_in_row_3","key_1_in_row_4",
"key_2_in_row_1", "key_2_in_row_2","key_2_in_row_3","key_2_in_row_4",
"key_3_in_row_1", "key_3_in_row_2","key_3_in_row_3","key_3_in_row_4"]

pins = [20,6,22,17,16,12,24,27,26,13,5,23]

layer1 = {
    "key_1_in_row_1": {
        "name":  "Lamp"
        "color": 0x1eff1e,
        "colorOFF": 0xFF0000,
        "colorON": 0x00FF00,
        "state_req": {
            "bash": "echo ON"
            "url": "http://...",
            "path": ["prop1", "prop2"],
            "stateON": 'ON'
        },
        "keydown": {
            "layer": 0,
            "bash": "echo ON",
            "bashON": "echo ON",
            "bashOFF": "echo ON",
            "url": "http://...",
            "urlON": "http://...",
            "urlOFF": "http://...",
            "header": {"content-type": "application/json"},
            "body": "{\"on\":false}",
            "bodyON": "{\"on\":false}",
            "bodyOFF": "{\"on\":true}"
        }
    },
    "key_2_in_row_1": {},
    "key_3_in_row_1": {},
    "key_1_in_row_2": {},
    "key_2_in_row_2": {},
    "key_3_in_row_2": {},
    "key_1_in_row_3": {},
    "key_2_in_row_3": {},
    "key_3_in_row_3": {},
    "key_1_in_row_4": {},
    "key_2_in_row_4": {},
    "key_3_in_row_4": {}
}

layer2 = {
    "key_1_in_row_1": {
        "name":  "Lamp"
        "color": 0x1eff1e,
        "colorOFF": 0xFF0000,
        "colorON": 0x00FF00,
        "state_req": {
            "bash": "echo ON"
            "url": "http://...",
            "path": ["prop1", "prop2"],
            "stateON": 'ON'
        },
        "keydown": {
            "bash": "echo ON",
            "bashON": "echo ON",
            "bashOFF": "echo ON",
            "url": "http://...",
            "urlON": "http://...",
            "urlOFF": "http://...",
            "header": {"content-type": "application/json"},
            "body": "{\"on\":false}",
            "bodyON": "{\"on\":false}",
            "bodyOFF": "{\"on\":true}"
        }
    },
    "key_2_in_row_1": {},
    "key_3_in_row_1": {},
    "key_1_in_row_2": {},
    "key_2_in_row_2": {},
    "key_3_in_row_2": {},
    "key_1_in_row_3": {},
    "key_2_in_row_3": {},
    "key_3_in_row_3": {},
    "key_1_in_row_4": {},
    "key_2_in_row_4": {},
    "key_3_in_row_4": {}
}

layers = [{}, layer1, layer2]
layer_select = 1
selection_layer = {}

for i in range(1,len(layers)):
    column = int((i-1)/4) + 1
    row = 4 - int((i-1)%4)
    keyName = "key_" + str(column) + "_in_row_" + str(row)
    layer = layers[i]
    selection_layer[keyName] = {
        "color": layer["color"],
        "keydown": {
            "layer": i
        }
            
    }
layers[0] = selection_layer

strip = apa102.APA102(num_led=12, mosi=10, sclk=11, order='rgb')

def set_color(key_name, color):
    index = keyNames.index(key_name)
    strip.set_pixel_rgb(index, color)
    strip.show()

def get_color(key_name):
    global layer_select
    keys = layers[layer_select]
    if not key_name in keys:
        return 0x000000
    
    key = keys[key_name]
    state = get_state(key)

    
    if "color" + state in key:
        return key["color" + state]
    elif "color" in key:
        return key["color"]
    return 0x000000

def update_color(key_name):
    l_s = layer_select
    color = get_color(key_name)
    if (l_s == layer_select):
        set_color(key_name,color)
    
def get_keydown_url(key):
    state = get_state(key)

    if "keydown" in key:
        keydown = key["keydown"]
        if "url" + state in keydown:
            return keydown["url"+state]
        elif "url" in keydown:
            return keydown["url"]

    return ""

def get_keydown_body(key):
    state = get_state(key)

    if "keydown" in key:
        keydown = key["keydown"]
        if "body" + state in keydown:
            return keydown["body"+state]
        elif "body" in keydown:
            return keydown["body"]

    return ""

def get_keydown_bash(key):
    state = get_state(key)

    if "keydown" in key:
        keydown = key["keydown"]
        if "bash" + state in keydown:
            return keydown["bash"+state]
        elif "bash" in keydown:
            return keydown["bash"]

    return ""

def update_all():
    print ("Starting update")
    keys = layers[layer_select]

    for kN in keyNames:
        if kN in keys:
            invalidate_state(keys[kN])
            thread =threading.Thread(target=update_color, name="Color " + kN, args=[kN])
            thread.start()
        else:
            set_color(kN,0x000000)
    print("update finished")
        

def update_state():
    global layer_select
    while True:
        update_all()
        sleep(2)

def invalidate_state(key):
    if "state" in key:
        key.pop("state")
        
def get_state(key):
    if "state" in key:
        return key["state"]
    
    if "state_req" in key:
        state_req = key["state_req"]
        if "url" in state_req:
            try:
                res = requests.get(state_req["url"])
                if "path" in state_req:
                    doc = res.json()
                    for folder in state_req["path"]:
                        doc = doc[folder]
                    restext = str(doc)
                else:
                    restext = res.text

                if (restext == state_req["stateON"]):
                    key["state"]="ON"
                else:
                    key["state"]="OFF"
            except:
                key["state"]=""
        elif "bash" in state_req:
            try:
                process = subprocess.Popen(state_req["bash"], shell=True, stdout=subprocess.PIPE)
                output, error = process.communicate()
                
                res = output.decode('UTF-8').rstrip()
                print("State result is "+ res)
                if process.returncode != 0:
                    key["state"]=""
                elif (res == state_req["stateON"]):
                    key["state"]="ON"
                else:
                    key["state"]="OFF"
            except:
                key["state"]=""

    else:
        key["state"] = ""
        
    return key["state"]

key_down = {}
for kN in keyNames:
    key_down[kN]=False

def handle_keydown(keyName):
    global layer_select

    print("Handling keydown on " + keyName)
    
    keys = layers[layer_select]
    key = keys[keyName]
        
    #handle keydown event
    if "keydown" in key:
        keydown = key["keydown"]
        url = get_keydown_url(key)
        bash = get_keydown_bash(key)
        if not (url == ""):
            body = get_keydown_body(key)
            # execute correct body
            try: 
                res = requests.put(url,data=body, headers=keydown["header"])
            except:
                res = ""
        if not (bash == ""):
            try:
                process = subprocess.Popen(bash, shell=True, stdout=subprocess.PIPE)
                output, error = process.communicate()

            except:
                output = ""
        if "layer" in keydown:
            layer_select = keydown["layer"]
            print("switching to layer " + str(layer_select))
            update_all()
        invalidate_state(key)
        sleep(0.3)
    update_color(keyName)
    print("finished Handling keydown on " + keyName)

    
def handle(button):
    global key_down
    keyName = keyNames[button]
    keys = layers[layer_select]
    print("event on " + keyName)

    print("state is " + str(GPIO.input(pins[button])))
    
    if GPIO.input(pins[button]) == 1:
        # KeyUp Event
        key_down[keyName]=False
        print("is keyup Event")
        return

    if key_down[keyName]:
        # if already down -> ignore
        print("Bounce detected")
        return
    else: 
        key_down[keyName] = True

    if keyName in keys:
        handler = threading.Thread(target=handle_keydown, args=[keyName])
        handler.start() 
        
    print("Event delegated")

def set_handler(id):
    pin = pins[id]
    
    GPIO.setup(pin,GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(pin, GPIO.BOTH, bouncetime=50, callback=lambda x: handle(id))


t_handlers = {}
for i in range(0,len(pins)):
    t_handlers[i] = threading.Thread(target=set_handler, args=[i])
    t_handlers[i].start() 

thread = threading.Thread(target=update_state, args=())
thread.daemon = True                            # Daemonize thread
thread.start() 

thread.join()
