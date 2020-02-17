"""
-*- coding: utf-8 -*-
----------------------------------------------
--- Author         : Mayank Lad
--- Mail           : mayanklad12@gmail.com
--- Github         : mayanklad
----------------------------------------------
"""
#Imports
#import sys
import time
import math
from random import randint
import pygame
from pygame import gfxdraw

class Orbits:
    """Main Class"""
    def __init__(self):

        # Define some colors
        self.BLACK = pygame.Color(  0,   0,   0)
        self.WHITE = pygame.Color(255, 255, 255)
        self.RED   = pygame.Color(255,   0,   0)
        self.GREEN = pygame.Color(  0, 255,   0)
        self.BLUE  = pygame.Color(  0,   0, 255)

        pygame.init()

        # Set the height and width of the screen
        self.size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
        self.screen = pygame.display.set_mode(self.size, pygame.FULLSCREEN | pygame.SRCALPHA)

        self.status_surface = pygame.Surface(
            [pygame.display.Info().current_w / 5, pygame.display.Info().current_h], pygame.SRCALPHA)

        pygame.display.set_caption("Orbits")

        #background = pygame.image.load('space3.jpg').convert()
        #background = pygame.transform.scale(background, size)

        # Loop until the user clicks the close button.
        self.done = False

        # Used to manage how fast the screen updates
        self.clock = pygame.time.Clock()

        # Starting position of the circle
        self.circle_x = 50
        self.circle_y = 50

        self.planet = []
        self.planet_color = pygame.Color(randint(0, 255), randint(0, 255), randint(0, 255))

        # Speed and direction of circle
        self.dir_x = 0
        self.dir_y = 0

        self.theta = 0
        self.alpha = 0

        self.v = 5
        self.a = 0
        self.t = 1

        self.b_r = 25
        self.p_r = 5
        self.p_m = pow(10, 14) / 500

        self.G = 6.674 * pow(10, -11)
        self.M = pow(10, 14)

        self.mouseClicked1 = False
        self.mouseClicked2 = False
        self.eaten = False

        # This is a font we use to draw text on the screen (size 36)
        #font = pygame.font.Font('freesansbold.ttf', 12)

        # Use this boolean variable to trigger if the game is over.
        self.game_over = False

        if __name__ == 'orbits_main':
            self.main()


    def draw_circle(self, surface, color, center, radius, fill=False, border=False):
        """Draw Circle"""
        if fill:
            gfxdraw.filled_circle(surface, int(center[0]), int(center[1]), radius, color)
            if border:
                gfxdraw.aacircle(surface, int(center[0]), int(center[1]), radius, color)
        else:
            gfxdraw.aacircle(surface, int(center[0]), int(center[1]), radius, color)

    def draw_line(self, surface, color, p1, p2):
        """Draw line"""
        pygame.draw.aaline(surface, color, p1, p2)

    def distance(self, p1, p2):
        """Calculate distance between two points"""
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def angle(self, dy, dx):
        """Calculate slope of vector"""
        return math.atan2(dy, dx)

    def collision(self, c1, r1, c2, r2):
        """Check Collision of planet and black hole"""
        return bool(pow(c1[1] - c2[1], 2) + pow(c1[0] - c2[0], 2) <= pow(r1 + r2, 2))

    def update_acceleration(self, i):
        """Update acceleration of planet"""
        a_x = 0
        a_y = 0
        alpha = 0
        a = 0

        if len(self.planet) > 0:
            for j in range(0, len(self.planet)):
                if j == i:
                    continue
                alpha = self.angle(
                    self.planet[j]['y'] - self.planet[i]['y'],
                    self.planet[j]['x'] - self.planet[i]['x'])
                a = (self.G * self.p_m) / (
                    pow(self.planet[j]['y'] - self.planet[i]['y'], 2)
                    + pow(self.planet[j]['x'] - self.planet[i]['x'], 2))
                a_x += a * math.cos(alpha)
                a_y += a * math.sin(alpha)

        alpha = self.angle(
            self.screen.get_height()/2 - self.planet[i]['y'],
            self.screen.get_width()/2 - self.planet[i]['x'])

        a = (self.G * self.M) / (
            pow(self.screen.get_height()/2 - self.planet[i]['y'], 2)
            + pow(self.screen.get_width()/2 - self.planet[i]['x'], 2))

        a_x += a * math.cos(alpha)
        a_y += a * math.sin(alpha)
        self.planet[i]['acceleration'] = math.sqrt(pow(a_x, 2) + pow(a_y, 2))
        self.planet[i]['alpha'] = self.angle(a_y, a_x)

    def update_velocity(self, i):
        """Update velocity of planet"""
        self.planet[i]['velocity'] = math.sqrt(
            pow(self.planet[i]['velocity'] * math.cos(self.planet[i]['theta'])
            + self.planet[i]['acceleration'] * math.cos(self.planet[i]['alpha']) * self.t, 2)
            + pow(self.planet[i]['velocity'] * math.sin(self.planet[i]['theta'])
            + self.planet[i]['acceleration'] * math.sin(self.planet[i]['alpha']) * self.t, 2))

        self.planet[i]['theta'] = self.angle(
            self.planet[i]['velocity'] * math.sin(self.planet[i]['theta'])
            + self.planet[i]['acceleration'] * math.sin(self.planet[i]['alpha']) * self.t,
            self.planet[i]['velocity'] * math.cos(self.planet[i]['theta'])
            + self.planet[i]['acceleration'] * math.cos(self.planet[i]['alpha']) * self.t)

    def update_position(self, i):
        """Update position of planet"""
        self.planet[i]['x'] += (
            (self.planet[i]['velocity'] * math.cos(self.planet[i]['theta']) * self.t)
            + (
                0.5
                * self.planet[i]['acceleration'] * math.cos(self.planet[i]['alpha'])
                * pow(self.t, 2)))

        self.planet[i]['y'] += (
            (self.planet[i]['velocity'] * math.sin(self.planet[i]['theta']) * self.t)
            + (
                0.5
                * self.planet[i]['acceleration'] * math.sin(self.planet[i]['alpha'])
                * pow(self.t, 2)))

    def initial_speed(self):
        """Calculate initial speed of planet"""
        self.v = (1 / 10) * math.sqrt(
            pow(self.circle_x - self.dir_x, 2)
            + pow(self.circle_y - self.dir_y, 2))

    def game_over_text(self, fsize=40):
        """Text to print when game is over"""
        # Set the screen background
        #screen.blit(background, (0, 0))
        self.screen.fill((50, 50, 50))
        # If game over is true, draw game over
        font = pygame.font.Font('freesansbold.ttf', fsize)
        text = font.render("Black Hole Wins", True, self.WHITE)
        text_rect = text.get_rect()
        text_x = self.screen.get_width() / 2 - text_rect.width / 2
        text_y = self.screen.get_hei
        self.screen.blit(text, [text_x, text_y])

    def closing_animation(self, fsize=40):
        """Closing Animation"""
        for i in range(0, int(self.screen.get_width()/2) - 10):
            self.draw_circle(
                self.screen,
                self.BLACK,
                [int(self.screen.get_width()/2), int(self.screen.get_height()/2)],
                10 + i + 1,
                True,
                True)
            pygame.display.flip()

        font = pygame.font.Font('freesansbold.ttf', fsize)
        text = font.render("Black Hole Wins", True, self.WHITE)
        text_rect = text.get_rect()
        text_x = self.screen.get_width() / 2 - text_rect.width / 2
        text_y = self.screen.get_height() / 2 - text_rect.height / 2
        self.screen.blit(text, [text_x, text_y])
        pygame.display.flip()

        time.sleep(3)

    def main_surface_text(self, fsize=20):
        """Main surface text"""
        font = pygame.font.Font('freesansbold.ttf', fsize)
        text = font.render("Press q to destroy universe", True, (200, 200, 200))
        self.screen.blit(text, [0, 0])

    def status_surface_text(self, fsize=12):
        """Status surface text"""
        font = pygame.font.Font('freesansbold.ttf', fsize)
        text1 = font.render("PLANET", True, self.WHITE)
        text2 = font.render("SPEED", True, self.WHITE)
        text3 = font.render("DISTANCE", True, self.WHITE)
        sub_part = self.status_surface.get_width() / 3
        text_x1 = 10
        text_x2 = sub_part
        text_x3 = sub_part * 2
        text_y1 = text_y2 = text_y3 = 35
        self.status_surface.blit(text1, [text_x1, text_y1])
        self.status_surface.blit(text2, [text_x2, text_y2])
        self.status_surface.blit(text3, [text_x3, text_y3])

    def distance_text(self, surface, pos, i, fsize=12):
        """Display planet's distance from black hole"""
        dis = self.distance(
            [self.planet[i]['x'], self.planet[i]['y']],
            [self.screen.get_width()/2, self.screen.get_height()/2])

        font = pygame.font.Font('freesansbold.ttf', fsize)
        text1 = font.render("{0:.2f}".format(dis), True, self.WHITE)
        text_rect1 = text1.get_rect()
        text_x1 = pos[0]
        text_y1 = pos[1] - text_rect1.height
        surface.blit(text1, [text_x1, text_y1])

    def speed_text(self, surface, pos, vel, fsize=12):
        """Display planet's speed text"""
        font = pygame.font.Font('freesansbold.ttf', fsize)
        text1 = font.render("{0:.2f}".format(vel), True, self.WHITE)
        text_rect1 = text1.get_rect()
        text_x1 = pos[0]
        text_y1 = pos[1] - text_rect1.height
        surface.blit(text1, [text_x1, text_y1])

    def crossed_limit(self, var):
        """Checking int08's limit"""
        if var >= 32700 or var <= -32700:
            return True
        else:
            return False

    # -------- Main Program Loop -----------
    def main(self):
        """Main function"""
        while not self.done:

            # Limit frames per second
            self.clock.tick(60)

            # --- Event Processing
            for event in pygame.event.get():
                if (
                    event.type == pygame.QUIT
                    or (event.type == pygame.KEYDOWN and event.key == pygame.K_q)):

                    self.done = True
                    self.game_over = True

                elif event.type == pygame.MOUSEMOTION:

                    if self.mouseClicked1:
                        self.dir_x, self.dir_y = event.pos
                        self.initial_speed()

                    else:
                        self.circle_x, self.circle_y = event.pos

                elif event.type == pygame.MOUSEBUTTONUP:

                    if not self.mouseClicked1:
                        self.mouseClicked1 = True
                        self.mouseClicked2 = False
                        self.circle_x, self.circle_y = event.pos
                        self.dir_x, self.dir_y = self.circle_x, self.circle_y

                    else:
                        self.mouseClicked1 = False
                        self.mouseClicked2 = True
                        self.dir_x, self.dir_y = event.pos
                        self.theta = self.angle(
                            self.dir_y - self.circle_y,
                            self.dir_x - self.circle_x)

                        self.alpha = self.angle(
                            self.screen.get_height()/2 - self.circle_y,
                            self.screen.get_width()/2 - self.circle_x)

                        self.a = (self.G * self.M) / (
                            pow(self.screen.get_height()/2 - self.circle_y, 2)
                            + pow(self.screen.get_width()/2 - self.circle_x, 2))

                        self.planet.append({
                            'color': self.planet_color,
                            'x': self.circle_x,
                            'y': self.circle_y,
                            'velocity': self.v,
                            'theta': self.theta,
                            'acceleration': self.a,
                            'alpha': self.alpha})
                        
                        self.circle_x, self.circle_y = self.dir_x, self.dir_y

                        self.planet_color = (randint(0, 255), randint(0, 255), randint(0, 255))

            # --- Game Logic

            if not self.eaten:
                # Actual logic
                if len(self.planet) > 0:
                    p_i = 0
                    while p_i < len(self.planet):
                        if self.collision(
                            (self.screen.get_width()/2, self.screen.get_height()/2),
                            self.b_r,
                            (self.planet[p_i]['x'], self.planet[p_i]['y']),
                            self.p_r):
                            
                            del self.planet[p_i]

                        else:
                            self.update_position(p_i)
                            if (
                                self.crossed_limit(self.planet[p_i]['x'])
                                or self.crossed_limit(self.planet[p_i]['y'])):

                                del self.planet[p_i]

                            else:
                                self.update_acceleration(p_i)           
                                self.update_velocity(p_i)
                                p_i += 1

                # --- Draw the frame

                # Set the screen background
                # screen.blit(background, (0, 0))
                self.screen.fill((50, 50, 50))
                self.status_surface.fill((0, 0, 0, 112))

                # Draw the shapes
                # drawing black hole
                self.draw_circle(
                    self.screen, self.BLACK,
                    [self.screen.get_width()/2, self.screen.get_height()/2],
                    20,
                    True)

                # black hole aura
                for i in range(1, 50):
                    self.draw_circle(
                        self.screen,
                        (0, 0, 0, i),
                        [self.screen.get_width()/2, self.screen.get_height()/2],
                        50-i,
                        True)

                if self.mouseClicked1 and not self.mouseClicked2:
                    self.draw_line(
                        self.screen,
                        self.WHITE,
                        [self.circle_x, self.circle_y],
                        [self.dir_x, self.dir_y])

                    self.speed_text(self.screen, [self.dir_x, self.dir_y], self.v)

                if len(self.planet) > 0:
                    for i in range(0, len(self.planet)):
                        self.draw_line(
                            self.screen,
                            self.WHITE,
                            [self.planet[i]['x'], self.planet[i]['y']],
                            [self.planet[i]['x'] + 25, self.planet[i]['y'] - 10])

                        self.speed_text(
                            self.screen,
                            [self.planet[i]['x'] + 25, self.planet[i]['y'] - 10],
                            self.planet[i]['velocity'])

                        self.draw_circle(
                            self.screen,
                            self.planet[i]['color'],
                            [self.planet[i]['x'], self.planet[i]['y']],
                            5,
                            True,
                            True)

                        #status surface
                        self.draw_circle(
                            self.status_surface,
                            self.planet[i]['color'],
                            [15, 65+(i*25)],
                            5,
                            True,
                            True)

                        self.speed_text(
                            self.status_surface,
                            [self.status_surface.get_width()/3, 73+(i*25)],
                            self.planet[i]['velocity'])

                        self.distance_text(
                            self.status_surface,
                            [2*self.status_surface.get_width()/3, 73+(i*25)],
                            i)

                self.draw_circle(
                    self.screen,
                    self.planet_color,
                    [self.circle_x, self.circle_y],
                    5,
                    True,
                    True)

            # Till window is not closed, draw this stuff.
            if not self.done:
                #status surface
                self.status_surface_text()
                self.screen.blit(self.status_surface, (0, 0))

                self.main_surface_text()
                pygame.display.flip()
            else:
                self.closing_animation()


        # on exit.
        pygame.quit()
        #sys.exit(0)

if __name__ == '__main__':
    O = Orbits()
    O.main()