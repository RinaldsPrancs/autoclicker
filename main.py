from pynput import keyboard, mouse
from pynput.mouse import Controller, Button
import time
import tkinter as tk
import json
import threading

def update_label():
    cps_label.config(text=f"Click speed: {args['cps']} (c/s)")
    start_key_label.config(text=f"Start key: {args['start_key']}")
    end_key_label.config(text=f"End key: {args['end_key']}")

def save_settings():
    with open("config.json", "w") as f:
        json.dump(args, f, indent=4)

def on_press(key):
    global listening_for
    try:
        val = key.char
        if listening_for == "start":
            args["start_key"]= val
        else:
            args["end_key"]= val
        stop_listeners()
    except AttributeError:
        val = str(key)
        if listening_for == "start":
            args["start_key"]= val
        else:
            args["end_key"]= val
        stop_listeners()
    
    listening_for = None
    stop_listeners()
    update_label()
    save_settings()
    start_main_listener()

def on_click(x, y, button, pressed):
    if button and pressed:
        val = str(button)
        if val != "Button.left" and listening_for == "start":
            args["start_key"]= val
        elif val != "Button.left" and listening_for == "end":
            args["end_key"]= val
        
        
        stop_listeners()
        update_label()
        save_settings()
        start_main_listener()
        

def start_listeners(key_type):
    global keyboard_listener, mouse_listener, listening_for
    stop_main_listener()
    listening_for = key_type
    keyboard_listener = keyboard.Listener(on_press=on_press)
    mouse_listener = mouse.Listener(on_click=on_click)
    keyboard_listener.start()
    mouse_listener.start()


def stop_listeners():
    global keyboard_listener, mouse_listener, listening
    if mouse_listener:
        mouse_listener.stop()
        mouse_listener = None
    if keyboard_listener:
        keyboard_listener.stop()
        keyboard_listener = None

def on_enter(event):
    val = entry.get()
    if val.isnumeric():
        args['cps'] = val
        update_label()
    entry.delete(0, tk.END)
    root.focus()
    save_settings()


# MAIN

def on_click_main(x, y, button, pressed):
    global clicking,click_thread
    if button and pressed:
        val = str(button)
        if val == args["start_key"]:
            if not clicking:
                clicking = True
                click_thread = threading.Thread(target=click_mouse_indefinitely)
                click_thread.start()
            
        elif val == args["end_key"]:
            if clicking:
                clicking = False
                if click_thread:
                    click_thread.join() 
                    click_thread = None

def on_press_main(key):
    global clicking, click_thread
    try:
        val = key.char
    except AttributeError:
        val = str(key)

    if val == args["start_key"]:
        if not clicking:
            clicking = True
            click_thread = threading.Thread(target=click_mouse_indefinitely)
            click_thread.start()
        
    elif val == args["end_key"]:
        if clicking:
            clicking = False
            if click_thread:
                click_thread.join() 
                click_thread = None
        

def start_main_listener():
    global main_listener, main_listener2
    if main_listener or main_listener2:
        return 
    main_listener = keyboard.Listener(on_press=on_press_main)
    main_listener.start()
    main_listener2 = mouse.Listener(on_click=on_click_main)
    main_listener2.start()

def stop_main_listener():
    global main_listener, main_listener2
    if main_listener:
        main_listener.stop()
        main_listener = None
    if main_listener2:
        main_listener2.stop()
        main_listener2 = None    


def click_mouse_indefinitely():
    global clicking
    delay = 1 / float(args['cps'])
    while clicking:
        mouse_controller.click(Button.left)
        time.sleep(delay)

root = tk.Tk()
root.title("Autoclicker")
root.geometry("400x550")

filename = "config.json"

try:
    with open(filename, "r") as f:
        args = json.load(f)
except FileNotFoundError:
    args = {"cps": 10, "start_key": "8", "end_key": "9"}
    with open(filename, "w") as f:
        json.dump(args, f, indent=4)

mouse_controller = Controller()
click_thread = None
clicking = False
main_listener = None
main_listener2 = None
keyboard_listener = None
mouse_listener = None
listening_for = None

cps_label = tk.Label(root, text=f"Click speed: {args['cps']} (c/s)")
cps_label.pack(pady=20)

entry = tk.Entry(root)
entry.pack(pady=20)
entry.bind("<Return>", on_enter)

start_key_label = tk.Label(root, text=f"Start key: {args['start_key']}")
start_key_label.pack(pady=20)

btn_start_key = tk.Button(root, text="Set Start key", command=lambda: start_listeners("start"))
btn_start_key.pack(pady=10)

end_key_label = tk.Label(root, text=f"End key: {args['end_key']}")
end_key_label.pack(pady=20)

btn_end_key = tk.Button(root, text="Set End key", command=lambda: start_listeners("end"))
btn_end_key.pack(pady=10)

start_main_listener()
root.mainloop()