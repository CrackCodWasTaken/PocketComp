import pygame
import sys

pygame.init()

# Screen setup
WIDTH, HEIGHT = 480, 340
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Settings Menu")

FLIP_DISPLAY = True
# Colors
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
LIGHT_BLUE = (173, 216, 230)

# Fonts
font = pygame.font.SysFont(None, 40)

# Settings options
settings = ["Music Volume", "Sound Effects", "Screen Brightness", "Back"]
selected_index = 0

# Smooth transition variables
cursor_y = 0
transition_speed = 10

clock = pygame.time.Clock()

def draw_menu():
    global cursor_y
    screen.fill(GRAY)
    
    cursor_rect = pygame.Rect(WIDTH//4 + 80, cursor_y - 20, WIDTH//2, 50)
    pygame.draw.rect(screen, LIGHT_BLUE, cursor_rect, border_radius=5)
   
    for i, setting in enumerate(settings):
        text_color = WHITE
        text = font.render(setting, True, text_color)
        text_rect = text.get_rect(center=(WIDTH // 2 + 80, 50 + i * 60))
        screen.blit(text, text_rect)

        # Update cursor position smoothly
        if i == selected_index:
            target_y = text_rect.centery
            cursor_y += (target_y - cursor_y) / transition_speed

    # Draw cursor (a rectangle behind selected option)
    #cursor_rect = pygame.Rect(WIDTH//4, cursor_y - 20, WIDTH//2, 50)
    #pygame.draw.rect(screen, LIGHT_BLUE, cursor_rect, border_radius=5)
def main():
    global selected_index
    running = True

      while running:
          for event in pygame.event.get():
              if event.type == pygame.QUIT:
                  pygame.quit()
                  sys.exit()
              elif event.type == pygame.KEYDOWN:
                  if event.key == pygame.K_w and selected_index > 0:
                      selected_index -= 1
                  elif event.key == pygame.K_s and selected_index < len(settings) - 1:
                      selected_index += 1
                  elif event.key == pygame.K_RETURN:
                      print(f"Selected: {settings[selected_index]}")

          draw_menu()
          if FLIP_DISPLAY:
             rotated = pygame.transform.rotate(screen, 180)
             pygame.display.get_surface().blit(rotated, (0, 0))

          pygame.display.flip()
          clock.tick(60)

if __name__ == "__main__":
    main()
