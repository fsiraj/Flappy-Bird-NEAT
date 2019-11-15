import pygame
from pygame import image, transform, display, Rect
import os
import random
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (550,40)
# os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()

# Create game window
WIN_HEIGHT = 770 # Background scaled
WIN_WIDTH = 430
WIN = display.set_mode((WIN_WIDTH, WIN_HEIGHT))
display.set_caption("Flappy Bird")
font = pygame.font.SysFont("calibri", 50)

# Loads in images
BIRD_IMGS = [transform.scale(image.load("imgs/"+PATH), (51,36)) for PATH in os.listdir("imgs/") if "bird" in PATH]
PIPE_IMGS = [transform.scale(image.load("imgs/pipe.png"), (75, 700)),
             transform.scale(transform.flip(image.load("imgs/pipe.png"),0,1), (75, 700))]
BG_IMG = transform.scale(image.load("imgs/bg.png"), (WIN_WIDTH, WIN_HEIGHT))
BASE_IMG = transform.scale(image.load("imgs/base.png"), (WIN_WIDTH, 112))

class Bird:

    def __init__(self, x, y):

        # Initialize state variables
        self.x = x
        self.y = y
        self.vel_x = 5
        self.vel_y = 0
        self.vel_y_min = 5
        self.vel_y_max = 17.5
        self.tilt = 0
        self.acc = -30
        self.img = BIRD_IMGS[0]
        self.frame = 0
        self.vel_x = 5
        self.hitbox = Rect(self.x, self.y, 51, 36)

    def move(self):

        # Flapping Animation
        if self.frame <= self.vel_x:
            self.img = BIRD_IMGS[0]
        elif self.frame <= self.vel_x * 2:
            self.img = BIRD_IMGS[1]
        elif self.frame <= self.vel_x * 3:
            self.img = BIRD_IMGS[2]
        elif self.frame <= self.vel_x * 4:
            self.img = BIRD_IMGS[1]
        else:
            self.img = BIRD_IMGS[0]
            self.frame = 0

        self.frame += 1

        # Gravity physics
        self.vel_y = self.vel_y - self.acc * 2/30

        if self.vel_y > self.vel_y_max:
            self.vel_y = self.vel_y_max
        if abs(self.vel_y) < self.vel_y_min:
            direction = self.vel_y/(abs(self.vel_y)+1)
            self.y += direction * self.vel_y_min
        else:
            self.y += self.vel_y

        # Tilt
        if self.vel_y < 0 and self.tilt < 25:
            self.tilt += 25
        if self.vel_y > 0 and self.tilt > -90:
            self.tilt -= 5

        # Hitbox
        self.hitbox = Rect(self.x, self.y, 51, 36)

    def jump(self):
        self.vel_y = -23.5

    def draw(self, window):
        center = self.img.get_rect().center
        topleft = (self.x, self.y)
        rot_img = transform.rotate(self.img, self.tilt)
        rot_rect = rot_img.get_rect(center=self.img.get_rect(topleft=topleft).center)

        window.blit(rot_img, rot_rect)
        pygame.draw.rect(window, (0,255,0), self.hitbox, 2)


class Pipe:

    def __init__(self, offset=0):
        self.bottom = PIPE_IMGS[0]
        self.top = PIPE_IMGS[1]
        self.vel = 5
        self.gap = 200
        self.x = WIN_WIDTH + offset
        self.y_bot = random.randint(250, WIN_HEIGHT-100)
        self.y_top = self.y_bot - self.gap - 700
        self.hitbox_bot = Rect(self.x, self.y_bot, 75, 700)
        self.hitbox_top = Rect(self.x, self.y_top, 75, 700)

    def respawn(self, x):
        self.x = x
        self.y_bot = random.randint(250, WIN_HEIGHT-100)
        self.y_top = self.y_bot - self.gap - 700
        self.hitbox_bot = Rect(self.x, self.y_bot, 75, 700)
        self.hitbox_top = Rect(self.x, self.y_top, 75, 700)


    def move(self):
        self.x -= self.vel
        self.hitbox_bot = Rect(self.x, self.y_bot, 75, 700)
        self.hitbox_top = Rect(self.x, self.y_top, 75, 700)

    def draw(self, window):
        pass

