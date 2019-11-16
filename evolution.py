import pygame
from pygame import image, transform, display, Rect
import neat
import os
from flappy_bird import Bird, Pipe, Base

# Sets game window position
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (550,40)
# Initializes the game
pygame.init()
# Create game window
WIN_HEIGHT = 770 # Background scaled
WIN_WIDTH = 430
WIN = display.set_mode((WIN_WIDTH, WIN_HEIGHT))
display.set_caption("Flappy Bird")
# Initializes fonts to use later
score_font = pygame.font.Font("./font.ttf", 50)
stat_font = pygame.font.Font("./font.ttf", 30)
# Loads in sprites of all game objects
BIRD_IMGS = [transform.scale(image.load("imgs/"+PATH), (51,36)) for PATH in os.listdir("imgs/") if "bird" in PATH]
PIPE_IMGS = [transform.scale(image.load("imgs/pipe.png"), (75, 700)),
             transform.scale(transform.flip(image.load("imgs/pipe.png"),0,1), (75, 700))]
BG_IMG = transform.scale(image.load("imgs/bg.png"), (WIN_WIDTH, WIN_HEIGHT))
BASE_IMG = transform.scale(image.load("imgs/base.png"), (WIN_WIDTH, 112))
# Performance metrics for user. Global so main() can access via run()
GENERATION = 0
MAX_SCORE = 0

def draw_frame(window, background, birds, base, pipe_list, gen, alive, score, max_score):
    '''Handles all visual output of the game'''
    # Background
    window.blit(background, (0,0))
    # Pipes
    for pipe in pipe_list:
        window.blit(pipe.top, (pipe.x, pipe.y_top))
        window.blit(pipe.bottom, (pipe.x, pipe.y_bot))
        pygame.draw.rect(window, (255,0,0), pipe.hitbox_bot, 2)
        pygame.draw.rect(window, (255,0,0), pipe.hitbox_top, 2)
    # Base
    window.blit(base.img, (base.x[0], base.y))
    window.blit(base.img, (base.x[1], base.y))
    # Birds
    for bird in birds:
        bird.draw(window)
    # Text
    window.blit(gen, (10, 10))
    window.blit(alive, (10, 10 + gen.get_height()))
    window.blit(max_score, (10, 10 + gen.get_height() + alive.get_height()))
    window.blit(score, (WIN_WIDTH-score.get_width()-10, 10))
    # Displays everything
    display.update()

