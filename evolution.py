import pygame
from pygame import image, transform, display, Rect
import neat
import os
from flappy_bird import Bird, Pipe, Base

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (550,40)
# os.environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()

# Create game window
WIN_HEIGHT = 770 # Background scaled
WIN_WIDTH = 430
WIN = display.set_mode((WIN_WIDTH, WIN_HEIGHT))
display.set_caption("Flappy Bird")
score_font = pygame.font.Font("./font.ttf", 50)
stat_font = pygame.font.Font("./font.ttf", 30)

# Loads in images
BIRD_IMGS = [transform.scale(image.load("imgs/"+PATH), (51,36)) for PATH in os.listdir("imgs/") if "bird" in PATH]
PIPE_IMGS = [transform.scale(image.load("imgs/pipe.png"), (75, 700)),
             transform.scale(transform.flip(image.load("imgs/pipe.png"),0,1), (75, 700))]
BG_IMG = transform.scale(image.load("imgs/bg.png"), (WIN_WIDTH, WIN_HEIGHT))
BASE_IMG = transform.scale(image.load("imgs/base.png"), (WIN_WIDTH, 112))


def draw_frame(window, background, birds, base, pipe_list, gen, alive, score, max_score):
    '''Draws each frame'''
    window.blit(background, (0,0))

    for pipe in pipe_list:
        window.blit(pipe.top, (pipe.x, pipe.y_top))
        window.blit(pipe.bottom, (pipe.x, pipe.y_bot))
        pygame.draw.rect(window, (255,0,0), pipe.hitbox_bot, 2)
        pygame.draw.rect(window, (255,0,0), pipe.hitbox_top, 2)

    window.blit(base.img, (base.x[0], base.y))
    window.blit(base.img, (base.x[1], base.y))

    for bird in birds:
        bird.draw(window)

    window.blit(gen, (10, 10))
    window.blit(alive, (10, 10 + gen.get_height()))
    window.blit(max_score, (10, 10 + gen.get_height() + alive.get_height()))
    window.blit(score, (WIN_WIDTH-score.get_width()-10, 10))


    display.update()

GENERATION = 0
MAX_SCORE = 0
def main(genomes, config):
    '''Main game loop'''
    global GENERATION
    GENERATION += 1
    global MAX_SCORE
    SCORE = 0


    BIRDS = []
    NETS = []
    GENOMES = []

    for _, genome in genomes:
        genome.fitness = 0
        NET = neat.nn.FeedForwardNetwork.create(genome, config)
        GENOMES.append(genome)
        NETS.append(NET)
        BIRDS.append(Bird())

    BASE = Base()
    PIPE_SPACING = 275
    PIPE_LIST = [Pipe(gap=200, offset=0),
                 Pipe(gap=200, offset=PIPE_SPACING),
                 Pipe(gap=200, offset=2*PIPE_SPACING)]

    SCORE_TEXT = score_font.render("Score: {}".format(SCORE), True, (255,255,255))
    MAX_SCORE_TEXT = stat_font.render("Max : {}".format(MAX_SCORE), True, (0,255,0))
    GEN_TEXT = stat_font.render("Gen : {}".format(GENERATION), True, (0,255,0))
    ALIVE_TEXT = stat_font.render("Alive: {}".format(len(BIRDS)), True, (0,255,0))
    CLOCK = pygame.time.Clock()

    # Run game
    run = True
    while run:
        # Set framerate
        # CLOCK.tick(30)
        # Display new frame
        draw_frame(WIN, BG_IMG, BIRDS, BASE, PIPE_LIST, GEN_TEXT, ALIVE_TEXT, SCORE_TEXT, MAX_SCORE_TEXT)
        # Process game logic and calculate new positions
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        # Get index of closest pipe:
        pipe_dists = [(PIPE.x - BIRDS[0].x + 75) for PIPE in PIPE_LIST if (PIPE.x + 75 > BIRDS[0].x)]
        closest_idx = pipe_dists.index(min(pipe_dists))

        # Run the neural net and update object coordinates
        for i, BIRD in enumerate(BIRDS):
            BIRD.move()
            GENOMES[i].fitness += 0.05

            inputs = [BIRD.y,                                                   # Bird height
                      BIRD.y - PIPE_LIST[closest_idx].y_bot,                    # Bottom pipe position
                      BIRD.y - (PIPE_LIST[closest_idx].y_top + 700),            # Top pipe position
                      PIPE_LIST[closest_idx].x - BIRD.x                         # Distance to next pipe
                     ]

            output = NETS[i].activate(inputs)
            output = output[0]                                                  # Unsqueeze
            if output > 0.5:
                BIRD.jump()

        BASE.move()

        # Checks the upper and lower bounds of screen
        for i, BIRD in enumerate(BIRDS):
            if (BIRD.y + BIRD.img.get_width() >= BASE.y) or (BIRD.y < 0):
                del BIRDS[i]
                del GENOMES[i]
                del NETS[i]

        pipe_passed = False

        for PIPE in PIPE_LIST:
            PIPE.move()
            for i, BIRD in enumerate(BIRDS):
                if PIPE.hitbox_bot.colliderect(BIRD.hitbox) or PIPE.hitbox_top.colliderect(BIRD.hitbox):
                    GENOMES[i].fitness -= 1
                    del BIRDS[i]
                    del GENOMES[i]
                    del NETS[i]

                if PIPE.x + 75 == BIRD.x:
                    GENOMES[i].fitness += 10
                    pipe_passed = True


                if PIPE.x + 75 <= 0:
                    # Index of last pipe
                    idx = (PIPE_LIST.index(PIPE) + 2) % 3
                    x = PIPE_LIST[idx].x + PIPE_SPACING
                    PIPE.respawn(x)

        if pipe_passed:
            SCORE += 1
            SCORE_TEXT = score_font.render("Score: {}".format(SCORE), True, (255,255,255))
            if SCORE > MAX_SCORE:
                MAX_SCORE = SCORE
                MAX_SCORE_TEXT = stat_font.render("Max : {}".format(MAX_SCORE), True, (0,255,0))


        if len(BIRDS) == 0:
            run = False
            break
        else:
            ALIVE_TEXT = stat_font.render("Alive: {}".format(len(BIRDS)), True, (0,255,0))


def run(config_path):
    config = neat.config.Config(
                        neat.DefaultGenome, neat.DefaultReproduction,
                        neat.DefaultSpeciesSet, neat.DefaultStagnation,
                        config_path)

    population = neat.population.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())

    elite_genome = population.run(main)


    print("\nBEST GENOME:", "\n{}".format(elite_genome))
    print("\nMAX SCORE:", MAX_SCORE)

if __name__=="__main__":
    config_path = "./config.txt"
    run(config_path)
