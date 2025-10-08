#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import evdev
import time
import subprocess
import json
import os
from dotenv import load_dotenv
import threading

load_dotenv()
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT =  int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_TOPIC_UNLOCK = "door/unlock"
MQTT_TOPIC_SCAN = "door/scan"
INPUT_DEVICE_NAME = os.getenv("INPUT_DEVICE_NAME", "keyboard")
USBRELAY_RELID = os.getenv("USBRELAY_RELID", "1")
USBRELAY_PREFIX = os.getenv("USBRELAY_PREFIX", "BITFT")
DEV_MODE = os.getenv("DEV_MODE", "False").lower() in ("true", "1", "t")
RELAY_NAME = USBRELAY_PREFIX+"_"+USBRELAY_RELID

def find_keyboard():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    print(devices)
    for dev in devices:
        if INPUT_DEVICE_NAME.lower() in dev.name.lower():
            print("Using Input Device: ", dev)
            return dev
    print("Keyboard not found, entering dev mode.")
    DEV_MODE = True
    return None

def watchdog():
    while True:
        output = subprocess.run(["echo", "BITFT_1=0"], capture_output=True, text=True).stdout
        print(RELAY_NAME.lower() in output.lower())
        time.sleep(3)


def unlock_door():
    try:
        cmd = RELAY_NAME+"="
        print("Unlocking door...")
        subprocess.run(["usbrelay", cmd+"1"], check=True)
        time.sleep(5)
        subprocess.run(["usbrelay", cmd+"0"], check=True)
    except Exception as e:
        print(f"Error unlocking door: {e}")


def read_scanner(device, client):
    input_text = ""
    for event in device.read_loop():
        if event.type == evdev.ecodes.EV_KEY:
            key = evdev.categorize(event)
            if key.keystate == 1:  # key down
                if key.keycode == "KEY_ENTER":
                    if input_text:
                        send_payload(input_text, client)
                        input_text = ""
                else:
                    code = key.keycode.replace("KEY_", "")
                    if len(code) == 1:
                        input_text += code
        

def send_payload(input_text, client):
    payload = {"type": "barcode", "code": input_text}
    client.publish(MQTT_TOPIC_SCAN, json.dumps(payload), 2)

def on_message(client, userdata, msg):
    if msg.topic == MQTT_TOPIC_UNLOCK:
        unlock_door()

threading.Thread(target=watchdog).start()

client = mqtt.Client()
client.on_message = on_message
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.subscribe(MQTT_TOPIC_UNLOCK)
client.loop_start()

if not DEV_MODE:
    input_device = find_keyboard()
    read_scanner(input_device, client)
else:
    while True:
        input_text = input("Enter barcode to simulate scan (or 'exit' to quit): ")
        if input_text.lower() == 'exit':
            break
        send_payload(input_text, client)