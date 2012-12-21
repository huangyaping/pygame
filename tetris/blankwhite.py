import pygame, sys, threading, time, random
from pygame.locals import *

FPS = 30 # frames per second, the general speed of the program

CAPTION = 'Tetris - Blank White'
WINDOWWIDTH = 300
WINDOWHEIGHT = 450
BOARDWIDTH = 10
BOARDHEIGHT = 15
XMARGIN = 5
YMARGIN = 5
GAPSIZE = 1
FALLSPEED = 1

WHITE = (255, 255, 255)
LIGHTGRAY = (241, 241, 241)
GRAY = (100, 100, 100)
LIGHTGREEN = (170, 238, 187)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

BGCOLOR = WHITE
BGBOXCOLOR = LIGHTGRAY
BOARDCOLOR = BLACK
BOXCOLOR = LIGHTGREEN

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

LINE = "line"
SQUARE = "square"
TBLOCK = "tblock"
LBLOCK = "lblock"
ALLSHAPE = (LINE, SQUARE, TBLOCK, LBLOCK,)
ALLFORWARD = (UP, RIGHT, DOWN, LEFT)

def main():
    global DISPLAYSURF, FPSCLOCK, ISDEAD, FALLOVER
    pygame.init()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption(CAPTION)
    
    FPSCLOCK = pygame.time.Clock()
    initBoard()
    startGame()
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                ISDEAD = True
                while not FALLOVER: # wait until the "fall thread" die
                    pass
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP:
                if event.key in (K_DOWN, K_LEFT, K_RIGHT):
                    direction = dirFromKey(event.key)
                    move(direction)
                elif event.key == K_SPACE:
                    transform()
                elif ISDEAD and event.key == K_RETURN:
                    initBoard()
                    startGame()
        pygame.display.update()

def initBoard():
    # erase all things in the game main board
    # create background with new game state
    global BOXWIDTH, BOXHEIGHT, ALLBLOCKS, MAINBOARD
    DISPLAYSURF.fill(BGCOLOR)
    MAINBOARD = [[0]*BOARDWIDTH for i in range(BOARDHEIGHT)]
    awidth = WINDOWWIDTH - XMARGIN*2
    aheight = WINDOWHEIGHT - YMARGIN*2
    pygame.draw.rect(DISPLAYSURF, BOARDCOLOR, (XMARGIN-1, YMARGIN-3, awidth+1, aheight+1), 1)
    BOXWIDTH = int((awidth + GAPSIZE) / BOARDWIDTH - GAPSIZE)
    BOXHEIGHT = int((aheight + GAPSIZE) / BOARDHEIGHT - GAPSIZE)
    ALLBLOCKS = [ (shape, forward) for shape in ALLSHAPE for forward in ALLFORWARD ]
    random.shuffle(ALLBLOCKS)
    drawBoard()

def drawBoard():
    "Redraw entire board."
    for boxy in range(BOARDHEIGHT):
        for boxx in range(BOARDWIDTH):
            drawBox(boxx, boxy)

def drawBox(boxx, boxy):
    color = BGBOXCOLOR
    if MAINBOARD[boxy][boxx]:
        color = BOXCOLOR
    left, top = leftTopCoordsOfBox(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, color, (left, top, BOXWIDTH, BOXHEIGHT))

def drawBlock(coords, color):
    for boxx, boxy in coords:
        drawBox(boxx, boxy, color)

def leftTopCoordsOfBox(boxx, boxy):
    left = boxx * (BOXWIDTH+GAPSIZE) + XMARGIN
    top = boxy * (BOXHEIGHT+GAPSIZE) + YMARGIN
    return (left, top)

def startGame():
    # start the process for the fall-off block
    global ISDEAD, FALLOVER
    ISDEAD = False
    FALLOVER = False
    newBlock()
    FALL = threading.Thread(target=fallOff)
    FALL.daemon = True
    FALL.start()
    
def clearBlock():
    "Empty current state."
    global BLOCK
    BLOCK = dict(shape=None, forward=None, coords=[])
    
def newBlock():
    global BLOCK, ISDEAD
    clearBlock()
    shape, forward = random.choice(ALLBLOCKS)
    coords = getCoords(shape, forward)
    for boxx, boxy in coords:
        if MAINBOARD[boxy][boxx]:
            ISDEAD = True
            return
        else:
            MAINBOARD[boxy][boxx] = 1
            drawBox(boxx, boxy)
    BLOCK = dict(shape=shape, forward=forward, coords=coords)
    print BLOCK

