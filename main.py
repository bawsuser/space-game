#sudo apt-get install python3-pygame
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
PU_CHANCE = 150
COIN_CHANCE = 1500
FPS = 60
WIDTH = 1280
HEIGHT = 720

# runs pg from here
# runs game from spaceship.py
clock = pg.time.Clock()
pg.init()

# asset caches — load each file/font once and reuse.
# Loading sounds/images from disk every frame was the main cause of stuttering.
_image_cache = {}
_sound_cache = {}
_font_cache = {}

def get_image(path):
    img = _image_cache.get(path)
    if img is None:
        img = pg.image.load(path).convert_alpha()
        _image_cache[path] = img
    return img

def get_sound(path):
    snd = _sound_cache.get(path)
    if snd is None:
        snd = pg.mixer.Sound(path)
        _sound_cache[path] = snd
    return snd

def get_font(name, size):
    key = (name, size)
    f = _font_cache.get(key)
    if f is None:
        f = pg.font.SysFont(name, size)
        _font_cache[key] = f
    return f

# program submenu for resolution and fullscreen

