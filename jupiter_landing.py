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


def main():

    # Initialise variables
    terrain_block_size = planet_blank_image.get_rect().width
    terrain_blocks = int(SCREEN_WIDTH / terrain_block_size)

    display_lander_image = lander_image
    lander_width = lander_image.get_rect().width

    fuel_left = True
    velocity_ok = True
    landing_location_ok = True
    angle_ok = True
    on_screen = True
    landed = False

    fuel = 500
    landing_blocks = 16
    landing_velocity = 1.0
    landing_angle = 24

    level = 1
    level_score = 0
    total_score = 0
    hi_score = 0

    planet = []

    lander_center_y = LANDER_START_Y
    angle = 0
    velocity_x = 0
    velocity_y = 0
    gravity = KGRAVITY
    rocket_thrust = False
    exploded = False
    level_end_sound_played = False
    hit_terrain = False

    # Random planet, landing pad and start location
    landing_pad_start = random_landing_pad_start(landing_blocks, terrain_blocks)
    setup_planet(planet, landing_pad_start, landing_blocks, terrain_blocks)
    lander_column = random_lander_loc(landing_pad_start, landing_blocks, terrain_blocks)
    lander_center_x = lander_column * terrain_block_size

    # Main game loop
    while True:

        for event in pygame.event.get():
            key_pressed = pygame.key.get_pressed()

            # SPACE key pressed - rocket thrust
            if key_pressed[pygame.K_SPACE]:
                rocket_thrust = True
            else:
                rocket_thrust = False

            # Left or right key pressed - rotate ship
            if key_pressed[pygame.K_RIGHT]:
                angle -= ROTATE_ANGLE
                if angle < -90:
                    angle = -90
            elif key_pressed[pygame.K_LEFT]:
                angle += ROTATE_ANGLE
                if angle > 90:
                    angle = 90

            # RETURN pressed and end of level/game
            if key_pressed[pygame.K_RETURN] and (landed or hit_terrain is True):

                # Successful landing - level up
                if landed is True:
                    level += 1
                    total_score += level_score

                    if level == 2:
                        fuel = 400
                        landing_blocks = 12
                        landing_velocity = 1.0
                        landing_angle = 24
                    elif level == 3:
                        fuel = 350
                        landing_blocks = 12
                        landing_velocity = 0.8
                        landing_angle = 20
                    elif level == 4:
                        fuel = 300
                        landing_blocks = 12
                        landing_velocity = 0.8
                        landing_angle = 16
                    elif level == 5:
                        fuel = 250
                        landing_blocks = 8
                        landing_velocity = 0.8
                        landing_angle = 12
                    elif level == 6:
                        fuel = 200
                        landing_blocks = 8
                        landing_velocity = 0.6
                        landing_angle = 8
                    else:
                        fuel = 200 - (level * 10)
                        landing_blocks = 6
                        landing_velocity = 0.5
                        landing_angle = 0

                # Crashed - back to level 1
                elif hit_terrain is True:
                    level = 1
                    total_score = 0
                    level_score = 0

                    landing_blocks = 16
                    landing_velocity = 1.0
                    landing_angle = 24
                    fuel = 500

                # Reset new game / new level variables
                lander_center_y = LANDER_START_Y
                angle = 0
                velocity_x = 0
                velocity_y = 0
                gravity = KGRAVITY
                rocket_thrust = False
                exploded = False
                level_end_sound_played = False
                hit_terrain = False
                landed = False

                fuel_left = True
                velocity_ok = True
                landing_location_ok = True
                angle_ok = True
                on_screen = True

                # Random planet, landing pad and start location
                landing_pad_start = random_landing_pad_start(landing_blocks, terrain_blocks)
                setup_planet(planet, landing_pad_start, landing_blocks, terrain_blocks)
                lander_column = random_lander_loc(landing_pad_start, landing_blocks, terrain_blocks)
                lander_center_x = lander_column * terrain_block_size

                pygame.mixer.stop()

            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # Update lander location
        lander_rect = display_lander_image.get_rect()

        lander_center_x += velocity_x
        lander_left_x = lander_center_x - lander_width / 2
        lander_right_x = lander_center_x + lander_width / 2
        
        lander_center_y += velocity_y
        lander_top_y = lander_center_y - lander_width / 2

        lander_rect.centerx = lander_center_x
        lander_rect.centery = lander_center_y

        # Check lander has not left screen left, right or top
        if lander_left_x < 0 or lander_right_x > SCREEN_WIDTH:
            velocity_x = 0
            exploded = True
            on_screen = False

        if lander_top_y < 0:
            velocity_x = 0
            velocity_y = 0
            exploded = True
            on_screen = False

        # Check for terrain collision by looping through all terrain blocks
        for block_number, block in enumerate(planet):

            terrain_y = block.get('terrain_y')
            block_x = block_number * terrain_block_size
            block_y = terrain_y * terrain_block_size

            terrain_rect = pygame.Rect(
                block_x,
                block_y,
                terrain_block_size,
                terrain_block_size)

            if lander_rect.colliderect(terrain_rect):
                hit_terrain = True

                # Check if landing velocity acceptable
                if abs(velocity_x) > landing_velocity or velocity_y > landing_velocity:
                    exploded = True
                    velocity_ok = False

                # Check if landing angle acceptable
                if abs(angle) > landing_angle:
                    exploded = True
                    angle_ok = False

                # Check if lander is within landing pad location
                landing_pad_left = (landing_pad_start - 1) * terrain_block_size
                landing_pad_right = (landing_pad_start + landing_blocks + 2) * terrain_block_size
                if lander_left_x >= landing_pad_left and lander_right_x <= landing_pad_right:
                    if exploded is False:
                        landed = True

                else:
                    exploded = True
                    landing_location_ok = False

                velocity_x = 0
                velocity_y = 0
                gravity = 0
                
        # Rocket thrust
        if exploded is False:

            # If rocket thrust, calculate new velocity
            if rocket_thrust is True:
                velocity_y = velocity_y - 2 * gravity - math.cos(math.radians(angle)) * 2 * gravity
                velocity_x += 2 * gravity * math.sin(math.radians(-angle))

                display_lander_image = pygame.transform.rotate(thrust_image, angle)

                # Reduce fuel
                fuel -= 1
                if fuel == 0:
                    exploded = True
                    fuel_left = False

                # Play thrust sound effect
                if pygame.mixer.get_busy() == 0:
                    thrust_sound.play()

            else:
                display_lander_image = pygame.transform.rotate(lander_image, angle)

                thrust_sound.stop()

        else:
            display_lander_image = pygame.transform.rotate(exploded_lander_image, angle)

        # Gravity affects the y velocity
        velocity_y += gravity

        # Display background
        game_screen.blit(background_image, [0, 0])

        # Display planet
        for block_number, block in enumerate(planet):
            terrain_type = block.get('terrain_type')
            terrain_y = block.get('terrain_y')

            block_x = block_number * terrain_block_size
            block_y = terrain_y * terrain_block_size

            game_screen.blit(terrain_type, [block_x, block_y])

            # Display blank blocks below terrain surface
            for blank_block in range(terrain_y + 1, MAX_TERRAIN_HEIGHT):
                block_x = block_number * terrain_block_size
                block_y = blank_block * terrain_block_size
                game_screen.blit(planet_blank_image, [block_x, block_y])

        # Display lander
        game_screen.blit(display_lander_image, lander_rect)

        # Landed messages
        if hit_terrain is True:
            if landed is True:
                display_successful_landing()
                return_message_text = 'Hit return for next level.'
                level_score = fuel * level + (landing_angle - abs(angle)) * 10 * level
                
            else:
                display_failed_landing(on_screen, fuel_left, velocity_ok, landing_location_ok, angle_ok)
                level_score = 0
                return_message_text = 'Hit return for new game.'

            if total_score + level_score > hi_score:
                hi_score = total_score + level_score

            display_game_end(level_score, total_score + level_score, hi_score, return_message_text)

        else:
            display_status(fuel, velocity_x, landing_velocity, velocity_y, angle, landing_angle, level)

        if exploded is True:
            if level_end_sound_played is False:
                explosion_sound.play()
                level_end_sound_played = True

        if landed is True:
            if level_end_sound_played is False:
                landed_sound.play()
                level_end_sound_played = True

        pygame.display.update()
        clock.tick(60)


