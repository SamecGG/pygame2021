import sys, pygame
pygame.init()

size = width, height = 800, 600
black = 255, 255, 255

WIN = pygame.display.set_mode(size)

FPS = 60

def draw_window():
    WIN.fill(black)
    pygame.display.update()

def main():
    pass

if __name__ == "__main__":
    clock = pygame.time.Clock()
    run = True

    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False
        main()
        draw_window()

    pygame.quit()