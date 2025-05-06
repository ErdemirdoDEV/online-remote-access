
import websocket
import threading
import time
import mss
import cv2
import numpy as np
import json
from pynput.keyboard import Controller, Key
from pynput.mouse import Button, Controller as MouseController

WS_URL = "wss://yourbackend.com"

def capture_and_send(ws):
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        while True:
            img = np.array(sct.grab(monitor))
            _, jpeg = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            ws.send(jpeg.tobytes(), opcode=websocket.ABNF.OPCODE_BINARY)
            time.sleep(0.05)

def on_open(ws):
    print("[✔] Connection opened.")
    ws.send("iamstreamer")
    threading.Thread(target=capture_and_send, args=(ws,)).start()

def on_error(ws, error):
    print(f"[✖] WebSocket Error: {error}")

def on_message(ws, message):
    try:
        keyboard = Controller()
        mouse = MouseController()
        data = json.loads(message)

        if data['type'] == 'mousemove':
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                screen_width = monitor['width']
                screen_height = monitor['height']
            
            x = int(data['x'] * screen_width)
            y = int(data['y'] * screen_height)
            mouse.position = (x, y)
            
        elif data['type'] == 'mouseclick':
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                screen_width = monitor['width']
                screen_height = monitor['height']
            
            x = int(data['x'] * screen_width)
            y = int(data['y'] * screen_height)
            mouse.position = (x, y)
            button = Button.left if data.get('button', 0) == 0 else Button.right
            mouse.click(button)
            
        elif data['type'] == 'keypress':
            special_keys = {
                'Enter': Key.enter,
                'Backspace': Key.backspace,
                'Tab': Key.tab,
                'ArrowUp': Key.up,
                'ArrowDown': Key.down,
                'ArrowLeft': Key.left,
                'ArrowRight': Key.right,
                'Escape': Key.esc,
                'Delete': Key.delete,
            }

            key = special_keys.get(data['key'], data['key'])

            if data['ctrlKey']:
                keyboard.press(Key.ctrl)
            if data['shiftKey']:
                keyboard.press(Key.shift)
            if data['altKey']:
                keyboard.press(Key.alt)

            try:
                keyboard.press(key)
                keyboard.release(key)
            except Exception as e:
                print(f"[✖] Error during key press: {e}")

            if data['ctrlKey']:
                keyboard.release(Key.ctrl)
            if data['shiftKey']:
                keyboard.release(Key.shift)
            if data['altKey']:
                keyboard.release(Key.alt)

    except json.JSONDecodeError as e:
        print(f"[✖] Error decoding JSON message: {e}")

def on_close(ws, close_status_code, close_msg):
    try:
        print("[✖] Connection closed.")
    except Exception as e:
        print(f"[✖] Error during connection close: {e}")

if __name__ == "__main__":
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_error=on_error,
        on_message=on_message,
        on_close=on_close
    )
    ws.run_forever()
