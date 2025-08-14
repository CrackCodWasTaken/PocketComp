# keypad_controller.py
import time
from evdev import UInput, ecodes as e
import ORPi_wiring as gpio

# Physical pins for your 4x4 keypad
ROWS = [37, 35, 33, 31]   # replace with your actual physical row pins
COLS = [40, 38, 36, 29]  # replace with your actual physical column pins

# Key mapping
# Reserve last row for Shift, Ctrl, Fn




if gpio:
    print("found GPIO lib")

KEYS = [
    ['w', 'a', 's', 'd'],                     # navigation for Kodi
    ['KEY_UP', 'KEY_LEFT', 'KEY_DOWN', 'KEY_RIGHT'],  # arrow keys
    ['KEY_ENTER', 'KEY_ESC', 'KEY_BACKSPACE', 'KEY_SPACE'],  # basic terminal
    ['SHIFT', 'CTRL', 'FN', 'KEY_TAB']        # modifiers and extra
]

Fn_keys = [
    ["q", "e", "r", "t"],
    ["f", "g", "h", "j"],
    ["z", "x", "c", "v"]
]

Fn_ctrl = [
    ["y", "u", "i", "o"],
    ["k", "l", "'", "|"],
    ["b", "n", "m", "KEY_ALT"]
]


# Track modifiers
shift = False
ctrl = False
fn = False

# Setup GPIO pins

gpio.boardmode("OPiZero2W")



for r in ROWS:
    gpio.pinmode(r, "out")
    gpio.write(r, 0)
for c in COLS:
    gpio.pinmode(c, "in")

# Setup virtual keyboard
ui = UInput()

def send_key(row_idx, col_idx):
    global shift, ctrl, fn

    if fn and ctrl:
        key_name = Fn_ctrl[row_idx][col_idx]
    elif fn:
        key_name = Fn_keys[row_idx][col_idx]
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

try:
    while True:
        scan_keypad()
        time.sleep(0.05)
except KeyboardInterrupt:
    ui.close()
    for p in ROWS + COLS:
        gpio.unexport(p)