def main(genomes, config):
    '''Main game loop used as fitness function'''
    # Performance variables
    global GENERATION
    GENERATION += 1
    global MAX_SCORE
    SCORE = 0
    # Birds, nets, and genomes correspond by index
    BIRDS = []
    NETS = []
    GENOMES = []
    # Create the lists
    for _, genome in genomes:
        genome.fitness = 0
        NET = neat.nn.FeedForwardNetwork.create(genome, config)
        GENOMES.append(genome)
        NETS.append(NET)
        BIRDS.append(Bird())
    # Create base and pipes
    BASE = Base()
    PIPE_SPACING = 275
    PIPE_LIST = [Pipe(gap=200, offset=0),
                 Pipe(gap=200, offset=PIPE_SPACING),
                 Pipe(gap=200, offset=2*PIPE_SPACING)]
    # Renders initial texts
    SCORE_TEXT = score_font.render("Score: {}".format(SCORE), True, (255,255,255))
    MAX_SCORE_TEXT = stat_font.render("Max : {}".format(MAX_SCORE), True, (0,255,0))
    GEN_TEXT = stat_font.render("Gen : {}".format(GENERATION), True, (0,255,0))
    ALIVE_TEXT = stat_font.render("Alive: {}".format(len(BIRDS)), True, (0,255,0))
    # Clock can be used to control framerate
    CLOCK = pygame.time.Clock()
    # Run game
    run = True
    while run:
        # Set framerate. Comment out to run simulation at max speed
        # CLOCK.tick(30)
        # Display new frame
        draw_frame(WIN, BG_IMG, BIRDS, BASE, PIPE_LIST, GEN_TEXT, ALIVE_TEXT, SCORE_TEXT, MAX_SCORE_TEXT)
        # Checks for quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        # Get index of closest pipe:
        pipe_dists = [(PIPE.x - BIRDS[0].x + 75) for PIPE in PIPE_LIST if (PIPE.x + 75 > BIRDS[0].x)]
        closest_idx = pipe_dists.index(min(pipe_dists))
        # Run the neural net and update object coordinates
        for i, BIRD in enumerate(BIRDS):
            BIRD.move()
            # Bird receives some fitness for moving correctly
            GENOMES[i].fitness += 0.05
            # Inputs for the feedforward network defined by user
            inputs = [BIRD.y,                                                   # Bird height
                      BIRD.y - PIPE_LIST[closest_idx].y_bot,                    # Bottom pipe position
                      BIRD.y - (PIPE_LIST[closest_idx].y_top + 700),            # Top pipe position
                      PIPE_LIST[closest_idx].x - BIRD.x                         # Distance to next pipe
                     ]
            # Pass inputs through network
            output = NETS[i].activate(inputs)
            output = output[0]                                                  # Unsqueeze
            # Jumps if output > 0.5 [output between 0 and 1 due to sigmoid]
            if output > 0.5:
                BIRD.jump()
        # Moves base each frame
        BASE.move()
        # Checks the upper and lower bounds of screen
        for i, BIRD in enumerate(BIRDS):
            if (BIRD.y + BIRD.img.get_width() >= BASE.y) or (BIRD.y < 0):
                # Birds killed if they are out of bounds
                del BIRDS[i]
                del GENOMES[i]
                del NETS[i]
        # Main game logic checking for collisions
        pipe_passed = False
        for PIPE in PIPE_LIST:
            PIPE.move()
            for i, BIRD in enumerate(BIRDS):
                # If collides with pipe
                if PIPE.hitbox_bot.colliderect(BIRD.hitbox) or PIPE.hitbox_top.colliderect(BIRD.hitbox):
                    # Reduces fitness and kills bird
                    GENOMES[i].fitness -= 1
                    del BIRDS[i]
                    del GENOMES[i]
                    del NETS[i]
                # If bird passes the pipe
                if PIPE.x + 75 == BIRD.x:
                    # Give maximum fitness reward and update score
                    GENOMES[i].fitness += 10
                    pipe_passed = True
                # Once pipe is off screen, respawns it behind the other two (there is always 3 pipes in the list)
                if PIPE.x + 75 <= 0:
                    # Index of furthest pipe
                    idx = (PIPE_LIST.index(PIPE) + 2) % 3
                    # Respawn position for pipe
                    x = PIPE_LIST[idx].x + PIPE_SPACING
                    PIPE.respawn(x)
        # Updates scores and renders new texts
        if pipe_passed:
            SCORE += 1
            SCORE_TEXT = score_font.render("Score: {}".format(SCORE), True, (255,255,255))
            if SCORE > MAX_SCORE:
                MAX_SCORE = SCORE
                MAX_SCORE_TEXT = stat_font.render("Max : {}".format(MAX_SCORE), True, (0,255,0))
        # Checks if there are still birds alive
        if len(BIRDS) == 0:
            # Breaks out of main()
            run = False
            break
        else:
            # Number of birds still alive
            ALIVE_TEXT = stat_font.render("Alive: {}".format(len(BIRDS)), True, (0,255,0))

def run(config_path):
    '''Runs the actual NEAT algorithm on the game loop (main())'''
    # Loads in configuration file for NEAT algorithm
    config = neat.config.Config(
                        neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        config_path)
    # Creates a population of genomes
    population = neat.population.Population(config)
    # Adds reporters which print stats to console
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())
    # Runs the simulation and returns the best genome once criteria is met
    elite_genome = population.run(main)
    # Prints max score and returns elite (best) genome
    print("\nMAX SCORE:", MAX_SCORE)

    return elite_genome

if __name__=="__main__":
    config_path = "./config.txt"
    run(config_path)
