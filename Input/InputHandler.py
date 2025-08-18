# keypad_controller.py
import time
from evdev import UInput, ecodes as e
import ORPi_wiring as gpio
import BridgeMenu

# Physical pins for your 4x4 keypad
ROWS = [37, 35, 33, 31]   # replace with your actual physical row pins
COLS = [29, 36, 38, 40]  # replace with your actual physical column pins

# Key mapping
# Reserve last row for Shift, Ctrl, Fn

#RGB LED Pins 
rL = 12
b = 16
g = 18


# this script handles sesistivty this way, hight pixels / 20, width pixels / 10 then sensivity either times by 0.1-1.5
sens = 1
displayH = 480
displayW = 340


Hs = (displayH / 20) * sens
Ws = (displayW / 10) * sens


if gpio:
    print("found GPIO lib")


#gpio.pinmode(rL,"out")
#gpio.pinmode(g,"out")
#gpio.pinmode(b,"out")



KEYS = [
    ['KEY_SPACE', 'w', 'e', 'mbl'],
    ['a', 's', 'd', 'mbr'],
    ['mvl', 'mvu', 'mvb', 'mvr'],
    ['SHIFT', 'CTRL', 'FN', 'FN2']
]

Fn_keys = [
    ["r", "t", "y", "u"],
    ["i", "o", "p", "f"],
    ["g", "h", "j", "k"]
]

Fn2_keys = [
    ["v", "b", "n", "m"],
    ["KEY_BACKSPACE", "KEY_TAB", "KEY_ALT", "KEY_ENTER"],
    ["q", '"', "|", "/"]
]

Fn_Fn2_keys = [
    ["l", "z", "x", "c"],
    ["(", ")", "KEY_MINUS", "+"],
    ["1", "2", "3", "4"]
]

# Track modifiers
shift = False
ctrl = False
fn = False
fn2 = False
# Setup GPIO pins

gpio.boardmode("OPiZero2W")



for r in ROWS:
    gpio.pinmode(r, "out")
    gpio.write(r, 0)
for c in COLS:
    gpio.pinmode(c, "in")

# Setup virtual keyboard and mouse
ui = UInput({
    e.EV_KEY: list(range(e.KEY_ESC, e.KEY_MICMUTE + 1)) + [
        e.BTN_LEFT, e.BTN_RIGHT, e.BTN_MIDDLE
    ],
    e.EV_REL: [e.REL_X, e.REL_Y],
}, name="keyboard+mouse")


def send_key(row_idx, col_idx):
    global shift, ctrl, fn, fn2
    if row_idx == 3:
         key_name = KEYS[row_idx][col_idx]
    else:
         if fn and fn2:
              key_name = Fn_Fn2_keys[row_idx][col_idx]
              print("using Fn+Fn2")
         elif fn:
              key_name = Fn_keys[row_idx][col_idx]
              print("using Fn")
         elif fn2:
              key_name = Fn2_keys[row_idx][col_idx]
                      else:
              key_name = KEYS[row_idx][col_idx]
    # Modifier keys toggle state
    if key_name == 'SHIFT':
        shift = not shift
        return
    if key_name == 'CTRL':
        ctrl = not ctrl
        return
    if key_name == 'FN':
        fn = not fn
        BridgeMenu.fn = fn
        return
    if key_name == 'FN2':
        fn2 = not fn2
        BridgeMenu.fn2 = fn2
        return
    if key_name == 'mvu':
        move_mouse(-1, "Y")
        return
    if key_name == 'mvb':
        move_mouse(1, "Y")
        return
    if key_name == 'mvr':
        move_mouse(1, "X")
        return
    if key_name == 'mvl':
        move_mouse(-1, "X")
        return
    if key_name == 'mbl':
        ui.write(e.EV_KEY, e.BTN_LEFT, 1)  # press
        ui.syn()
        time.sleep(0.05)
        ui.write(e.EV_KEY, e.BTN_LEFT, 0)  # release
        ui.syn()
        return
    if key_name == 'mbr':
        ui.write(e.EV_KEY, e.BTN_RIGHT, 1)
        ui.write(e.EV_KEY, e.BTN_RIGHT, 0)
        ui.syn()
        return
     # Map evdev keycode
    keycode = getattr(e, key_name, getattr(e, 'KEY_' + key_name.upper(), None))
    if not keycode:
        return

    # Press modifiers first
    if shift: ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
    if ctrl:  ui.write(e.EV_KEY, e.KEY_LEFTCTRL, 1)

    # Press the key
    ui.write(e.EV_KEY, keycode, 1)
    ui.write(e.EV_KEY, keycode, 0)
    print(keycode)
    ui.syn()

    # Release modifiers
    if shift: ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
    if ctrl:  ui.write(e.EV_KEY, e.KEY_LEFTCTRL, 0)
    ui.syn()

def scan_keypad():
    for r_idx, r_pin in enumerate(ROWS):
        gpio.write(r_pin, 1)
        for c_idx, c_pin in enumerate(COLS):
            if gpio.readpin(c_pin) == 1:
                send_key(r_idx, c_idx)
                time.sleep(0.2)  # debounce
        gpio.write(r_pin, 0)

acc_x = 0.0
acc_y = 0.0



def getKey():
    scan_keypad()



def move_mouse(Input, Dir):
    global acc_x, acc_y

    if Dir == "X":
        acc_x += Ws * Input
        move = int(acc_x)  # take whole pixels
        if move != 0:
            ui.write(e.EV_REL, e.REL_X, move)
            acc_x -= move    # keep leftover fraction

    if Dir == "Y":
        acc_y += Hs * Input
        move = int(acc_y)
        if move != 0:
            ui.write(e.EV_REL, e.REL_Y, move)
            acc_y -= move

    ui.syn()

try:
    while True:
        time.sleep(0.05)
        getKey()
except KeyboardInterrupt:
    ui.close()
    for p in ROWS + COLS:
        gpio.unexport(p)
    #gpio.unexport(rL)
    #gpio.unexport(g)
    #gpio.unexport(b)
