import pygame
from pygame import image, transform, display, Rect
import os
import random

# Sets position of window
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (550,40)
# Initializes game
pygame.init()
# Create game window
WIN_HEIGHT = 770 # Background scaled
WIN_WIDTH = 430
WIN = display.set_mode((WIN_WIDTH, WIN_HEIGHT))
display.set_caption("Flappy Bird")
font = pygame.font.Font("./font.ttf", 50)
# Loads in images
BIRD_IMGS = [transform.scale(image.load("imgs/"+PATH), (51,36)) for PATH in os.listdir("imgs/") if "bird" in PATH]
PIPE_IMGS = [transform.scale(image.load("imgs/pipe.png"), (75, 700)),
             transform.scale(transform.flip(image.load("imgs/pipe.png"),0,1), (75, 700))]
BG_IMG = transform.scale(image.load("imgs/bg.png"), (WIN_WIDTH, WIN_HEIGHT))
BASE_IMG = transform.scale(image.load("imgs/base.png"), (WIN_WIDTH, 112))

class Bird:
    def __init__(self, x=50, y=330):
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
        '''Calculates new bird coordinates'''
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
        # Increment frames
        self.frame += 1

        # Gravity physics
        self.vel_y = self.vel_y - self.acc * 2/30
        # Uses velocity to update x coordinates
        if self.vel_y > self.vel_y_max:
            self.vel_y = self.vel_y_max
        if abs(self.vel_y) < self.vel_y_min:
            direction = self.vel_y/(abs(self.vel_y)+1)
            self.y += direction * self.vel_y_min
        else:
            self.y += self.vel_y

        # Calculates tilt
        if self.vel_y < 0 and self.tilt < 25:
            self.tilt += 25
        if self.vel_y > 0 and self.tilt > -90:
            self.tilt -= 5

        # Calculates hitbox
        self.hitbox = Rect(self.x, self.y, 51, 36)

    def jump(self):
        '''Alters velocity to make bird jump'''
        self.vel_y = -23.5

    def draw(self, window):
        '''Displays bird on game window'''
        # Calculates rectangle to display bird in
        center = self.img.get_rect().center
        topleft = (self.x, self.y)
        rot_img = transform.rotate(self.img, self.tilt)
        rot_rect = rot_img.get_rect(center=self.img.get_rect(topleft=topleft).center)
        # Displays bird
        window.blit(rot_img, rot_rect)
        # Draws rectangle only if class is initialized in another script
        if __file__ != "flappy_bird.py":
            pygame.draw.rect(window, (0,255,0), self.hitbox, 2)

class Pipe:
    def __init__(self, gap=200, offset=0):
        # Initializes state variables
        self.bottom = PIPE_IMGS[0]
        self.top = PIPE_IMGS[1]
        self.vel = 5
        self.gap = gap
        self.x = WIN_WIDTH + offset
        self.y_bot = random.randint(300, WIN_HEIGHT-200)
        self.y_top = self.y_bot - self.gap - 700
        self.hitbox_bot = Rect(self.x, self.y_bot, 75, 700)
        self.hitbox_top = Rect(self.x, self.y_top, 75, 700)

    def respawn(self, x):
        '''Generates random height and moves pipe to x'''
        self.x = x
        self.y_bot = random.randint(300, WIN_HEIGHT-200)
        self.y_top = self.y_bot - self.gap - 700
        self.hitbox_bot = Rect(self.x, self.y_bot, 75, 700)
        self.hitbox_top = Rect(self.x, self.y_top, 75, 700)

    def move(self):
        '''Calculates new pipe coordinates'''
        self.x -= self.vel
        self.hitbox_bot = Rect(self.x, self.y_bot, 75, 700)
        self.hitbox_top = Rect(self.x, self.y_top, 75, 700)

