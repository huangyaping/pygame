import pygame, sys
from pygame.locals import *

pygame.init()

# set up the window
DISPLAYSURF = pygame.display.set_mode((500, 400), 0, 32)
pygame.display.set_caption('Drawing')

# set up the colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# draw on the surface object
DISPLAYSURF.fill(WHITE)
#pygame.draw.polygon(DISPLAYSURF, GREEN, ((146,0), (291,106), (236,277), (56,277), (0,106)))
pygame.draw.line(DISPLAYSURF, BLUE, (60, 60), (120, 60), 4)
pygame.draw.line(DISPLAYSURF, BLUE, (120, 60), (60, 120))
pygame.draw.line(DISPLAYSURF, BLUE, (60, 120), (120, 120), 4)
pygame.draw.lines(DISPLAYSURF, RED, True, ((80, 80), (80, 140), (140, 140)), 4)
pygame.draw.rect(DISPLAYSURF, RED, (80, 180, 30, 30))
pygame.draw.ellipse(DISPLAYSURF, YELLOW, (80, 180+int(30*1/4./2), 30, int(30*3/4.)))
pygame.draw.rect(DISPLAYSURF, YELLOW, (10, 80, 30, 30), 8)
pygame.draw.circle(DISPLAYSURF, RED, (100, 300), 20)
pygame.draw.circle(DISPLAYSURF, BLUE, (200, 300), 10, 8)
pygame.draw.circle(DISPLAYSURF, BLUE, (150, 300), 10, 4)

pygame.draw.rect(DISPLAYSURF, RED, (180, 180, 30, 30), 4)
pygame.draw.rect(DISPLAYSURF, BLUE, (180, 180, 30, 30), 4)

print DISPLAYSURF.get_locked()
pixObj = pygame.PixelArray(DISPLAYSURF)
pixObj[480][380] = BLACK
pixObj[482][382] = BLACK
pixObj[484][384] = BLACK
pixObj[486][386] = BLACK
print DISPLAYSURF.get_locked()
del pixObj
print DISPLAYSURF.get_locked()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
