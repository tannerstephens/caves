#!/usr/bin/python3

from opensimplex import OpenSimplex
import pygame

def count_true_neighbors(x,y,base):
  count = 0  
  for dx in range(-1,2):
    for dy in range(-1,2):
      if dx == 0 and dy == 0:
        count += 1
        continue

      look_x = x + dx
      look_y = y + dy

      if look_x < 0 or look_x >= len(base) or look_y < 0 or look_y >= len(base[0]):
        continue

      if base[look_x][look_y]:
        count += 1

  return count


def generate_cave(width=100, height=100, seed=None, threshold=0, steps=4):
  if seed:
    simplex = OpenSimplex(seed=seed)
  else:
    simplex = OpenSimplex()

  width -= 2
  height -= 2

  base = [[None for _ in range(height)] for _ in range(width)]

  for y in range(height):
    for x in range(width):
      n = simplex.noise2d(x,y)
      base[x][y] = True if n > threshold else False

  for step in range(steps):
    new = [[None for _ in range(height)] for _ in range(width)]

    for x, col in enumerate(base):
      for y, cell in enumerate(col):
        count = count_true_neighbors(x,y,base)
        if count >= 5:
          new[x][y] = True
        else:
          new[x][y] = False
  
    base = new[:]

  for x in range(width):
    base[x] = [True] + base[x] + [True]
  
  base = [[True]*len(base[0])] + base + [[True]*len(base[0])]

  return base

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

def explore_caves(seed=4651564651564984444651464648901):
  width = 100
  height = 100
  scale = 8
  threshold = 0.11
  steps = 5

  pygame.init()

  pygame.display.set_caption("Cave Display")
  screen = pygame.display.set_mode((width*scale, height*scale))

  running = True

  cave = generate_cave(width, height, seed, threshold, steps)
  display_cave(cave, screen, scale)

  re_render = False

  while running:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
      elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
          steps = max((steps-1, 0))
          re_render = True
        elif event.key == pygame.K_RIGHT:
          steps += 1
          re_render = True
        elif event.key == pygame.K_SPACE:
          print(threshold, steps)
        elif event.key == pygame.K_UP:
          threshold = min((threshold+0.01, 1))
          re_render = True
        elif event.key == pygame.K_DOWN:
          threshold = max((threshold-0.01, -1))
          re_render = True

    if re_render:
      re_render = False   
      cave = generate_cave(width, height, seed, threshold, steps)
      display_cave(cave, screen, scale)
          
  
  pygame.quit()
