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

  def break_block(self, x, y):
    chunk_x, chunk_y = self.calculate_chunk_id(x, y)
    chunk = self.load_chunk(chunk_x, chunk_y)

    look_x = x - self.chunk_size*chunk_x
    look_y = y - self.chunk_size*chunk_y

    chunk[look_x][look_y] = False

    self.chunks[chunk_x][chunk_y] = chunk



  def is_accessable(self, x, y):
    chunk_x, chunk_y = self.calculate_chunk_id(x, y)

    chunk = self.load_chunk(chunk_x, chunk_y)

    look_x = x - self.chunk_size*chunk_x
    look_y = y - self.chunk_size*chunk_y

    return not chunk[look_x][look_y]

  def load_chunk(self, chunk_x, chunk_y):
    if chunk_x not in self.chunks:
      self.chunks[chunk_x] = dict()
    
    if chunk_y not in self.chunks[chunk_x]:
      self._generate_chunk(chunk_x,chunk_y)
    
    chunk = self.chunks[chunk_x][chunk_y]

    return chunk

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

def display_cave(cave_array, screen, player_direction, scale=2):
  width = len(cave_array)*scale
  height = len(cave_array[0])*scale

  screen.fill((0,0,0))

  for x, col in enumerate(cave_array):
    for y, cell in enumerate(col):
      if cell:
        r = pygame.Rect(x*scale, y*scale, scale, scale)

        screen.fill((165,165,165), rect=r)

  r = pygame.Rect(math.floor((width-scale)/2), math.floor((height-scale)/2), scale, scale)
  screen.fill((255,0,0), rect=r)


  if player_direction == 0 or player_direction == 0.5 or player_direction == 3.5:
    r = pygame.Rect(math.floor((width-scale)/2), math.floor((height-scale)/2), scale, max((scale//8, 1)))
    screen.fill((0,255,0), rect=r)
  if player_direction == 1 or player_direction == 0.5 or player_direction == 1.5:
    r = pygame.Rect(max((math.floor((width-scale)/2) + (scale - scale//8), 1)), math.floor((height-scale)/2), max((scale//8, 1)), scale)
    screen.fill((0,255,0), rect=r)
  if player_direction == 2 or player_direction == 1.5 or player_direction == 2.5:
    r = pygame.Rect(math.floor((width-scale)/2), max((math.floor((height-scale)/2) + (scale - scale//8), 1)), scale, max((scale//8, 1)))
    screen.fill((0,255,0), rect=r)
  if player_direction == 3 or player_direction == 2.5 or player_direction == 3.5:
    r = pygame.Rect(math.floor((width-scale)/2), math.floor((height-scale)/2), max((scale//8, 1)), scale)
    screen.fill((0,255,0), rect=r)

  

  pygame.display.flip()

def calculate_direction(dx, dy, d):
  if dx == 0:
    if dy == 0:
      return math.floor(d)
    elif dy == -1:
      return 0
    elif dy == 1:
      return 2
  elif dx == 1:
    if dy == 0:
      return 1
    elif dy == -1:
      return 0.5
    elif dy == 1:
      return 1.5
  elif dx == -1:
    if dy == 0:
      return 3
    elif dy == -1:
      return 3.5
    elif dy == 1:
      return 2.5

def explore_caves():
  width = 51
  height = 51
  scale = 16
  threshold = -0.1
  steps = 4

  player_x = 0
  player_y = 0

  pygame.init()

  pygame.display.set_caption("Cave Display")
  screen = pygame.display.set_mode((int(width*scale), int(height*scale)))

  running = True
  redraw = True

  cave = Cave(threshold=threshold, steps=steps, chunk_size=16)
  
  while not cave.is_accessable(player_x, player_y):
    player_y += 1

  dx = 0
  dy = 0
  d = 0

  MOVEEVENT = pygame.USEREVENT+1
  pygame.time.set_timer(MOVEEVENT, 50)

  while running:
    generated_cave = cave.load_area(player_x - 25, player_y - 25, width, height)
    display_cave(generated_cave, screen, d, scale)

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
      elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_w or event.key == pygame.K_UP:
          dy = -1
        elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
          dy = 1
        elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
          dx = -1
        elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
          dx = 1
        elif event.key = pygame.K_SPACE:
          if d == 0:
            lx = 0
            ly = -1
          elif d == 1:
            lx = 1
            ly = 0
          elif d == 2:
            lx = 0
            ly = 1
          elif d == 3:
            lx = -1
            ly = 0

          cave.break_block(player_x + lx, player_y + ly)
          
      elif event.type == pygame.KEYUP:
        if event.key == pygame.K_w or event.key == pygame.K_UP:
          dy = 0
        elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
          dy = 0
        elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
          dx = 0
        elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
          dx = 0
      elif event.type == MOVEEVENT:
        d = calculate_direction(dx, dy, d)
        if dx != 0 or dy != 0:
          if cave.is_accessable(player_x+dx, player_y):
            player_x += dx
            redraw = True
          if cave.is_accessable(player_x, player_y+dy):
            player_y += dy
            redraw = True

  pygame.quit()
