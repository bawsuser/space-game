from random import randint, choice
from time import sleep, time
import sqlite3
import math
from pygame import gfxdraw
import pygame as pg
#from game_loop import Game
from game_loop import *

ASTEROID_SPAWN_FACTOR = 0.99
DIFFICULTY_SCORE_BARRIER = 100
PU_CHANCE = 300
COIN_CHANCE = 1500
FPS = 60
WIDTH = 1280
HEIGHT = 720

# runs pg from here
# runs game from spaceship.py
clock = pg.time.Clock()
pg.init()
disp = pg.display.set_mode([WIDTH, HEIGHT])

# program submenu for resolution and fullscreen

