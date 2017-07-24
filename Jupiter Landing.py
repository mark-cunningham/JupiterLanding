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
SCREENWIDTH = 640
SCREENHEIGHT = 480
LEFTMARGIN = 16
TEXTSPACE = 24
TERRAINBLOCKSIZE = 4
LANDERWIDTH = 24
LANDERHEIGHT = 24
MAXTERRAIN = 120
MINTERRAIN = 90
FUELWARNING = 50
KGRAVITY = 0.01
LANDER_START_Y = 40

# Setup
os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
game_screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption("Jupiter Landing")
pygame.key.set_repeat(10, 20)
clock = pygame.time.Clock()
font = pygame.font.SysFont("Courier", 12)

# Load images
background_image = pygame.image.load("background.png").convert()

planet_high_low_image = pygame.image.load("planet_high_low.png").convert_alpha()
planet_high_mid_image = pygame.image.load("planet_high_mid.png").convert_alpha()
planet_low_high_image = pygame.image.load("planet_low_high.png").convert_alpha()
planet_low_mid_image = pygame.image.load("planet_low_mid.png").convert_alpha()
planet_mid_image = pygame.image.load("planet_mid.png").convert_alpha()
planet_mid_high_image = pygame.image.load("planet_mid_high.png").convert_alpha()
planet_mid_low_image = pygame.image.load("planet_mid_low.png").convert_alpha()
planet_blank_image = pygame.image.load("planet_blank.png").convert_alpha()
planet_landing_block_image = pygame.image.load("planet_landing_block.png").convert_alpha()

lander_image = pygame.image.load("lander.png").convert_alpha()
boost_image = pygame.image.load("boost_lander.png").convert_alpha()
exploded_lander_image = pygame.image.load("exploded_lander.png").convert_alpha()

