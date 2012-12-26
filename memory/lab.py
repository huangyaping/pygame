import pygame, sys, random
from pygame.locals import *

# ui configurations
width, height = 400, 320
wn, hn = 10, 7
assert wn*hn % 2 == 0, 'The number of boxes must be even.'
xmargin = 25
ymargin = 25
sx, sy = xmargin, ymargin
gapsize = 5
boxsize = (width - 2*xmargin ) / wn - gapsize
print boxsize

def getRandomizedBoard():
    mainBoard, poss = [], []
    for h in range(hn):
        mainBoard.append([0]*wn)
    digit = range(7)
    alpha = ('a', 'b', 'c', 'd', 'e')
    g = []
    for dd in digit:
        for aa in alpha:
            g.append(str(dd)+aa)
    print g
    g *= 2
    random.shuffle(g)
    index = 0
    for row in range(hn):
        for col in range(wn):
            mainBoard[row][col] = g[index]
            index += 1
    for row in mainBoard:
        print row

mainBoard = getRandomizedBoard()

pygame.init()
DISPLAYSURF = pygame.display.set_mode((width, height))
pygame.display.set_caption('Memory Puzzle')

# set up color
background = (170, 238, 187)
icon_color = (240, 240, 240)
black = (0, 0, 0)

DISPLAYSURF.fill(background)
fontObj = pygame.font.Font('freesansbold.ttf', 22)
for row in range(hn):
    csx = sx
    csy = sy + row * (boxsize + gapsize)
    cpos = []
    for col in range(wn):
        pygame.draw.rect(DISPLAYSURF, icon_color, (csx, csy, boxsize, boxsize))
        # textSurfaceObj = fontObj.render(mainBoard[row][col], True, icon_color, black)
        # DISPLAYSURF.blit(textSurfaceObj, (csx, csy, boxsize, boxsize))
        cpos.append((csx, csy))
        csx += boxsize + gapsize
    poss.append(cpos)
for row in poss:
    print row

def locate(x, y):
    " x, y - position of mouse click "
    row, col = 0, 0
    while col < wn:
        if x >= poss[0][col][0] and x <= poss[0][col][0]+boxsize:
            break
        col += 1
    if col == wn:
        return None
    while row < hn:
        if y >= poss[row][col][1] and y <= poss[row][col][1]+boxsize:
            return row, col
        row += 1
    return None
pair, last_pos = None, None
while True:
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            pos = locate(event.pos[0], event.pos[1])
            if pos:
                if pair:
                    if pair == mainBoard[pos[0]][pos[1]]:
                        print 1, mainBoard[pos[0]][pos[1]], pair, last_pos
                        pygame.draw.rect(DISPLAYSURF, background, (poss[pos[0]][pos[1]][0], poss[pos[0]][pos[1]][1], boxsize, boxsize))
                        pygame.draw.rect(DISPLAYSURF, background, (poss[last_pos[0]][last_pos[1]][0], poss[last_pos[0]][last_pos[1]][1], boxsize, boxsize))
                    pair = None
                else:
                    pair = mainBoard[pos[0]][pos[1]]
                    last_pos = pos
                    print mainBoard[pos[0]][pos[1]], pair, last_pos
            
    pygame.display.update()
