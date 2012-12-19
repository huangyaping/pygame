import pygame, sys
from pygame.locals import *

pygame.init()

FPS = 30 # frames per second
fpsClock = pygame.time.Clock()

# set up the window
DISPLAYSURF = pygame.display.set_mode((400, 300), 0, 32)
pygame.display.set_caption('Cat Animation')

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
catImg = pygame.image.load('cat.png').convert()
catx = 10
caty = 10
w, h = catImg.get_rect().width, catImg.get_rect().height
direction = 'right'

fontObj = pygame.font.Font('freesansbold.ttf', 32)
textSurfaceObj = fontObj.render('Hello world!', True, GREEN)
textRectObj = textSurfaceObj.get_rect()
DISPLAYSURF.fill(WHITE)
pygame.display.flip()
import time
while True: # the main game loop
    

    if direction == 'right':
        catx += 5
        if catx == 270:
            direction = 'down'
    elif direction == 'down':
        caty += 5
        if caty == 220:
            direction = 'left'
    elif direction == 'left':
        catx -= 5
        if catx == 10:
            direction = 'up'
    elif direction == 'up':
        caty -= 5
        if caty == 10:
            direction = 'right'
    
    DISPLAYSURF.blit(catImg, (catx, caty))
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
    #print time.clock()
    fpsClock.tick(FPS)
