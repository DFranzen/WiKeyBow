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
    "color": 0x00ff00,
    "key_1_in_row_1": {
        "name":  "Lamp"
        "color": 0x1eff1e,
        "colorOFF": 0xFF0000,
        "colorON": 0x00FF00,
        "state_req": {
            "bash": "echo ON"
            "url": "http://...",
            "method": "GET",
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
            "method": "PUT",
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
    "color": 0x0000ff,
    "key_1_in_row_1": {
        "name":  "Lamp"
        "color": 0x1eff1e,
        "colorOFF": 0xFF0000,
        "colorON": 0x00FF00,
        "state_req": {
            "bash": "echo ON"
            "url": "http://...",
            "method": "GET",
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
            "method": "POST",
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
layers = [{}, layer1, layer2, layer_Esszimmer, layer_Arbeitszimmer]
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
    
def get_state_req_method(state_req):
    if "method" in state_req:
        return state_req["method"]
    return "GET"

def get_state_req_body(state_req):
    if "body" in state_req:
        return state_req["body"]
    return "{}"

def get_state_req_header(state_req):
    if "header" in state_req:
        return state_req["header"]
    return {}

def get_keydown_url(key):
    state = get_state(key)

    if "keydown" in key:
        keydown = key["keydown"]
        if "url" + state in keydown:
            return keydown["url"+state]
        elif "url" in keydown:
            return keydown["url"]

    return ""

def get_keydown_method(keydown):
    if "method" in keydown:
        return keydown["method"]
    return "PUT"

def get_keydown_body(key):
    state = get_state(key)

    if "keydown" in key:
        keydown = key["keydown"]
        if "body" + state in keydown:
            return keydown["body"+state]
        elif "body" in keydown:
            return keydown["body"]

    return ""

def get_keydown_header(keydown):
    if "header" in keydown:
        return keydown["header"]
    return {}


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
    keys = layers[layer_select]

    for kN in keyNames:
        if kN in keys:
            invalidate_state(keys[kN])
            thread =threading.Thread(target=update_color, name="Color " + kN, args=[kN])
            thread.start()
        else:
            set_color(kN,0x000000)
        

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
                http_action = get_state_req_method(state_req)
                header = get_state_req_header(state_req)
                body = get_state_req_body(state_req)
                
                if http_action == "GET":
                    res = requests.get(state_req["url"],headers=header)
                elif http_action == "POST":
                    res = requests.post(state_req["url"],headers=header, data = body)
                elif http_action == "PUT":
                    res = requests.put(state_req["url"],headers=header, data = body)
                    
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
            try:
                http_action = get_keydown_method(keydown)
                body = get_keydown_body(key)
                header = get_keydown_header(keydown)
                if http_action == "GET":
                    res = requests.get(url, headers=header)
                elif http_action == "PUT":
                    res = requests.put(url,data=body, headers=header)
                elif http_action == "POST":
                    res = requests.post(url,data=body, headers=header)
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
