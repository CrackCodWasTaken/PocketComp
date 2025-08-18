import subprocess
import time
import os


MENU_PATH = "/root/PocketCalc/FrontEnd/Menu/LCM.py"
LOCK_FILE = "/tmp/menu.lock"




Drunning = False


def is_display_in_use():
    try:
        output = subprocess.check_output("pgrep Xorg", shell=True)
        return bool(output.strip())
        Drunning = True
    except subprocess.CalledProcessError:
        return False
        Drunning = False


while True:
    is_display_in_use()

    if not Drunning:
        if not os.path.exists(LOCK_FILE):
            subprocess.Popen(f"python3 {MENU_PATH}", shell=True)
            print("Menu launched")
    
    time.sleep(2)  # check every 2 seconds to avoid spamming
