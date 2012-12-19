import pygame, sys
from pygame.locals import *

pygame.init()
DISPLAYSURF = pygame.display.set_mode((400, 300))
pygame.display.set_caption('Event')

while True:
    
    pygame.event.pump()
    if pygame.key.get_pressed()[K_ESCAPE]:
        pygame.quit()
        sys.exit()
    elif pygame.key.get_pressed()[K_DOWN]:
        print 'down arrow'
        print pygame.key.get_repeat()
    elif pygame.key.get_pressed()[K_LEFT]:
        print 'left arrow'
    '''
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_DOWN:
                print K_UP, K_DOWN, K_RIGHT, K_LEFT, 'down arrow'
            elif event.key == K_LEFT:
                print K_LEFT, 'left arrow'
    '''
    pygame.display.update()
