#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import evdev
import time
import subprocess
import json
import os
from dotenv import load_dotenv

load_dotenv()
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT =  int(os.getenv("MQTT_PORT", 1883))
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_TOPIC_UNLOCK = "door/unlock"
MQTT_TOPIC_SCAN = "door/scan"
DEV_MODE = os.getenv("DEV_MODE", "False").lower() in ("true", "1", "t")


def find_keyboard():
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for dev in devices:
        print(dev)
        if "barcode" in dev.name.lower() or "keyboard" in dev.name.lower():
            print(dev)
            return dev
    print("Keyboard not found, entering dev mode.")
    DEV_MODE = True
    return None


def unlock_door():
    try:
        print("Unlocking door...")
        subprocess.run(["usbrelay"], check=True)
        time.sleep(3)
        subprocess.run(["usbrelay"], check=True)
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
    client.publish(MQTT_TOPIC_SCAN, json.dumps(payload))

def on_message(client, userdata, msg):
    if msg.topic == MQTT_TOPIC_UNLOCK:
        unlock_door()

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