class Base:

    def __init__(self):
        self.img = BASE_IMG
        self.x = [0, WIN_WIDTH]
        self.y = WIN_HEIGHT-80
        self.vel = 5

    def move(self):
        self.x[0] -= self.vel
        self.x[1] -= self.vel

        # Loops images for continued movement
        if self.x[0] + WIN_WIDTH < 0:
            self.x[0] = self.x[1] + WIN_WIDTH
        if self.x[1] + WIN_WIDTH < 0:
            self.x[1] = self.x[0] + WIN_WIDTH

def draw_frame(window, background, bird, base, pipe_list, text=None, text_rect=None):
    '''Draws each frame'''
    window.blit(background, (0,0))

    for pipe in pipe_list:
        window.blit(pipe.top, (pipe.x, pipe.y_top))
        window.blit(pipe.bottom, (pipe.x, pipe.y_bot))
        pygame.draw.rect(window, (255,0,0), pipe.hitbox_bot, 2)
        pygame.draw.rect(window, (255,0,0), pipe.hitbox_top, 2)

    window.blit(base.img, (base.x[0], base.y))
    window.blit(base.img, (base.x[1], base.y))

    bird.draw(window)

    if text and text_rect:
        window.blit(text, text_rect)
    elif text:
        window.blit(text, (WIN_WIDTH-text.get_width()-10, 10))

    display.update()

BIRD = Bird(50, 330)
BASE = Base()
PIPE_SPACING = 250
PIPE_LIST = [Pipe(0), Pipe(PIPE_SPACING), Pipe(2*PIPE_SPACING)]
SCORE = 0
TEXT = font.render("Score: {}".format(SCORE), True, (255,255,255))

def game_logic():

    global run
    global TEXT
    global SCORE
    global BIRD
    global PIPE_LIST
    global BASE

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pgame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                BIRD.jump()

    # Update object coordinates
    BIRD.move()
    BASE.move()

    if BIRD.y + BIRD.img.get_width() >= BASE.y:
        run = False

    for PIPE in PIPE_LIST:
        PIPE.move()
        if PIPE.hitbox_bot.colliderect(BIRD.hitbox) or PIPE.hitbox_top.colliderect(BIRD.hitbox):
            run = False
            print("COLLISION!")

        if PIPE.x + 75 == BIRD.x:
            SCORE += 1
            TEXT = font.render("Score: {}".format(SCORE), True, (255,255,255))

        if PIPE.x + 75 <= 0:
            idx = (PIPE_LIST.index(PIPE) + 2) % 3
            x = PIPE_LIST[idx].x + PIPE_SPACING
            PIPE.respawn(x)


def main():
    '''Main game loop'''
    global run
    global BIRD
    global PIPE_LIST
    global BASE
    global SCORE
    global TEXT
    global PIPE_SPACING
    clock = pygame.time.Clock()

    # Run game
    run = True
    while run:
        # Set framerate
        clock.tick(30)
        # Display new frame
        draw_frame(WIN, BG_IMG, BIRD, BASE, PIPE_LIST, TEXT)
        # Process game logic and calculate new positions
        game_logic()

    # Game Over
    font = pygame.font.SysFont("calibri", 100)
    text = font.render("Score: {}".format(SCORE), True, (255,255,255))
    text_rect = text.get_rect(center=(WIN_WIDTH/2, WIN_HEIGHT/2))
    timer = pygame.time.get_ticks()

    while pygame.time.get_ticks() - timer < 2000:
        draw_frame(WIN, BG_IMG, BIRD, BASE, PIPE_LIST, text, text_rect)

    pygame.quit()

if __name__=="__main__":
    main()