# Successful landing message
def display_successful_landing():

    message_text = 'Congratulations Commander, a successful landing.'
    text = font.render(message_text, True, GREEN)

    text_rect = text.get_rect()
    message_x = (SCREEN_WIDTH - text_rect.width) / 2
    message_y = (SCREEN_HEIGHT - text_rect.height) / 2 - TEXT_LINE_SPACE * 6
    game_screen.blit(text, [message_x, message_y])


# Failed landing message
def display_failed_landing(on_screen, fuel_left, velocity_ok, landing_location_ok, angle_ok):

    message_text = 'Commander, you failed to land the spacecraft.'
    text = font.render(message_text, True, GREEN)

    text_rect = text.get_rect()
    message_x = (SCREEN_WIDTH - text_rect.width) / 2
    message_y = (SCREEN_HEIGHT - text_rect.height) / 2 - TEXT_LINE_SPACE * 7
    game_screen.blit(text, [message_x, message_y])

    fault_report_head = 'Fault Report'
    text = font.render(fault_report_head, True, AMBER)

    text_rect = text.get_rect()
    message_x = (SCREEN_WIDTH - text_rect.width) / 2
    message_y = (SCREEN_HEIGHT - text_rect.height) / 2 - TEXT_LINE_SPACE * 3
    game_screen.blit(text, [message_x, message_y])

    fault_text = ''
    if on_screen is False:
        fault_text += 'Left planet orbit'
    else:
        if fuel_left is False:
            fault_text += 'No fuel. '
        if velocity_ok is False:
            fault_text += 'Approach velocity. '
        if landing_location_ok is False:
            fault_text += 'Missed landing pad. '
        if angle_ok is False:
            fault_text += 'Approach angle. '

    text = font.render(fault_text, True, AMBER)
    text_rect = text.get_rect()
    message_x = (SCREEN_WIDTH - text_rect.width) / 2
    message_y = (SCREEN_HEIGHT - text_rect.height) / 2 - TEXT_LINE_SPACE * 2
    game_screen.blit(text, [message_x, message_y])


