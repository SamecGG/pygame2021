import terrain_generation
import numpy as np
import pygame
import math
import os

pygame.init()

is_editor = False

class Object:
    def __init__(this, img, parent):
        this.img = img
        this.collider = Collider(img.get_rect())
        this.transform = Transform()
        this.children
    
    def move(this, dir, force):
        pass

    def destroy(this):
        pass

    def draw(this, win):
        img = this.img
        if this.transform.enabled:
            win.blit(this.img, this.transform.position)

    def draw_prefab(this, win):
        pass

class GameObject(Object):
    def __init__(this):
        pass

class Transform:
    def __init__(this, position=(0, 0), rotation=(0, 0)):
        this.enabled = True
        this.position = position
        this.rotation = rotation

class Collider:
    def __init__(this, rect):
        this.rect = rect

# Terrain
class Terrain:
    def __init__(this, texture_sheet, path=None, height=3, width=3):
        """
        Načte terén, pokud zadaná cesta neexistuje vytvoří terén nový
        """
        if path:
            this.path = path
        if not os.path.exists(path):
            this.create_terrain(texture_sheet.img_size, height, width)
        else: 
            this.load_file(path)

        this.texture_sheet = texture_sheet
        this.chunks = np.zeros((height, width), dtype=TerrainChunk)
        this.chunk_pos_x = -1
        this.chunk_pos_y = -1
        this.chunk_size = (16 * this.img_size)

        this.load_pos((0,0))
    
    def load_pos(this, position):
        """
        Načte chunky okolo zadané pozice
        """
        x = position[0]
        y = position[1]

        chunk_size = this.chunk_size
        chunk_pos_x = -math.floor(x/chunk_size)
        chunk_pos_y = -math.floor(y/chunk_size)

        # print("Terrain/load_pos: ", chunk_pos_x, chunk_pos_y)

        chunks = np.zeros((3, 3), dtype=TerrainChunk)
        chunks_arr = np.zeros((3, 3), dtype=TerrainChunk)

        if chunk_pos_x != this.chunk_pos_x or chunk_pos_y != this.chunk_pos_y:
            width = this.width
            height = this.height
            for y in range(3):
                for x in range(3):
                    chunk_x = x + chunk_pos_x - 1
                    chunk_y = y + chunk_pos_y - 1

                    #skipping border chunks
                    if not (width > chunk_x >= 0) or not (height > chunk_y >= 0):
                        chunks[y][x] = None
                        continue

                    chunk = TerrainChunk((chunk_x , chunk_y), this.path, this.texture_sheet)
                    _, chunk_arr = chunk.load(this.img_size, (this.width, this.height))
                    chunks[y][x] = chunk
                    chunks_arr[chunk_y][chunk_x] = chunk_arr

            this.chunks = chunks
            this.chunks_arr = chunks_arr
            this.chunk_pos_x = chunk_pos_x
            this.chunk_pos_y = chunk_pos_y
    
    def reload_pos(this, position):
        """
        Načte chunky okolo zadané pozice
        """
        x = position[0]
        y = position[1]

        chunk_size = this.chunk_size
        chunk_pos_x = -math.floor(x/chunk_size)
        chunk_pos_y = -math.floor(y/chunk_size)

        # print("Terrain/load_pos: ", chunk_pos_x, chunk_pos_y)

        chunks = np.zeros((3, 3), dtype=TerrainChunk)
        chunks_arr = np.zeros((3, 3), dtype=TerrainChunk)

        width = this.width
        height = this.height
        for y in range(3):
            for x in range(3):
                chunk_x = x + chunk_pos_x - 1
                chunk_y = y + chunk_pos_y - 1

                #skipping border chunks
                if not (width > chunk_x >= 0) or not (height > chunk_y >= 0):
                    chunks[y][x] = None
                    continue

                chunk = TerrainChunk((chunk_x , chunk_y), this.path, this.texture_sheet)
                _, chunk_arr = chunk.load(this.img_size, (this.width, this.height))
                chunks[y][x] = chunk
                chunks_arr[chunk_y][chunk_x] = chunk_arr

            this.chunks = chunks
            this.chunks_arr = chunks_arr
            this.chunk_pos_x = chunk_pos_x
            this.chunk_pos_y = chunk_pos_y

    def draw_pos(this, position, win):
        """
        Vykreslí chunky okolo pozice(position) do okna(win)
        """
        x = position[0]
        y = position[1]

        chunks = this.chunks

        this.load_pos(position)

        i = 0
        i_range = range(-1, 2)
        for x_row in chunks:
            for chunk in x_row:
                # print("Terrain/drawpos: ", position)
                x_tuple = tuple(x + y for x, y in zip(position, (this.chunk_pos_x, this.chunk_pos_y)))
                if chunk:
                    chunk.draw(win, position, this.img_size)
            i += 1

    """
    Terrain file format 

    0 img_size
    1 width
    2 height
    """

    def create_terrain(this, img_size, height, width):
        os.mkdir(this.path.replace("\\", "/"))

        with open(f'{this.path}/settings.txt', 'w+') as f:
            f.write(f"{img_size}\n")
            f.write(f"{width}\n")
            f.write(f"{height}\n")

        this.img_size = img_size
        this.width = width
        this.height = height

    def load_file(this, path):
        with open(f'{this.path}/settings.txt', 'rb') as f:
            this.img_size = int(f.readline())
            this.width = int(f.readline())
            this.height = int(f.readline())

