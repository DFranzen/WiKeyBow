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

keys = {
    "key_1_in_row_1": {
        "name":  "Lamp"
        "color": 0x1eff1e,
        "colorOFF": 0xFF0000,
        "colorON": 0x00FF00,
        "state_req": {
            "bash": "echo ON"
            "url": "http://...",
            "stateON": 'ON',
        },
        "keydown": {
            "url": "http://...",
            "header": {"content-type": "application/json"},
            "body": "{\"on\":false}"
            "bodyON": "{\"on\":false}"
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

strip = apa102.APA102(num_led=12, mosi=10, sclk=11, order='rgb')

def update_color(key_name, color):
    index = keyNames.index(key_name)
    strip.set_pixel_rgb(index, color)
    strip.show()

def get_color(key_name):
    key = keys[key_name]
    state = get_state(key)
    
    if "color" + state in key:
        return key["color" + state]
    return 0x000000
    
    
def update_state():
    # threads = {}
    while True:
        print ("Starting update")
        for kN in keyNames:
            color = get_color(kN)
            update_color(kN,color)
#            threads[kN] =threading.Thread(target=update_color, name="Color " + kN, args=[kN,color])
#            threads[kN].start()
        print("update finished")
        sleep(2)

def get_state(key):
    if "state_req" in key:
        state_req = key["state_req"]
        if "url" in state_req:
            res = requests.get(state_req["url"])
            if (res.text == state_req["stateON"]):
                key["state"]="ON"
            else:
                key["state"]="OFF"
        elif "bash" in state_req:
            process = subprocess.Popen(state_req["bash"], shell=True, stdout=subprocess.PIPE)
            output, error = process.communicate()
            res = output.decode('UTF-8').rstrip()
            if (res == state_req["stateON"]):
                key["state"]="ON"
            else:
                key["state"]="OFF"

    else:
        key["state"] = ""
        
    return key["state"]

        
def handle(button):
    keyName = keyNames[button]
    if keyName in keys:
        key = keys[keyName]
        if not "down" in key:
            key["down"] = False
    
        if GPIO.input(pins[button]) == 1:
            #update_state()
            key["down"]=False
            return

        if key["down"]:
            return

        key["down"] = True
        if "keydown" in key:
            keydown = key["keydown"]
            if "url" in keydown:
                
                # get the state
                state = get_state(key)
                # execute correct body
                res = requests.put(keydown["url"],data=keydown["body" + state], headers=keydown["header"])
    sleep(0.3)
    update_color(keyName, get_color(keyName))
    print("handle done")
#    update_state()



def set_handler(id):
    pin = pins[id]
    
    GPIO.setup(pin,GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(pin, GPIO.BOTH, bouncetime=300, callback=lambda x: handle(id))

t_handlers = {}
for i in range(0,len(pins)):
    t_handlers[i] = threading.Thread(target=set_handler, args=[i])
    t_handlers[i].start() 

thread = threading.Thread(target=update_state, args=())
thread.daemon = True                            # Daemonize thread
thread.start() 

thread.join()
