import numpy as np
import perlin_noise

def generate_chunk(position: tuple[int, int], terrain_size: tuple[int, int], rng: tuple[int, int] = (0, 5), seed: int = 123456789):
    array = np.zeros((16, 16))

    divider = max(position[1], 1)
    #final_seed = seed + sum(position) * (int(position[0] / divider) * 1000)
    noise = perlin_noise.PerlinNoise(octaves=10, seed=seed)

    """
    0 - grass 3
    1 - dirt 2
    2 - stone 1
    3 - ore (33 - 35)
    4 - ore 
    """
    texture_map = [3, 2, 1, 33, 34, 35]

    chunk_x = position[0] / terrain_size[0]
    chunk_y = position[1] / terrain_size[1]

    new_array = []
    for y in range(len(array)):
        new_line = []
        for x in range(len(array[0])):
            element = max(0, int(noise([((position[0] + 1) * (x + 1)) / (17 * (terrain_size[0] + 1)), ((position[1] + 1) * (y + 1)) / (17 * (terrain_size[1] + 1))]) * 10)) #random.randint(*rng)
            new_line.append(texture_map[element])
        new_array.append(new_line)

    return np.array(new_array)