def main():

    # Initialise variables



    display_lander_image = lander_image

    lander_center_y = LANDER_START_Y
    angle = 0
    velocity_x = 0
    velocity_y = 0

    gravity = KGRAVITY
    fuel = 500

    rocket_boost = False
    exploded = False
    hit_terrain = False

    landing_blocks = 16
    landing_velocity = 1.0
    landing_angle = 24

    fuel_left = True
    velocity_ok = True
    landing_location_ok = True
    angle_ok = True
    on_screen = True
    landed = False

    level = 1
    score = 0
    new_score = 0


    

    planet_dict = setup_planet(landing_blocks)
    terrain = planet_dict['Terrain Blocks']
    terrain_y  = planet_dict['Terrain Blocks Y Coords']
    lander_center_x = planet_dict['Lander Start X']
    terrain_blocks = planet_dict['Number Terrain Blocks']
    landing_pad_block = planet_dict['Landing Pad']

    
   
    

    while True: # main game loop

        # Keypress events
        for event in pygame.event.get():
            key_pressed = pygame.key.get_pressed()

            # SPACE key pressed - rocket boost
            if key_pressed[pygame.K_SPACE]:
                rocket_boost = True
            else:
                rocket_boost = False

            if key_pressed[pygame.K_RIGHT]:
                angle = angle - 4
                if angle < -90:
                    angle = -90
            elif key_pressed[pygame.K_LEFT]:
                angle = angle + 4
                if angle > 90:
                    angle = 90

            if key_pressed[pygame.K_RETURN]:
                if landed is True:
                    level = level + 1
                    score = new_score
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
                        

                elif hit_terrain is True:
                    level = 1
                    score = 0
                    
                    fuel = 500

                lander_center_y = LANDER_START_Y
                angle = 0
                velocity_x = 0
                velocity_y = 0
                gravity = KGRAVITY
                rocket_boost = False
                exploded = False
                hit_terrain = False
                landed = False

                planet_dict = setup_planet(landing_blocks)
                terrain = planet_dict['Terrain Blocks']
                terrain_y  = planet_dict['Terrain Blocks Y Coords']
                lander_center_x = planet_dict['Lander Start X']
                terrain_blocks = planet_dict['Number Terrain Blocks']
                landing_pad_block = planet_dict['Landing Pad']
       

            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        

        lander_rect = display_lander_image.get_rect()

        lander_center_x = lander_center_x + velocity_x
        lander_left_x = lander_center_x - LANDERWIDTH/2
        lander_right_x = lander_center_x + LANDERWIDTH/2
        
        lander_center_y = lander_center_y + velocity_y
        lander_top_y = lander_center_y - LANDERWIDTH/2

        if lander_left_x < 0 or lander_right_x > SCREENWIDTH:
            velocity_x = 0
            exploded = True
            on_screen = False
            

        if lander_top_y < 0:
            velocity_x = 0
            velocity_y = 0
            exploded = True
            on_screen = False
            
        

        game_screen.blit(background_image, [0, 0])

        # display terrain
        for terrain_count in range(terrain_blocks):
            game_screen.blit(terrain[terrain_count], [terrain_count * TERRAINBLOCKSIZE, terrain_y[terrain_count] * TERRAINBLOCKSIZE])
            for planet_blocks in range(terrain_y[terrain_count] + 1, MAXTERRAIN):
                game_screen.blit(planet_blank_image, [terrain_count * TERRAINBLOCKSIZE, planet_blocks * TERRAINBLOCKSIZE])
                

        lander_rect.centerx = lander_center_x    
        lander_rect.centery = lander_center_y

        # check for collision
        for terrain_count in range(terrain_blocks):
            terrain_rect = pygame.Rect(terrain_count * TERRAINBLOCKSIZE, terrain_y[terrain_count] * TERRAINBLOCKSIZE, TERRAINBLOCKSIZE, TERRAINBLOCKSIZE)
            if lander_rect.colliderect(terrain_rect):
                hit_terrain = True

                if abs(velocity_x) > landing_velocity or velocity_y > landing_velocity:
                        exploded = True
                        velocity_ok = False

                elif abs(angle) > landing_angle:
                    exploded = True
                    angle_ok = False

                if lander_left_x >= (landing_pad_block - 1) * TERRAINBLOCKSIZE and lander_right_x <= (landing_pad_block + landing_blocks + 2) * TERRAINBLOCKSIZE:
                    if exploded is False:
                        landed = True
                    

                else:
                    exploded = True
                    landing_location_ok = False

                velocity_x = 0
                velocity_y = 0
                gravity = 0

                
        
        if exploded is False:
            if rocket_boost is True:
                velocity_y = velocity_y - 2 * gravity - math.cos(math.radians(angle)) * 2 * gravity
                velocity_x = velocity_x + 2 * gravity * math.sin(math.radians(-angle))
                display_lander_image = pygame.transform.rotate(boost_image, angle)

                fuel = fuel - 1
                if fuel == 0:
                    exploded = True
                    fuel_left = False
                    
            
            else:
                display_lander_image = pygame.transform.rotate(lander_image, angle)
        else:
            display_lander_image = pygame.transform.rotate(exploded_lander_image, angle)

     
        velocity_y = velocity_y + gravity


        game_screen.blit(display_lander_image, lander_rect)

        # landed messages
        if hit_terrain is True:
            if landed is True:
                display_successful_landing()
                return_message_text = "Hit return for next level"
                new_score = score + fuel * level + (landing_angle - abs(angle)) * 10 * level
                
            else:
                display_failed_landing(on_screen, fuel_left, velocity_ok, landing_location_ok, angle_ok)
                new_score = score
                return_message_text = "Hit return for new game"

            display_game_end(new_score, return_message_text)

        else:
            display_status(fuel, velocity_x, landing_velocity, velocity_y, angle, landing_angle, level)


        pygame.display.update()
        clock.tick(60)

def display_successful_landing():
    message_text = "Congratulations Commander, a successful landing."
    text = font.render(message_text, True, (GREEN))

    text_rect = text.get_rect()
    game_screen.blit(text, [(SCREENWIDTH - text_rect.width) / 2, (SCREENHEIGHT - text_rect.height) / 2 - TEXTSPACE * 6])