def getCoords(shape, forward):
    coords = []
    center = int(BOARDWIDTH / 2)
    if shape == LINE:
        if forward == UP or forward == DOWN:
            coords = [(center-1, 0), (center, 0), (center+1, 0), (center+2, 0)]
        elif forward == LEFT or forward == RIGHT:
            coords = [(center, 0), (center, 1), (center, 2), (center, 3)]
    elif shape == SQUARE:
        coords = [(center, 0), (center+1, 0), (center, 1), (center+1, 1)]
    elif shape == TBLOCK:
        if forward == UP:
            coords = [(center, 0), (center+1, 1), (center, 1), (center-1, 1)]
        elif forward == RIGHT:
            coords = [(center, 0), (center+1, 1), (center, 1), (center, 2)]
        elif forward == DOWN:
            coords = [(center-1, 0), (center+1, 0), (center, 0), (center, 1)]
        elif forward == LEFT:
            coords = [(center-1, 1), (center, 0), (center, 1), (center, 2)]
    elif shape == LBLOCK:
        if forward == UP:
            coords = [(center+1, 0), (center+1, 1), (center, 1), (center-1, 1)]
        elif forward == RIGHT:
            coords = [(center+1, 2), (center, 2), (center, 1), (center, 0)]
        elif forward == DOWN:
            coords = [(center-1, 1), (center-1, 0), (center, 0), (center+1, 0)]
        elif forward == LEFT:
            coords = [(center-1, 0), (center, 0), (center, 1), (center, 2)]
    return coords

def fallOff():
    global ISDEAD, FALLOVER
    time.sleep(FALLSPEED)
    while True:
        if not move(DOWN):
            clearBlock()
            eliminate()
            center = int(BOARDWIDTH / 2)
            if MAINBOARD[0][center]:
                break
            newBlock()
        if ISDEAD:
            break
        time.sleep(FALLSPEED)
    gameOver()
    FALLOVER = True
    print 'FALLOVER'

def moveTo(direction):
    # test if can move in the 'direction'
    shape, forward = getShapeAndForward()
    coords = BLOCK['coords']
    newCoords = []
    # print direction, DOWN, LEFT, RIGHT
    if direction == DOWN:
        for boxx, boxy in coords:
            newCoords.append((boxx, boxy+1))
    elif direction == LEFT:
        for boxx, boxy in coords:
            newCoords.append((boxx-1, boxy))
    elif direction == RIGHT:
        for boxx, boxy in coords:
            newCoords.append((boxx+1, boxy))
    # print newCoords
    if not newCoords:
        return None
    for boxx, boxy in newCoords:
        if boxx < 0 or boxy < 0 or boxx >= BOARDWIDTH or boxy >= BOARDHEIGHT:
            return None
    for nc in newCoords:
        if nc not in coords and MAINBOARD[nc[1]][nc[0]]:
            return None
    return newCoords
    
def move(direction):
    # move in the 'direction'
    lock = threading.RLock()
    with lock:
        #print lock, threading.current_thread()
        coords = BLOCK['coords']
        newCoords = moveTo(direction)
        if newCoords:
            for boxx, boxy in coords:
                MAINBOARD[boxy][boxx] = 0
                drawBox(boxx, boxy)
            for boxx, boxy in newCoords:
                MAINBOARD[boxy][boxx] = 1
                drawBox(boxx, boxy)
            BLOCK['coords'] = newCoords
        #print '-'*10+'over'+'-'*10
        return newCoords

