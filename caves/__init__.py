#!/usr/bin/python3

from opensimplex import OpenSimplex
import pygame
import random
import math

class Cave:
  def __init__(self, seed=None, threshold=-0.08, steps=5, chunk_size=50):
    self.threshold = threshold
    self.steps = steps
    self.chunk_size = chunk_size
    
    if seed == None:
      seed = random.getrandbits(100)

    self.simplex = OpenSimplex(seed=seed)
    self.chunks = dict()

  def load_chunk(self, x, y):
    if x not in self.chunks:
      self.chunks[x] = dict()
    
    if y not in self.chunks[x]:
      self._generate_chunk(x,y)
    
    return self.chunks[x][y]

  def _generate_chunk(self, x, y):
    base_chunk = [[None for _ in range(self.chunk_size)] for _ in range(self.chunk_size)]

    for chunk_x in range(self.chunk_size):
      for chunk_y in range(self.chunk_size):
        real_x = x*self.chunk_size + chunk_x
        real_y = y*self.chunk_size + chunk_y

        noise = self.simplex.noise2d(real_x, real_y)

        base_chunk[chunk_x][chunk_y] = True if noise > self.threshold else False

    for _ in range(self.steps):
      new = [[None for _ in range(self.chunk_size)] for _ in range(self.chunk_size)]

      for cell_x in range(self.chunk_size):
        for cell_y in range(self.chunk_size):
          count = 0
          for dx in range(-1,2):
            for dy in range(-1,2):
              if dx == 0 and dy == 0:
                continue

              look_x = cell_x + dx
              look_y = cell_y + dy

              if look_x < 0 or look_x >= self.chunk_size or look_y < 0 or look_y >= self.chunk_size:
                noise = self.simplex.noise2d(look_x+chunk_x*self.chunk_size, look_y+chunk_y*self.chunk_size)
                noise2 = self.simplex.noise2d(look_x+chunk_x*self.chunk_size+dx, look_y+chunk_y*self.chunk_size+dy)
                count += 1 if noise > self.threshold and noise2 > self.threshold else 0
              elif base_chunk[look_x][look_y]:
                count += 1
          if count >= 5:
            new[cell_x][cell_y] = True
          else:
            new[cell_x][cell_y] = False
      base_chunk = new[:]

    self.chunks[x][y] = base_chunk

  def calculate_chunk_id(self, x, y):
    chunk_x = math.floor(x/self.chunk_size)
    chunk_y = math.floor(y/self.chunk_size)

    return (chunk_x, chunk_y)

  def load_area(self, left, top, width, height):
    chunk_x_start, chunk_y_start = self.calculate_chunk_id(left, top)
    chunk_x_end, chunk_y_end = self.calculate_chunk_id(left+width-1, top+height-1)
    chunk_x_end += 1
    chunk_y_end += 1

    result_width = self.chunk_size*abs(chunk_x_end-chunk_x_start)
    result_height = self.chunk_size*abs(chunk_y_end-chunk_y_start)

    loaded_area = [[None for _ in range(result_height)] for _ in range(result_width)]

    for chunk_x in range(chunk_x_start, chunk_x_end):
      for chunk_y in range(chunk_y_start, chunk_y_end):
        rel_x = chunk_x - chunk_x_start
        rel_y = chunk_y - chunk_y_start

        chunk = self.load_chunk(chunk_x, chunk_y)

        for x in range(self.chunk_size):
          for y in range(self.chunk_size):
            loaded_area[self.chunk_size*rel_x + x][self.chunk_size*rel_y + y] = chunk[x][y]

    result = [[None for _ in range(height)] for _ in range(width)]

    result_x_start = left - self.chunk_size*chunk_x_start
    result_y_start = top - self.chunk_size*chunk_y_start

    for x in range(width):
      for y in range(height):
        result[x][y] = loaded_area[result_x_start + x][result_y_start + y]
    
    return result

def display_cave(cave_array, screen, scale=2):
  width = len(cave_array)*scale
  height = len(cave_array[0])*scale

  screen.fill((0,0,0))

  for x, col in enumerate(cave_array):
    for y, cell in enumerate(col):
      if cell:
        r = pygame.Rect(x*scale, y*scale, scale, scale)

        screen.fill((165,165,165), rect=r)
  pygame.display.flip()

def explore_caves():
  width = 400
  height = 400
  scale = 2
  threshold = -0.08
  steps = 5
  seed = 1234

  pygame.init()

  pygame.display.set_caption("Cave Display")
  screen = pygame.display.set_mode((int(width*scale), int(height*scale)))

  running = True

  cave = Cave(seed=seed, threshold=threshold, steps=steps)
  generated_cave = cave.load_area(1, 1, width, height)
  display_cave(generated_cave, screen, scale)
  print("Displayed")

  while running:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False

  pygame.quit()
