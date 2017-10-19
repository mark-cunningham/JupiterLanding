#!/usr/bin/python
# Jupiter Landing
# Code Angel


import sys
import os
import pygame
from pygame.locals import *
import random
import math

# Define the colours
GREEN = (84, 216, 61)
AMBER = (255, 153, 0)

# Define constants
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

DATA_DISPLAY_LEFT = 16
TEXT_LINE_SPACE = 24

FUEL_WARNING = 50
KGRAVITY = 0.01

MAX_TERRAIN_HEIGHT = 120
MIN_TERRAIN_HEIGHT = 90
LEFT_BUFFER_ZONE = 36
RIGHT_BUFFER_ZONE = 12

LANDER_START_Y = 40
ROTATE_ANGLE = 4

# Setup
os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()
pygame.init()
game_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Jupiter Landing')
pygame.key.set_repeat(10, 20)
clock = pygame.time.Clock()
font = pygame.font.SysFont('Courier', 16)

# Load images
background_image = pygame.image.load('background.png').convert()

planet_high_low_image = pygame.image.load('planet_high_low.png').convert_alpha()
planet_high_mid_image = pygame.image.load('planet_high_mid.png').convert_alpha()
planet_low_high_image = pygame.image.load('planet_low_high.png').convert_alpha()
planet_low_mid_image = pygame.image.load('planet_low_mid.png').convert_alpha()
planet_mid_image = pygame.image.load('planet_mid.png').convert_alpha()
planet_mid_high_image = pygame.image.load('planet_mid_high.png').convert_alpha()
planet_mid_low_image = pygame.image.load('planet_mid_low.png').convert_alpha()
planet_blank_image = pygame.image.load('planet_blank.png').convert_alpha()
planet_landing_block_image = pygame.image.load('planet_landing_block.png').convert_alpha()

lander_image = pygame.image.load('lander.png').convert_alpha()
thrust_image = pygame.image.load('thrust_lander.png').convert_alpha()
exploded_lander_image = pygame.image.load('exploded_lander.png').convert_alpha()

# Load sounds
thrust_sound = pygame.mixer.Sound('thrust.ogg')
explosion_sound = pygame.mixer.Sound('explosion.ogg')
landed_sound = pygame.mixer.Sound('landed.ogg')