# End of game message
def display_game_end(level_score, game_score, hi_score, message):

    score_text = 'Level ' + str(level_score) + '  -  Game ' + str(game_score) + '  -  Hi ' + str(hi_score)
    text = font.render(score_text, True, GREEN)

    text_rect = text.get_rect()
    message_x = (SCREEN_WIDTH - text_rect.width) / 2
    message_y = (SCREEN_HEIGHT - text_rect.height) / 2 - TEXT_LINE_SPACE * 5
    game_screen.blit(text, [message_x, message_y])

    text = font.render(message, True, GREEN)
    text_rect = text.get_rect()
    message_x = (SCREEN_WIDTH - text_rect.width) / 2
    message_y = (SCREEN_HEIGHT - text_rect.height) / 2 + TEXT_LINE_SPACE * 1
    game_screen.blit(text, [message_x, message_y])


# On screen data display: Fuel, H Velocity, V Velocity, Angle and Level
def display_status(fuel, velocity_x, landing_velocity, velocity_y, angle, landing_angle, level):

    fuel_text = 'Fuel:  ' + str(fuel)
    if fuel < FUEL_WARNING:
        text = font.render(fuel_text, True, AMBER)
    else:
        text = font.render(fuel_text, True, GREEN)
    game_screen.blit(text, [DATA_DISPLAY_LEFT, TEXT_LINE_SPACE * 2])

    rounded_vel_x = round(velocity_x, 2)
    h_velocity_text = 'H Vel: ' + str(rounded_vel_x)
    if abs(velocity_x) > landing_velocity:
        text = font.render(h_velocity_text, True, AMBER)
    else:
        text = font.render(h_velocity_text, True, GREEN)
    game_screen.blit(text, [DATA_DISPLAY_LEFT, TEXT_LINE_SPACE * 3])

    rounded_vel_y = round(velocity_y, 2)
    v_velocity_text = 'V Vel: ' + str(rounded_vel_y)
    if velocity_y > landing_velocity:
        text = font.render(v_velocity_text, True, AMBER)
    else:
        text = font.render(v_velocity_text, True, GREEN)

    game_screen.blit(text, [DATA_DISPLAY_LEFT, TEXT_LINE_SPACE * 4])

    angle_text = 'Angle: ' + str(-angle)
    if abs(angle) > landing_angle:
        text = font.render(angle_text, True, AMBER)
    else:
        text = font.render(angle_text, True, GREEN)
    game_screen.blit(text, [DATA_DISPLAY_LEFT, TEXT_LINE_SPACE * 5])

    level_text = 'Level: ' + str(level)
    text = font.render(level_text, True, GREEN)
    game_screen.blit(text, [DATA_DISPLAY_LEFT, TEXT_LINE_SPACE * 6])