def display_failed_landing(on_screen, fuel_left, velocity_ok, landing_location_ok, angle_ok):
    message_text = "Commander, you failed to land the spacecraft"
    text = font.render(message_text, True, (GREEN))
    text_rect = text.get_rect()
    game_screen.blit(text, [(SCREENWIDTH - text_rect.width) / 2, (SCREENHEIGHT - text_rect.height) / 2 - TEXTSPACE * 6])

    fault_report_head = "Fault Report"
    text = font.render(fault_report_head, True, (AMBER))
    text_rect = text.get_rect()
    game_screen.blit(text, [(SCREENWIDTH - text_rect.width) / 2, (SCREENHEIGHT - text_rect.height) / 2 - TEXTSPACE * 3])

    fault_text = ""
    if on_screen is False:
        fault_text = fault_text + "Left planet orbit. "
    else:
        if fuel_left is False:
            fault_text = fault_text + "No fuel. "
        if velocity_ok is False:
            fault_text = fault_text + "Approach velocity too high. "
        if landing_location_ok is False:
            fault_text = fault_text + "Missed landing pad. "
        if angle_ok is False:
            fault_text = fault_text + "Approach angle too high. "

    text = font.render(fault_text, True, (AMBER))
    text_rect = text.get_rect()
    game_screen.blit(text, [(SCREENWIDTH - text_rect.width) / 2, (SCREENHEIGHT - text_rect.height) / 2 - TEXTSPACE * 2])

def display_game_end(score, message):
    score_text = "Your overall score is " + str(score)
    text = font.render(score_text, True, (GREEN))
    text_rect = text.get_rect()
    game_screen.blit(text, [(SCREENWIDTH - text_rect.width) / 2, (SCREENHEIGHT - text_rect.height) / 2 - TEXTSPACE * 5])

    text = font.render(message, True, (GREEN))
    text_rect = text.get_rect()
    game_screen.blit(text, [(SCREENWIDTH - text_rect.width) / 2, (SCREENHEIGHT - text_rect.height) / 2 + TEXTSPACE * 1])

def display_status(fuel, velocity_x, landing_velocity, velocity_y, angle, landing_angle, level):
    # display status
    fuel_text = "Fuel: " + str(fuel)
    if fuel < FUELWARNING:
        text = font.render(fuel_text, True, (AMBER))
    else:
        text = font.render(fuel_text, True, (GREEN))
    game_screen.blit(text, [LEFTMARGIN, TEXTSPACE * 2])

    h_velocity_text = "H Vel: " + str(round(velocity_x, 2))
    if abs(velocity_x) > landing_velocity:
        text = font.render(h_velocity_text, True, (AMBER))
    else:
        text = font.render(h_velocity_text, True, (GREEN))
    game_screen.blit(text, [LEFTMARGIN, TEXTSPACE * 3])

    v_velocity_text = "V Vel: " + str(round(velocity_y, 2))
    if velocity_y > landing_velocity:
        text = font.render(v_velocity_text, True, (AMBER))
    else:
        text = font.render(v_velocity_text, True, (GREEN))

    game_screen.blit(text, [LEFTMARGIN, TEXTSPACE * 4])

    angle_text = "Angle: " + str(-angle)
    if abs(angle) > landing_angle:
        text = font.render(angle_text, True, (AMBER))
    else:
        text = font.render(angle_text, True, (GREEN))
    game_screen.blit(text, [LEFTMARGIN, TEXTSPACE * 5])

    level_text = "Level: " + str(level)
    text = font.render(level_text, True, (GREEN))
    game_screen.blit(text, [LEFTMARGIN, TEXTSPACE * 6])


