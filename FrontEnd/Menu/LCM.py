import pygame
import sys
import subprocess
import os


LOCK_FILE = "/tmp/menu.lock"


if os.path.exists(LOCK_FILE):
    print("Menu already running!")
    sys.exit()


with open(LOCK_FILE, "w") as f:
    f.write("running")


os.environ["XDG_RUNTIME_DIR"] = "/tmp"



sys.path.append("/root/PocketCalc/Input/")  # absolute or relative path

#import BridgeMenu

# --- Config ---
SCREEN_W, SCREEN_H = 480, 340
ICON_SIZE = 64
PADDING = 20
FONT_SIZE = 16
MAX_VISIBLE = 5  # how many icons show at once in the dock
DOCK_Y = SCREEN_H - ICON_SIZE + 100
SCALE_SPEED = 0.2
FLIP_DISPLAY = True

# Define your "apps"
APPS = [
    {"name": "Kodi", "icon": "/usr/share/icons/tlauncher.png", "cmd": "xinit kodi"},
    {"name": "Files", "icon": "icons/folder.png", "cmd": "pcmanfm"},
    {"name": "Terminal", "icon": "icons/terminal.png", "cmd": "xinit xterm"},
    {"name": "Music", "icon": "icons/music.png", "cmd": "vlc"},
    {"name": "Games", "icon": "icons/game.png", "cmd":  "xinit retroarch"},
    {"name": "Settings", "icon": "icons/settings.png", "cmd": "python3 /root/PocketCalc/FrontEnd/Menu/settings.py"},
]

# --- Setup ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Handheld Menu")
font = pygame.font.SysFont("Arial", FONT_SIZE)

# Load icons (fallback to colored box if missing)
def load_icon(path):
    try:
        img = pygame.image.load(path)
        return pygame.transform.scale(img, (ICON_SIZE, ICON_SIZE))
    except:
        surf = pygame.Surface((ICON_SIZE, ICON_SIZE))
        surf.fill((150, 150, 150))
        return surf

for app in APPS:
    app["surf"] = load_icon(app["icon"])
    app["scale"] = 1.0  # for smooth animation

selected = 0
scroll_index = 0



# Optional: background image
try:
    bg = pygame.image.load("background.jpg").convert()
    bg = pygame.transform.scale(bg, (SCREEN_W, SCREEN_H))
except:
    bg = None  # fallback to solid color

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RIGHT, pygame.K_d):
                selected = min(selected + 1, len(APPS) - 1)
                if selected >= scroll_index + MAX_VISIBLE:
                    scroll_index += 1
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                selected = max(selected - 1, 0)
                if selected < scroll_index:
                    scroll_index -= 1

            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                app = APPS[selected]
                print(f"Launching: {app['cmd']}")

                # Quit Pygame to free display
                pygame.quit()

                # Launch app and wait until it exits
                subprocess.run(app["cmd"], shell=True)

                # Reinitialize Pygame menu
                pygame.init()
                screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
                pygame.display.set_caption("Handheld Menu")
                clock = pygame.time.Clock()

                if os.path.exists(LOCK_FILE):
                    os.remove(LOCK_FILE) 
                    sys.exit()
    # --- Draw ---
    if bg:
        screen.blit(bg, (0, 0))
    else:
        screen.fill((20, 20, 20))  # fallback background

    # Draw dock icons
    visible_apps = APPS[scroll_index:scroll_index + MAX_VISIBLE]
    spacing = (SCREEN_W - (len(visible_apps) * ICON_SIZE)) // (len(visible_apps) - 1)

    for i, app in enumerate(visible_apps):
        # Smooth scaling
        target_scale = 1.2 if scroll_index + i == selected else 1.0
        app["scale"] += (target_scale - app["scale"]) * SCALE_SPEED
        icon_size = int(ICON_SIZE * app["scale"])
        icon_surf = pygame.transform.scale(app["surf"], (icon_size, icon_size))
        total_width = len(visible_apps) * ICON_SIZE + (len(visible_apps) - 1) * spacing
        start_x = SCREEN_W - 340 - spacing  # start from right
        pos_x = start_x + i * (ICON_SIZE + spacing) + (ICON_SIZE - icon_size)//2
        pos_y = DOCK_Y - (icon_size - ICON_SIZE)//2

        # Highlight rectangle
        if scroll_index + i == selected:
            pygame.draw.rect(screen, (80, 80, 200),
                             (pos_x-4, pos_y-4, icon_size+8, icon_size+8), border_radius=6)

        # Draw icon
        screen.blit(icon_surf, (pos_x, pos_y))

        # Draw label
        label = font.render(app["name"], True, (255, 255, 255))
        label_rect = label.get_rect(center=(pos_x + icon_size//2, pos_y + icon_size + 12))
        screen.blit(label, label_rect)

    # --- Flip display if needed ---
    if FLIP_DISPLAY:
        rotated = pygame.transform.rotate(screen, 180)
        pygame.display.get_surface().blit(rotated, (0, 0))
    
    pygame.display.flip()
    clock.tick(30