class TerrainChunk:
    def __init__(this, position: (int, int), terrain_path: str, terrain_texture_sheet):
        this.x = position[0]
        this.y = position[1]
        this.terrain_path = terrain_path
        this.terrain_sheet = terrain_texture_sheet

    def load(this, img_size, terrain_size):
        x = this.x
        y = this.y

        t_path = this.terrain_path.replace("\\", "/")
        path = f'{t_path}/{x}_{y}.npy'

        if not os.path.exists(path):
            print(f"ERROR: chunk neexistuje: {x}, {y}")
            if is_editor:
                print(f"LOG: vytvářím nový")
                with open(path, 'wb') as f:
                    array = np.save(f, terrain_generation.generate_chunk((x, y), terrain_size), allow_pickle=True) #np.save(f, np.zeros((16, 16)), allow_pickle=True)
            else:
                return

        with open(path, 'rb') as f:
            array = np.load(f)

        terrain_sheet = this.terrain_sheet.images
        line_size = 16 * img_size
        texture = pygame.Surface((line_size, line_size))
        
        i = 0
        for y in array:
            for x in y:
                x = int(x)
                #replace x with index
                texture.blit(terrain_sheet[x], ((i % 16) * img_size, math.floor(i/16) * img_size))
                i += 1

        this.texture = texture
        return (texture, array)

    def draw(this, win, position, img_size):
        # print(this.x, this.y)
        win.blit(this.texture, tuple((x*img_size*16+y) for x, y in zip((this.x, this.y), position)))

# Texture Sheet
class TextureSheet:
    def __init__(this, path, img_size):
        sheet = pygame.image.load(path)

        if sheet:
            this.path = path
            this.sheet = sheet
            this.images = []
            this.img_size = img_size

            sheet_size = tuple(math.floor(x / img_size) for x in sheet.get_size())
            for y in range(sheet_size[1]):
                y *= img_size

                for x in range(sheet_size[0]):
                    i = x + math.floor(y/img_size) * sheet_size[1]
                    x *= img_size

                    this.load_area_at((x, y), img_size, i)            

    def load_area_at(this, position, img_size, index=0):
        """
        Načte obrázek z tabulky textur
        Vrátí Surface
        """
        sheet = this.sheet
        img = pygame.Surface((img_size, img_size))

        for x in range(position[0], position[0] + img_size):
            for y in range(position[1], position[1] + img_size):
                pos = (x, y)
                pixel_pos = (x - position[0], y - position[1])
                color = sheet.get_at(pos)
                img.set_at(pixel_pos, color)

        this.images.insert(index, img)
        return img
                


TERRAIN_TEXTURE_SHEET = TextureSheet(os.path.join(f"{os.getcwd()}/pygame/Assets/Images", "texture_sheet.png"), 55)

if __name__ == "__main__":
    WIN = pygame.display.set_mode((800, 600))
    WHITE = 255,255,255
    font = pygame.font.SysFont('Calibri', 30)

    clock = pygame.time.Clock()
    run = True
    i = 0
    ui = font.render('0', False, WHITE)

    while run:
        clock.tick(4)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: run = False

        WIN.fill((0, 0, 0))
        ui.fill((0, 0, 0))
        ui = font.render(str(i), False, WHITE)

        WIN.blit(TERRAIN_TEXTURE_SHEET.images[i], (400, 300))
        WIN.blit(ui, (0, 0))

        i += 1
        pygame.display.update()

    pygame.quit()
