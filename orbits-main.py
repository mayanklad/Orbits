import pygame
from pygame import gfxdraw
import math
import sys
import time
from random import *

# Define some colors
BLACK = pygame.Color(  0,   0,   0)
WHITE = pygame.Color(255, 255, 255)
RED   = pygame.Color(255,   0,   0)
GREEN = pygame.Color(  0, 255,   0)
BLUE  = pygame.Color(  0,   0, 255)

pygame.init()

# Set the height and width of the screen
size = [ pygame.display.Info().current_w, pygame.display.Info().current_h ]
screen = pygame.display.set_mode(size, pygame.FULLSCREEN | pygame.SRCALPHA)

status_surface = pygame.Surface([pygame.display.Info().current_w / 5, pygame.display.Info().current_h], pygame.SRCALPHA)

pygame.display.set_caption("Orbits")

background = pygame.image.load('space3.jpg').convert()
background = pygame.transform.scale(background, size)

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Starting position of the circle
circle_x = 50
circle_y = 50

planet = []
planet_color = pygame.Color(randint(0,255), randint(0,255), randint(0,255))
# Speed and direction of circle

dir_x = 0
dir_y = 0

theta = 0
alpha = 0

v = 5
a = 0
t = 1

b_r = 25
p_r = 5
p_m = pow(10, 14) / 500

G = 6.674 * pow(10, -11)
M = pow(10, 14)

mouseClicked1 = False
mouseClicked2 = False
eaten = False

# This is a font we use to draw text on the screen (size 36)
font = pygame.font.Font('freesansbold.ttf', 12)

# Use this boolean variable to trigger if the game is over.
game_over = False


def draw_circle(surface, color, center, radius, fill=False, border=False):
    if fill:
        gfxdraw.filled_circle(surface, int(center[0]), int(center[1]), radius, color)
        if border:
            gfxdraw.aacircle(surface, int(center[0]), int(center[1]), radius, color)
    else:
        gfxdraw.aacircle(surface, int(center[0]), int(center[1]), radius, color)

def draw_line(surface, color, p1, p2):
    pygame.draw.aaline(surface, color, p1, p2)
    
def angle(dy, dx):
    return math.atan2(dy, dx)

def collision(c1, r1, c2, r2):
    if (
        pow(c1[1] - c2[1], 2) + pow(c1[0] - c2[0], 2)
        <=
        pow(r1 + r2, 2)
    ):
        return True
    
    else:
        return False

def game_over_text():
    # Set the screen background
    screen.blit(background, (0, 0))
    # If game over is true, draw game over
    text = font.render("Black Hole Wins", True, WHITE)
    text_rect = text.get_rect()
    text_x = screen.get_width() / 2 - text_rect.width / 2
    text_y = screen.get_hei
    ght() / 2 - text_rect.height / 2
    screen.blit(text, [text_x, text_y])

def closing_animation():    
    for i in range(0, int(screen.get_width()/2) - 10):
        draw_circle(screen, BLACK, [int(screen.get_width()/2), int(screen.get_height()/2)], 10 + i + 1, True, True)
        pygame.display.flip()
    
    text = font.render("Black Hole Wins", True, WHITE)
    text_rect = text.get_rect()
    text_x = screen.get_width() / 2 - text_rect.width / 2
    text_y = screen.get_height() / 2 - text_rect.height / 2
    screen.blit(text, [text_x, text_y])
    pygame.display.flip()
    
    time.sleep(3)
    
def window_text():
    text = font.render("Press q to destroy universe", True, WHITE)
    text_rect = text.get_rect()
    #text_x = screen.get_width() / 2 - text_rect.width / 2
    #text_y = screen.get_height() / 2 - text_rect.height / 2
    screen.blit(text, [0, 0])

def update_acceleration(i):
    global planet
    a_x = 0
    a_y = 0
    alpha1 = 0
    a1 = 0
    if len(planet) > 0:
            for j in range(0, len(planet)):
                if j == i:
                    continue
                alpha1 = angle(planet[j]['y'] - planet[i]['y'], planet[j]['x'] - planet[i]['x'])
                a1 = \
                    (G * p_m) / (pow(planet[j]['y'] - planet[i]['y'], 2) + pow(planet[j]['x'] - planet[i]['x'], 2))
                a_x += a1 * math.cos(alpha1)
                a_y += a1 * math.sin(alpha1)


    #planet[i]['alpha'] = \
    #    angle(screen.get_height()/2 - planet[i]['y'], screen.get_width()/2 - planet[i]['x'])
    
    alpha1 = \
        angle(screen.get_height()/2 - planet[i]['y'], screen.get_width()/2 - planet[i]['x'])

    a1 = \
        (G * M) / (pow(screen.get_height()/2 - planet[i]['y'], 2) + pow(screen.get_width()/2 - planet[i]['x'], 2))
    
    a_x += a1 * math.cos(alpha1)
    a_y += a1 * math.sin(alpha1)

    #planet[i]['acceleration'] = \
    #    (G * M) / (pow(screen.get_height()/2 - planet[i]['y'], 2) + pow(screen.get_width()/2 - planet[i]['x'], 2))

    planet[i]['acceleration'] = math.sqrt(pow(a_x, 2) + pow(a_y, 2))
    planet[i]['alpha'] = angle(a_y, a_x)

