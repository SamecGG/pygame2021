import pygame, sys, os
import math

import classes
from classes import Terrain, TERRAIN_TEXTURE_SHEET

import numpy as np
from numpy import save

pygame.init()
pygame.font.init()

FPS = 60
SIZE = WIDTH, HEIGHT = 800, 600 
WIN = pygame.display.set_mode(SIZE)

# Colors 
WHITE = 255, 255, 255
BLACK = 0, 0, 0 

# Player CONSTANTS
PLAYER_SPEED = 20

# Player Vars
player_x = WIDTH / 2
player_y = HEIGHT / 2
player_width = 40
player_height = 40
player_rect = pygame.Rect(((WIDTH - player_width)/2, (HEIGHT - player_width)/2), (player_width, player_height))

font = pygame.font.SysFont('Calibri', 30)


if __name__ == "__main__":
    clock = pygame.time.Clock()
    run = True
    ui = font.render('0', False, WHITE)
    img_size = 55
    
    classes.is_editor = True

# terrain
    terrain_size = 3, 3
    terrain_path = f'{os.getcwd()}\pygame\Assets\Terrains\default'
    terrain = Terrain(TERRAIN_TEXTURE_SHEET, terrain_path, *terrain_size)

# pickbar
    pickbar_sensitivity = 1
    pickbar_scroll = 0
    pickbar_width = len(TERRAIN_TEXTURE_SHEET.images)
    pickbar = pygame.Surface((img_size * pickbar_width, img_size))

    i = 0
    for block in TERRAIN_TEXTURE_SHEET.images:
        pickbar.blit(block, (img_size * i, 0))
        i += 1

# tuple prefab 
    transparent_surface = tuple(x * terrain.chunk_size for x in terrain_size), pygame.SRCALPHA, 32

# objects
    objects = np.zeros((0), dtype=classes.Object)
    game_objects = np.zeros((0), dtype=classes.Object)
    
    object_layer = pygame.Surface(*transparent_surface)
    game_object_layer = pygame.Surface(*transparent_surface)

# building
    """
    'ci[1]-ci[0]_bi[1]-bi[0]' -> [chunk_index, block_index, int block]
    """
    building_queue = {}
    building_layer = pygame.Surface(*transparent_surface)

    is_building = False

#region MainLoop
# main loop
    while run:
        clock.tick(FPS)
        # clock.tick(10)
        WIN.fill(BLACK)

        # Selected block
        selection = abs(pickbar_scroll)

        #region Building positions calculations
        # building
        index_tuple = tuple(math.floor((x + y) / img_size) for x, y in zip(pygame.mouse.get_pos(), (player_x, player_y)))
        # chunk index
        chunk_index = tuple(math.floor(x / 16) for x in index_tuple)
        # block index
        block_index = tuple(x % 16 for x in index_tuple)
        # position
        position_tuple = tuple(x * img_size - y for x, y in zip(index_tuple, (player_x, player_y)))
        # building tuple
        building_tuple = tuple(x * img_size for x in index_tuple)
        #endregion

    #region Key binds
        for event in pygame.event.get():
            etype = event.type

        # win quit
            if etype == pygame.QUIT: 
                run = False

        # mouse scrolls
            if etype == pygame.MOUSEBUTTONDOWN:
                scroll_val = 1 * pickbar_sensitivity

            # scroll up
                if event.button == 4:
                    if pickbar_scroll + scroll_val <= 0:
                        pickbar_scroll += scroll_val
            # scroll down
                elif event.button == 5:
                    if pickbar_scroll - scroll_val >= -pickbar_width:
                        pickbar_scroll -= scroll_val
        
        # mouse up
            if etype == pygame.MOUSEBUTTONUP:
            # left button
                if event.button == 1:
                    if not building_queue:
                        print("ERROR: building_queue neexistuje, key bindings, mouse up, left button")
                        continue

                    is_building = False

                    for key in building_queue:
                        val = building_queue[key]

                        c_index = val[0]
                        b_index = val[1]
                        block = val[2]

                        with open(f'{terrain_path}/{c_index[0]}_{c_index[1]}.npy', 'wb') as f:
                            if not isinstance(terrain.chunks_arr[c_index[1]][c_index[0]], int):
                                terrain.chunks_arr[c_index[1]][c_index[0]][b_index[1]][b_index[0]] = block
                                save(f, terrain.chunks_arr[c_index[1]][c_index[0]], allow_pickle=True)

                    building_queue.clear()
                
                    terrain.reload_pos((n_player_x, n_player_y))

    # Mouse button input
        m_buttons = pygame.mouse.get_pressed()
        # Left Click held down
        if m_buttons[0]:
            condition = True
            is_building = True
            for x, y in zip(chunk_index, terrain_size):
                condition &= y > x >= 0

            if condition:
                block = terrain.chunks_arr[chunk_index[1]][chunk_index[0]][block_index[1]][block_index[0]]

                # if placing the same block
                if not (block == selection or selection > 255):
                    building_queue[f'{chunk_index[1]}-{chunk_index[0]}_{block_index[1]}-{block_index[0]}'] = [chunk_index, block_index, selection] 
                    building_layer.blit(TERRAIN_TEXTURE_SHEET.images[selection], building_tuple)

    # Key input
        # WSAD
        keys = pygame.key.get_pressed()
        if not is_building:
            if keys[pygame.K_w]:
                if player_y - PLAYER_SPEED + HEIGHT / 2 >= 0:
                    player_y -= PLAYER_SPEED
            if keys[pygame.K_s]:
                if player_y + PLAYER_SPEED - HEIGHT <= (terrain_size[1]-1)*16*img_size:
                    player_y += PLAYER_SPEED
            if keys[pygame.K_a]:
                if player_x - PLAYER_SPEED + WIDTH / 2 >= 0:
                    player_x -= PLAYER_SPEED
            if keys[pygame.K_d]:
                if player_x + PLAYER_SPEED - WIDTH / 2 <= (terrain_size[0]-1)*16*img_size:
                    player_x += PLAYER_SPEED

        n_player_x = -player_x
        n_player_y = -player_y
    
    #endregion
   
    #region Drawing calculations
    # terrain draw calculation
        terrain.draw_pos((n_player_x, n_player_y), WIN)

    # UI draw calculation
        # text
        ui = font.render(str(pickbar_scroll), False, WHITE)
        # building
        if -pickbar_scroll < 256:
            block = TERRAIN_TEXTURE_SHEET.images[-pickbar_scroll]
    
    # Objects draw calculation
        game_object_layer = pygame.Surface(*transparent_surface)

        for game_object in game_objects:
            game_object.draw(game_object_layer)

    #endregion

    #region Rendering
        if block:        
            prefab = block.copy()
            prefab.set_alpha(200)
            WIN.blit(prefab, position_tuple)

        player_n_position = (-player_x, -player_y)

        WIN.blit(object_layer, player_n_position)
        WIN.blit(game_object_layer, player_n_position)
        WIN.blit(building_layer, player_n_position)

        # pickbar
        WIN.blit(pickbar, (pickbar_scroll * img_size, HEIGHT-img_size)) if pickbar_scroll >= -240 else WIN.blit(pickbar, (-240 * img_size, HEIGHT-img_size))
        # text
        WIN.blit(ui, (0, 0))
        pygame.display.update()
    #endregion

    #endregion
    pygame.quit()