class Base:
    def __init__(self):
        # Initializes state variables
        self.img = BASE_IMG
        self.x = [0, WIN_WIDTH]
        self.y = WIN_HEIGHT-80
        self.vel = 5

    def move(self):
        '''Calculates new base coordinates'''
        self.x[0] -= self.vel
        self.x[1] -= self.vel
        # Loops images for continued movement
        if self.x[0] + WIN_WIDTH < 0:
            self.x[0] = self.x[1] + WIN_WIDTH
        if self.x[1] + WIN_WIDTH < 0:
            self.x[1] = self.x[0] + WIN_WIDTH

def draw_frame(window, background, bird, base, pipe_list, text=None, text_rect=None):
    '''Draws each frame'''
    # Background
    window.blit(background, (0,0))
    # Pipes
    for pipe in pipe_list:
        window.blit(pipe.top, (pipe.x, pipe.y_top))
        window.blit(pipe.bottom, (pipe.x, pipe.y_bot))
        if __file__ != "flappy_bird.py":
            pygame.draw.rect(window, (255,0,0), pipe.hitbox_bot, 2)
            pygame.draw.rect(window, (255,0,0), pipe.hitbox_top, 2)
    # Base
    window.blit(base.img, (base.x[0], base.y))
    window.blit(base.img, (base.x[1], base.y))
    # Bird
    bird.draw(window)
    # Text
    if text and text_rect:
        window.blit(text, text_rect)
    elif text:
        window.blit(text, (WIN_WIDTH-text.get_width()-10, 10))
    # Updates display to show new surfaces
    display.update()

def game_logic():
    '''Processes game logic'''
    global run
    global TEXT
    global SCORE
    global BIRD
    global PIPE_LIST
    global BASE
    # Checks for quit event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pgame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                BIRD.jump()
    # Update object coordinates
    BIRD.move()
    BASE.move()
    # Checks for collision with ground
    if BIRD.y + BIRD.img.get_width() >= BASE.y:
        run = False
    # Checks for collision with pipes
    for PIPE in PIPE_LIST:
        # Updates pipe coordinates
        PIPE.move()
        # If collides
        if PIPE.hitbox_bot.colliderect(BIRD.hitbox) or PIPE.hitbox_top.colliderect(BIRD.hitbox):
            # Stop game
            run = False
        # If bird passes pipe
        if PIPE.x + 75 == BIRD.x:
            # Add score and render new text
            SCORE += 1
            TEXT = font.render("Score: {}".format(SCORE), True, (255,255,255))
        # If pipe is off screen
        if PIPE.x + 75 <= 0:
            # Get index of furthest piper
            idx = (PIPE_LIST.index(PIPE) + 2) % 3
            # Position to respawn pipe
            x = PIPE_LIST[idx].x + PIPE_SPACING
            PIPE.respawn(x)

# Instantiates game objects
BIRD = Bird(50, 330)
BASE = Base()
PIPE_SPACING = 250
PIPE_LIST = [Pipe(offset=0), Pipe(offset=PIPE_SPACING), Pipe(offset=2*PIPE_SPACING)]
SCORE = 0
TEXT = font.render("Score: {}".format(SCORE), True, (255,255,255))

def main():
    '''Main game loop'''
    global run
    global BIRD
    global PIPE_LIST
    global BASE
    global SCORE
    global TEXT
    global PIPE_SPACING
    # Clock to control framerate
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
    # Game Over (run=False)
    # Render end game texts
    font = pygame.font.Font("./font.ttf", 100)
    text = font.render("Score: {}".format(SCORE), True, (255,255,255))
    text_rect = text.get_rect(center=(WIN_WIDTH/2, WIN_HEIGHT/2 - 100))
    # Timer to display text
    timer = pygame.time.get_ticks()
    # Draw endgame frame
    while pygame.time.get_ticks() - timer < 2000:
        draw_frame(WIN, BG_IMG, BIRD, BASE, PIPE_LIST, text, text_rect)
    # Quit game
    pygame.quit()

if __name__=="__main__":
    main()