# Set up a planet terrain as list
def setup_planet(planet, landing_pad_start, landing_blocks, terrain_blocks):

    del planet[:]

    terrain_choice = ''

    planet_images = {'hi_lo': planet_high_low_image,
                     'hi_mid': planet_high_mid_image,
                     'lo_hi': planet_low_high_image,
                     'lo_mid': planet_low_mid_image,
                     'mid': planet_mid_image,
                     'mid_lo': planet_mid_low_image,
                     'mid_hi': planet_mid_high_image,
                     'blank': planet_blank_image,
                     'landing': planet_landing_block_image}
    
    new_block_last_mid = ['mid', 'higher', 'lower']

    new_block_last_higher = ['higher', 'higher', 'higher', 'higher',
                             'higher', 'higher', 'higher', 'higher',
                             'higher', 'higher', 'mid', 'lower']

    new_block_last_lower = ['lower', 'lower', 'lower', 'lower',
                            'lower', 'lower', 'lower', 'lower',
                            'lower', 'lower', 'mid', 'higher']

    last_block = 'mid'

    terrain_y_coord = int(MAX_TERRAIN_HEIGHT - ((MAX_TERRAIN_HEIGHT - MIN_TERRAIN_HEIGHT) / 2))

    first_planet_block = {'terrain_type': planet_images['mid'], 'terrain_y': terrain_y_coord}
    planet.append(first_planet_block)
                                   
    for block in range(terrain_blocks):

        if block == landing_pad_start - 1 or block == landing_pad_start + landing_blocks:
            new_block = 'mid'
        else:
            if last_block == 'mid':
                new_block = random.choice(new_block_last_mid)
            elif last_block == 'higher':
                new_block = random.choice(new_block_last_higher)
            elif last_block == 'lower':
                new_block = random.choice(new_block_last_lower)

        if landing_pad_start <= block < landing_pad_start + landing_blocks:
            terrain_choice = planet_images['landing']
        else:

            if last_block == 'mid':

                if new_block == 'mid':
                    terrain_choice = planet_images['mid']

                elif new_block == 'higher':
                    terrain_choice = planet_images['mid_hi']

                elif new_block == 'lower':
                    terrain_choice = planet_images['mid_lo']
                
            elif last_block == 'higher':

                if new_block == 'mid':
                    terrain_choice = planet_images['hi_mid']

                elif new_block == 'higher':
                    terrain_choice = planet_images['lo_hi']
                    terrain_y_coord -= 1

                elif new_block == 'lower':
                    terrain_choice = planet_images['hi_lo']
                
            elif last_block == 'lower':

                if new_block == 'mid':
                    terrain_choice = planet_images['lo_mid']

                elif new_block == 'higher':
                    terrain_choice = planet_images['lo_hi']

                elif new_block == 'lower':
                    terrain_choice = planet_images['hi_lo']
                    terrain_y_coord += 1

        if terrain_y_coord < MIN_TERRAIN_HEIGHT:
            terrain_y_coord = MIN_TERRAIN_HEIGHT
            terrain_choice = planet_images['hi_mid']
            new_block = random.choice(new_block_last_lower)

        if terrain_y_coord > MAX_TERRAIN_HEIGHT - 1:
            terrain_y_coord = MAX_TERRAIN_HEIGHT - 1
            terrain_choice = planet_images['lo_mid']
            new_block = random.choice(new_block_last_higher)

        terrain_block = {'terrain_type': terrain_choice, 'terrain_y': terrain_y_coord}
        planet.append(terrain_block)

        last_block = new_block


# Generate a random x column location for the landing pad
def random_landing_pad_start(landing_blocks, terrain_blocks):
    maximum_right_col = terrain_blocks - RIGHT_BUFFER_ZONE - landing_blocks
    landing_pad_start = random.randint(LEFT_BUFFER_ZONE, maximum_right_col)

    return landing_pad_start


# Generate a random starting x column for the lander
def random_lander_loc(landing_pad_start, landing_blocks, terrain_blocks):
    maximum_right_col = terrain_blocks - RIGHT_BUFFER_ZONE - landing_blocks
    lander_column = random.randint(LEFT_BUFFER_ZONE, maximum_right_col)

    while landing_pad_start <= lander_column <= landing_pad_start + landing_blocks:
        lander_column = random.randint(LEFT_BUFFER_ZONE, maximum_right_col)

    return lander_column

if __name__ == '__main__':

    main()
