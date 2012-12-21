import pygame, sys, threading, time, random
from pygame.locals import *

FPS = 30 # frames per second, the general speed of the program

CAPTION = 'Tetris - X-Blank White'
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
RLBLOCK = "rlblock"
ALLSHAPE = (LBLOCK, RLBLOCK,)
ALLFORWARD = (UP, RIGHT, DOWN, LEFT)

'''
rules = {
            block type : (
                {
                    forward : ((x, y) - board coordinates of every point in order of this block),
                }
            ),
        }
'''
RULES = {
            LBLOCK : (
                {
                    UP : ((2,0), (2,1), (1,1), (0,1)),
                    RIGHT : ((2,2), (1,2), (1,1), (1,0)),
                    DOWN : ((0,2), (0,1), (1,1), (2,1)),
                    LEFT : ((0,0), (1,0), (1,1), (1,2))
                }
            ),
            RLBLOCK : (
                {
                    UP : ((2,0), (2,1), (1,1), (0,1)),
                    RIGHT : ((2,2), (1,2), (1,1), (1,0)),
                    DOWN : ((0,2), (0,1), (1,1), (2,1)),
                    LEFT : ((0,0), (1,0), (1,1), (1,2))
                }
            ),
        }

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
    #print BLOCK

def getCoords(shape, forward):
    coords = RULES[shape][forward]
    #print 'getCoords', shape, forward
    center = int(BOARDWIDTH / 2)
    if shape == LBLOCK and forward == DOWN:
        coords = do_move(coords, UP)
    coords = do_move(coords, RIGHT, center-1)
    #print 'getcs', coords
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

def moveTo(coords, direction):
    " coords - current board coordinates."
    # test if can move in the 'direction'
    # and return the destination coordinates
    newCoords = do_move(coords, direction)
    return checkBounds(coords, newCoords)

def do_move(coords, direction, step=1):
    " coords - current board coordinates."
    # test if can move in the 'direction'
    # and return the destination coordinates
    newCoords = []
    if direction == DOWN:
        for boxx, boxy in coords:
            newCoords.append((boxx, boxy+step))
    elif direction == LEFT:
        for boxx, boxy in coords:
            newCoords.append((boxx-step, boxy))
    elif direction == RIGHT:
        for boxx, boxy in coords:
            newCoords.append((boxx+step, boxy))
    elif direction == UP:
        for boxx, boxy in coords:
            newCoords.append((boxx, boxy-step))
    '''
    print 'do move'
    print coords
    print newCoords
    print 'over'
    '''
    return newCoords
            
def checkBounds(coords, newCoords):
    for boxx, boxy in newCoords:
        if boxx < 0 or boxy < 0 or boxx >= BOARDWIDTH or boxy >= BOARDHEIGHT:
            return None
    for box in newCoords:
        if box not in coords and MAINBOARD[box[1]][box[0]]:
            return None
    return newCoords
    
def move(direction):
    # move in the 'direction'
    lock = threading.RLock()
    with lock:
        #print lock, threading.current_thread()
        coords = BLOCK['coords']
        newCoords = moveTo(coords, direction)
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
        adjust = []
        newForward = getNewForward(forward)
        nf = RULES[shape][newForward]
        for i in range(len(RULES[shape][newForward])):
            adjust.append(( RULES[shape][newForward][i][0] - RULES[shape][forward][i][0],
                        RULES[shape][newForward][i][1] - RULES[shape][forward][i][1] ))

        newCoords = []
        for (boxx, boxy), (ax, ay) in zip(coords, adjust):
            newCoords.append( (boxx + ax, boxy + ay) )
                
        if not checkBounds(coords, newCoords):
            return None
        # erase old block, draw new block
        for boxx, boxy in coords:
            MAINBOARD[boxy][boxx] = 0
            drawBox(boxx, boxy)
        for boxx, boxy in newCoords:
            MAINBOARD[boxy][boxx] = 1
            drawBox(boxx, boxy)
        BLOCK['coords'] = newCoords
        BLOCK['forward'] = newForward
        print BLOCK

def getNewForward(forward):
    return ALLFORWARD[(forward+1)%len(ALLFORWARD)]

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
