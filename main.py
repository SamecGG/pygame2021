import pygame, sys
import pygame.font

pygame.init()
pygame.font.init()

FPS = 60
SIZE = WIDTH, HEIGHT = 800, 600 
WIN = pygame.display.set_mode(SIZE)

# Colors 
WHITE = 255, 255, 255
BLACK = 0, 0, 0 

# Player CONSTANTS
PLAYER_SPEED = 10

font = pygame.font.SysFont('Calibri', 30)

ui = font.render('Some Text', False, BLACK)


if __name__ == "__main__":
    clock = pygame.time.Clock()
    run = True

    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False

        WIN.fill(WHITE)
        WIN.blit(ui, (0, 0))
        pygame.display.update()

    pygame.quit()