def setup_planet(landing_blocks):

    planet_images = {'HiLo': planet_high_low_image, 'HiMid': planet_high_mid_image, 'LoHi': planet_low_high_image,
                     'LoMid': planet_low_mid_image, 'Mid': planet_mid_image, 'MidLo': planet_mid_low_image,
                     'MidHi': planet_mid_high_image, 'Blank': planet_blank_image, 'Landing': planet_landing_block_image}
    
    terrain = []
    terrain_y = []
    terrain_name = []
    
    next_block_last_mid = ["mid", "higher", "lower"]
    next_block_last_higher = ["higher", "higher", "higher", "higher", "higher", "higher", "higher", "higher", "higher", "higher", "mid", "lower"]
    next_block_last_lower = ["lower", "lower", "lower", "lower", "lower", "lower", "lower", "lower", "lower", "lower", "mid", "higher"]
    last_block = "mid"
    terrain_y_coord = int(MAXTERRAIN - ((MAXTERRAIN - MINTERRAIN) / 2))

    terrain_y.append(terrain_y_coord)
    terrain.append(planet_images['Mid'])
    terrain_name.append("mid")

    terrain_blocks = int(SCREENWIDTH / TERRAINBLOCKSIZE)
    landing_pad_block = random.randint(36, terrain_blocks - 12 - landing_blocks)

    lander_center_x = random.randint(36, terrain_blocks - 12 - landing_blocks)
    while lander_center_x >= landing_pad_block - LANDERWIDTH and lander_center_x <= landing_pad_block + landing_blocks + LANDERWIDTH:
        lander_center_x = random.randint(36, terrain_blocks - 12 - landing_blocks) 
    lander_center_x = lander_center_x * TERRAINBLOCKSIZE

    
                                   
    for block in range(terrain_blocks):

        if block == landing_pad_block - 1 or block == landing_pad_block + landing_blocks:
            next_block = "mid"
        else:
            if last_block == "mid":
                next_block = random.choice(next_block_last_mid)
            elif last_block == "higher":
                next_block = random.choice(next_block_last_higher)
            elif last_block == "lower":
                next_block = random.choice(next_block_last_lower)
            
                
        if block >= landing_pad_block and block < landing_pad_block + landing_blocks:
            terrain_choice = planet_images['Landing']
        else:

            if last_block == "mid":
                if next_block == "mid":
                    terrain_choice = planet_images['Mid']
                    #terrain_name.append("mid")
                elif next_block == "higher":
                    terrain_choice = planet_images['MidHi']
                    #terrain_name.append("mid_high")
                elif next_block == "lower":
                    terrain_choice = planet_images['MidLo']
                    #terrain_name.append("mid_low")
                
            elif last_block == "higher":
                if next_block == "mid":
                    terrain_choice = planet_images['HiMid']
                    #terrain_name.append("high_mid")
                elif next_block == "higher":
                    terrain_choice = planet_images['LoHi']
                    #terrain_name.append("low_high")
                    terrain_y_coord = terrain_y_coord - 1
                elif next_block == "lower":
                    terrain_choice = planet_images['HiLo']
                    #terrain_name.append("high_low")
                
            elif last_block == "lower":
                if next_block == "mid":
                    terrain_choice = planet_images['LoMid']
                    #terrain_name.append("low_mid")
                elif next_block == "higher":
                    terrain_choice = planet_images['LoHi']
                    #terrain_name.append("low_high")
                elif next_block == "lower":
                    terrain_choice = planet_images['HiLo']
                    #terrain_name.append("high_low")
                    terrain_y_coord = terrain_y_coord + 1

        if terrain_y_coord > MAXTERRAIN - 1:
            terrain_y_coord = MAXTERRAIN - 1
            terrain_choice = planet_images['LoMid']
            # next_block = "mid"
            next_block = random.choice(next_block_last_higher)

        if terrain_y_coord < MINTERRAIN:
            terrain_y_coord = MINTERRAIN
            terrain_choice = planet_images['HiMid']
            # next_block = "mid"
            next_block = random.choice(next_block_last_lower)

        #terrain.append(planet_mid_image)
        #terrain_y.append(MAXTERRAIN - 1)
        
        terrain.append(terrain_choice)
        terrain_y.append(terrain_y_coord)

        last_block = next_block

    planet_dict = {'Terrain Blocks': terrain, 'Terrain Blocks Y Coords': terrain_y, 'Lander Start X': lander_center_x, 'Number Terrain Blocks': terrain_blocks, 'Landing Pad': landing_pad_block}
    return planet_dict


if __name__ == "__main__":

    main()