def update_velocity(i):
    global planet
        
    planet[i]['velocity'] = \
        math.sqrt(
            pow( planet[i]['velocity'] * math.cos(planet[i]['theta']) + planet[i]['acceleration'] * math.cos(planet[i]['alpha']) * t, 2)
            + pow( planet[i]['velocity'] * math.sin(planet[i]['theta']) + planet[i]['acceleration'] * math.sin(planet[i]['alpha']) * t, 2)
        )
            
    planet[i]['theta'] = \
        angle(
            planet[i]['velocity'] * math.sin(planet[i]['theta']) + planet[i]['acceleration'] * math.sin(planet[i]['alpha']) * t,
            planet[i]['velocity'] * math.cos(planet[i]['theta']) + planet[i]['acceleration'] * math.cos(planet[i]['alpha']) * t
        )
            
def update_position(i):
    global planet
    
    planet[i]['x'] += (planet[i]['velocity'] * math.cos(planet[i]['theta']) * t) + (0.5 * planet[i]['acceleration'] * math.cos(planet[i]['alpha']) * pow(t, 2))
    planet[i]['y'] += (planet[i]['velocity'] * math.sin(planet[i]['theta']) * t) + (0.5 * planet[i]['acceleration'] * math.sin(planet[i]['alpha']) * pow(t, 2))

def initial_speed():
    global v
    v = math.sqrt( pow(circle_x - dir_x, 2) + pow(circle_y - dir_y, 2) ) * (1 / 10)

def speed_text(pos, vel=v):
    global planet
    
    text1 = font.render("{0:.2f}".format(vel), True, WHITE)
    text_rect1 = text1.get_rect()
    text_x1 = pos[0]
    text_y1 = pos[1] - text_rect1.height
    screen.blit(text1, [text_x1, text_y1])

def crossed_limit(var):
    if var >= 32700 or var<= -32700:
        return True
    else:
        return False

# -------- Main Program Loop -----------
while not done:
    
    # Limit frames per second
    clock.tick(60)

    # --- Event Processing
    for event in pygame.event.get():
        if (event.type == pygame.QUIT 
            or (event.type == pygame.KEYDOWN and event.key == pygame.K_q)
        ):               
            done = True
            game_over = True
        
        elif event.type == pygame.MOUSEMOTION:
            
            if mouseClicked1:
                dir_x, dir_y = event.pos
                initial_speed()
                
            else:
                circle_x, circle_y = event.pos
        
        elif event.type == pygame.MOUSEBUTTONUP:
            
            if not mouseClicked1:
                mouseClicked1 = True
                mouseClicked2 = False
                circle_x, circle_y = event.pos
                dir_x, dir_y = circle_x, circle_y
                            
            else:
                mouseClicked1 = False
                mouseClicked2 = True
                dir_x, dir_y = event.pos
                theta = angle(dir_y - circle_y, dir_x - circle_x)
                
                alpha = \
                    angle(screen.get_height()/2 - circle_y, screen.get_width()/2 - circle_x)
                
                a = \
                    (G * M) / (pow(screen.get_height()/2 - circle_y, 2) + pow(screen.get_width()/2 - circle_x, 2))
                
                planet.append( {'color': planet_color, 'x': circle_x, 'y': circle_y, 'velocity': v, 'theta': theta, 'acceleration': a, 'alpha': alpha} )
                circle_x, circle_y = dir_x, dir_y
                
                planet_color = (randint(0,255), randint(0,255), randint(0,255))
                
    # --- Game Logic

    if not eaten:
        # Actual logic
        if len(planet) > 0:
            p_i = 0
            while p_i < len(planet):
                if collision( (screen.get_width()/2, screen.get_height()/2), b_r,
                            (planet[p_i]['x'], planet[p_i]['y']), p_r
                ): 
                    del planet[p_i]          
                else:
                    update_position(p_i)
                    if crossed_limit(planet[p_i]['x']) or crossed_limit(planet[p_i]['y']):
                        del planet[p_i]
                    else:
                        update_acceleration(p_i)           
                        update_velocity(p_i)
                        p_i += 1
            
        # --- Draw the frame

        # Set the screen background
        #screen.blit(background, (0, 0))
        screen.fill((50, 50, 50))
        status_surface.fill((0, 0, 0, 112))
        
        # Draw the shapes
        '''
        draw_circle(screen, (0, 0, 0, 56), [screen.get_width()/2, screen.get_height()/2], 100, True)
        draw_circle(screen, (0, 0, 0, 112), [screen.get_width()/2, screen.get_height()/2], 70, True)
        draw_circle(screen, (0, 0, 0, 170), [screen.get_width()/2, screen.get_height()/2], 40, True)
        '''
        for i in range(1, 50):
            draw_circle(screen, (0, 0, 0, i), [screen.get_width()/2, screen.get_height()/2], 50-i, True)
        draw_circle(screen, BLACK, [screen.get_width()/2, screen.get_height()/2], 20, True)
                
        if mouseClicked1 and not mouseClicked2:
            draw_line(screen, WHITE, [circle_x, circle_y], [dir_x, dir_y])
            speed_text([dir_x, dir_y], v)
        
        if len(planet) > 0:
            for i in range(0, len(planet)):
                draw_line(screen, WHITE, [planet[i]['x'], planet[i]['y']], [planet[i]['x'] + 25, planet[i]['y'] - 10])
                speed_text([planet[i]['x'] + 25, planet[i]['y'] - 10], planet[i]['velocity'])
                draw_circle(screen, planet[i]['color'], [planet[i]['x'], planet[i]['y']], 5, True, True)
                draw_circle(status_surface, planet[i]['color'], [10, 35+(i*15)], 5, True, True)
        draw_circle(screen, planet_color, [circle_x, circle_y], 5, True, True)
        screen.blit(status_surface, (0, 0))

    # Till window is not closed, draw this stuff.
    if not done:
        window_text()
        pygame.display.flip()
    else:
        closing_animation()


# on exit.
pygame.quit()
sys.exit(0)