def transform():
    # transform
    lock = threading.RLock()
    with lock:
        shape, forward = getShapeAndForward()
        coords = BLOCK['coords']
        if not coords:
            return
        newCoords = []
        for boxx, boxy in coords:
            newCoords.append((boxx, boxy))
        if shape == LINE:
            boxx = coords[1][0]
            boxy = coords[1][1]
            if forward == UP or forward == DOWN:
                for i in range(len(coords)):
                    newCoords[i] = (boxx, boxy-1+i)
            elif forward == LEFT or forward == RIGHT:
                for i in range(len(coords)):
                    newCoords[i] = (boxx-1+i, boxy)
        elif shape == SQUARE:
            return
        elif shape == TBLOCK:
            if forward == UP: # transform to RIGHT
                newCoords[3] = (coords[3][0]+1, coords[3][1]+1)
            elif forward == RIGHT: # transform to DOWN
                newCoords[0] = (coords[0][0]-1, coords[0][1]+1)
            elif forward == DOWN: # transform to LEFT
                newCoords[1] = (coords[1][0]-1, coords[1][1]-1)
            elif forward == LEFT: # transform to UP
                newCoords[0], newCoords[3] = coords[1], coords[0]
                newCoords[1] = (coords[3][0]+1, coords[3][1]-1)
        elif shape == LBLOCK:
            if forward == UP: # transform to RIGHT
                newCoords[0] = (coords[0][0], coords[0][1]+2)
                newCoords[1] = (coords[1][0]-1, coords[1][1]+1)
                newCoords[3] = (coords[3][0]+1, coords[3][1]-1)
            elif forward == RIGHT: # transform to DOWN
                newCoords[0] = (coords[0][0]-2, coords[0][1])
                newCoords[1] = (coords[1][0]-1, coords[1][1]-1)
                newCoords[3] = (coords[3][0]+1, coords[3][1]+1)
            elif forward == DOWN: # transform to LEFT
                newCoords[0] = (coords[0][0], coords[0][1]-2)
                newCoords[1] = (coords[1][0]+1, coords[1][1]-1)
                newCoords[3] = (coords[3][0]-1, coords[3][1]+1)
            elif forward == LEFT: # transform to UP
                newCoords[0] = (coords[0][0]+2, coords[0][1])
                newCoords[1] = (coords[1][0]+1, coords[1][1]+1)
                newCoords[3] = (coords[3][0]-1, coords[3][1]-1)
        
        for boxx, boxy in newCoords:
            if boxx < 0 or boxy < 0 or boxx >= BOARDWIDTH or boxy >= BOARDHEIGHT:
                return None
        for nc in newCoords:
            if nc not in coords and MAINBOARD[nc[1]][nc[0]]:
                return None
        # erase old block, draw new block
        for boxx, boxy in coords:
            MAINBOARD[boxy][boxx] = 0
            drawBox(boxx, boxy)
        for boxx, boxy in newCoords:
            MAINBOARD[boxy][boxx] = 1
            drawBox(boxx, boxy)
        BLOCK['coords'] = newCoords
        BLOCK['forward'] = ALLFORWARD[(forward+1)%len(ALLFORWARD)]
        print BLOCK

def eliminate():
    lines = getEliminations()
    if not lines:
        return
    flash = 3
    for i in range(flash):
        for line in lines:
            for boxx in range(BOARDWIDTH):
                MAINBOARD[line][boxx] = 1
                drawBox(boxx, line)
        pygame.display.update()
        time.sleep(0.1)
        FPSCLOCK.tick(FPS)
        for line in lines:
            for boxx in range(BOARDWIDTH):
                MAINBOARD[line][boxx] = 0
                drawBox(boxx, line)
        pygame.display.update()
        time.sleep(0.1)
        FPSCLOCK.tick(FPS)
    for line in lines:
        del MAINBOARD[line]
    for line in lines:
        MAINBOARD.insert(0, [0]*BOARDWIDTH)
    drawBoard()

def getEliminations():
    '''
    Return those line number which is complete.
    Each line number has range(0, "BOARDHEIGHT").
    '''
    pboard()
    es = []
    for boxy in range(BOARDHEIGHT-1, -1, -1):
        for boxx in range(BOARDWIDTH-1, -1, -1):
            if MAINBOARD[boxy][boxx] == 0:
                break
        else:
            es.append(boxy)
    return es

def gameOver():
    fontObj = pygame.font.Font('freesansbold.ttf', 32)
    textSurfaceObj = fontObj.render('Game Over!', True, RED)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (WINDOWWIDTH/2, WINDOWHEIGHT/2-16)
    DISPLAYSURF.blit(textSurfaceObj, textRectObj)
    
    fontObj = pygame.font.Font('freesansbold.ttf', 16)
    textSurfaceObj = fontObj.render('Press Enter to replay game', True, BLACK)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (WINDOWWIDTH/2, WINDOWHEIGHT/2+16)
    DISPLAYSURF.blit(textSurfaceObj, textRectObj)

def getShapeAndForward():
    return BLOCK['shape'], BLOCK['forward']

def dirFromKey(key_val):
    "Return corresponding direction from keyboard constants."
    if key_val == K_DOWN:
        return DOWN
    elif key_val == K_LEFT:
        return LEFT
    elif key_val == K_RIGHT:
        return RIGHT

def pboard():
    '''   
    for b in MAINBOARD:
        print b
    print
    '''

if __name__ == "__main__":
    main()
