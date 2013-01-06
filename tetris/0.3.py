#!/usr/bin/env python
import pygame, sys, threading, time, random
from pygame.locals import *

FPS = 30 # frames per second, the general speed of the program

CAPTION = "Tetris - 0.3"
WINDOWWIDTH = 250
WINDOWHEIGHT = 375
PANELWIDTH = 100
BOARDWIDTH = 10
BOARDHEIGHT = 15
XMARGIN = 5
YMARGIN = 5
GAPSIZE = 1
FALLSPEED = 1
LINESCORE = 100
# game state constants
INIT = "init"
RUNNING = "running"
PAUSE = "pause"
TRANSITION = "transition"
GAMEOVER = "gameover"

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
PANELCOLOR = WHITE

UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3

LINE = "line"
SQUARE = "square"
TBLOCK = "tblock"
LBLOCK = "lblock"
RLBLOCK = "rlblock"
SQUIGGLE = "squiggle"
RSQUIGGLE = "rsquiggle"
ALLSHAPE = (LINE, SQUARE, TBLOCK, LBLOCK, RLBLOCK, SQUIGGLE, RSQUIGGLE)
ALLFORWARD = (UP, RIGHT, DOWN, LEFT)
#ALLSHAPE = (RLBLOCK,)

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
            LINE : (
                {
                    UP : ((0,1), (1,1), (2,1), (3,1)),
                    RIGHT : ((1,0), (1,1), (1,2), (1,3)),
                    DOWN : ((0,1), (1,1), (2,1), (3,1)),
                    LEFT : ((1,0), (1,1), (1,2), (1,3)),
                }
            ),
            SQUARE : (
                {
                    UP : ((0,0), (1,0), (1,1), (0,1)),
                    RIGHT : ((0,0), (1,0), (1,1), (0,1)),
                    DOWN : ((0,0), (1,0), (1,1), (0,1)),
                    LEFT : ((0,0), (1,0), (1,1), (0,1)),
                }
            ),
            TBLOCK : (
                {
                    UP : ((1,0), (1,1), (0,1), (2,1)),
                    RIGHT : ((2,1), (1,1), (1,0), (1,2)),
                    DOWN : ((1,2), (1,1), (2,1), (0,1)),
                    LEFT : ((0,1), (1,1), (1,2), (1,0)),
                }
            ),
            LBLOCK : (
                {
                    UP : ((2,0), (2,1), (1,1), (0,1)),
                    RIGHT : ((2,2), (1,2), (1,1), (1,0)),
                    DOWN : ((0,2), (0,1), (1,1), (2,1)),
                    LEFT : ((0,0), (1,0), (1,1), (1,2)),
                }
            ),
            RLBLOCK : (
                {
                    UP : ((0,0), (0,1), (1,1), (2,1)),
                    RIGHT : ((2,0), (1,0), (1,1), (1,2)),
                    DOWN : ((2,2), (2,1), (1,1), (0,1)),
                    LEFT : ((0,2), (1,2), (1,1), (1,0)),
                }
            ),
            SQUIGGLE : (
                {
                    UP : ((1,0), (1,1), (2,1), (2,2)),
                    RIGHT : ((2,0), (1,0), (1,1), (0,1)),
                    DOWN : ((1,0), (1,1), (2,1), (2,2)),
                    LEFT : ((2,0), (1,0), (1,1), (0,1)),
                }
            ),
            RSQUIGGLE : (
                {
                    UP : ((1,0), (1,1), (0,1), (0,2)),
                    RIGHT : ((2,1), (1,1), (1,0), (0,0)),
                    DOWN : ((1,0), (1,1), (0,1), (0,2)),
                    LEFT : ((2,1), (1,1), (1,0), (0,0)),
                }
            ),
        }

def main():
    global DISPLAYSURF, FPSCLOCK, GAMEOVER, FALLOVER, FALLEVENT, FALLSPEED, GAMESTATE
    pygame.init()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH + PANELWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption(CAPTION)
    
    FPSCLOCK = pygame.time.Clock()
    initGame()
    startGame()
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                print 'gameover'
                GAMESTATE = GAMEOVER
                while not FALLOVER: # until the "fall-thread" is dead
                    pass
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP:
                if GAMESTATE == GAMEOVER:
                    if event.key == K_RETURN:
                        initGame()
                        startGame()
                elif GAMESTATE == PAUSE:
                    if event.key == K_RETURN:
                        print 'running'
                        FALLEVENT = threading.Event()
                        GAMESTATE = RUNNING
                elif GAMESTATE == RUNNING:
                    if event.key in (K_DOWN, K_LEFT, K_RIGHT):
                        direction = dirFromKey(event.key)
                        move(direction)
                    elif event.key == K_UP:
                        rotate()
                    elif event.key == K_SPACE:
                        FALLEVENT.set() # fall the block straight with no waiting
                    elif event.key == K_RETURN:
                        print 'PAUSE'
                        FALLEVENT.set()
                        #drawFont(32, 'pause', BLACK, (WINDOWWIDTH/2, WINDOWHEIGHT/2))
                        GAMESTATE = PAUSE
        pygame.display.update()

def initGame():
    '''
    Erase all things of the game.
    Initialize game states.
    '''
    global BOXWIDTH, BOXHEIGHT, CENTER, ALLBLOCKS, MAINBOARD, FALLEVENT, LOCK, GAMESTATE, SCORES, NEXTBLOCK
    DISPLAYSURF.fill(BGCOLOR)
    MAINBOARD = [[0]*BOARDWIDTH for i in range(BOARDHEIGHT)]
    awidth = WINDOWWIDTH - XMARGIN*2
    aheight = WINDOWHEIGHT - YMARGIN*2
    pygame.draw.rect(DISPLAYSURF, BOARDCOLOR, (XMARGIN-1, YMARGIN-3, awidth+1, aheight+1), 1)
    BOXWIDTH = int((awidth + GAPSIZE) / BOARDWIDTH - GAPSIZE)
    BOXHEIGHT = int((aheight + GAPSIZE) / BOARDHEIGHT - GAPSIZE)
    CENTER = int(BOARDWIDTH / 2)
    ALLBLOCKS = [ (shape, forward) for shape in ALLSHAPE for forward in ALLFORWARD ]
    random.shuffle(ALLBLOCKS)
    drawBoard()
    FALLEVENT = threading.Event()
    LOCK = threading.RLock()
    GAMESTATE = INIT
    SCORES = 0
    drawScores()
    NEXTBLOCK = newBlock()

def drawBoard():
    "Redraw the entire board."
    for boxy in range(BOARDHEIGHT):
        for boxx in range(BOARDWIDTH):
            drawBox(boxx, boxy)

def drawBox(boxx, boxy):
    color = BGBOXCOLOR
    if MAINBOARD[boxy][boxx]:
        color = BOXCOLOR
    left, top = leftTopCoordsOfBox(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, color, (left, top, BOXWIDTH, BOXHEIGHT))

def drawNextBlock():
    global BLOCK, NEXTBLOCK
    coords = BLOCK["coords"]
    nextCoords = NEXTBLOCK["coords"]
    start_point = (WINDOWWIDTH+1, WINDOWHEIGHT/4)
    for boxx, boxy in coords:
        left = boxx * (BOXWIDTH+GAPSIZE) + XMARGIN
        top = boxy * (BOXHEIGHT+GAPSIZE) + YMARGIN
        pygame.draw.rect(DISPLAYSURF, PANELCOLOR, (start_point[0]+left, start_point[1]+top, BOXWIDTH, BOXHEIGHT))
    for boxx, boxy in nextCoords:
        left = boxx * (BOXWIDTH+GAPSIZE) + XMARGIN
        top = boxy * (BOXHEIGHT+GAPSIZE) + YMARGIN
        pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (start_point[0]+left, start_point[1]+top, BOXWIDTH, BOXHEIGHT))

def leftTopCoordsOfBox(boxx, boxy):
    left = boxx * (BOXWIDTH+GAPSIZE) + XMARGIN
    top = boxy * (BOXHEIGHT+GAPSIZE) + YMARGIN
    return (left, top)

def startGame():
    # start the process for the fall-off block
    global FALLOVER, GAMESTATE, BLOCK
    FALLOVER = False
    nextBlock()
    moveToBoard()
    FALL = threading.Thread(target=fallOff)
    FALL.daemon = True
    FALL.start()
    GAMESTATE = RUNNING
    
def clearBlock():
    "Empty current state."
    global BLOCK
    BLOCK = dict(shape=None, forward=None, coords=[])
    
def nextBlock():
    global BLOCK, NEXTBLOCK, FALLEVENT, GAMESTATE
    FALLEVENT = threading.Event()
    BLOCK, NEXTBLOCK = NEXTBLOCK, newBlock()
    drawNextBlock()
    #print BLOCK
    
def newBlock():
    shape, forward = random.choice(ALLBLOCKS)
    coords = RULES[shape][forward]
    return dict(shape=shape, forward=forward, coords=coords)

def moveToBoard():
    global BLOCK, GAMESTATE
    shape, forward = getShapeAndForward()
    oldCoords = BLOCK['coords']
    newCoords = do_move(oldCoords, RIGHT, CENTER-1) # move to the center of board
    ad = dirFromAdjust(shape, forward) # direction which the block be adjusted
    #print ad
    if ad != None:
        newCoords = do_move(newCoords, ad)
    print 'moveToBoard', shape, forward, newCoords
    for boxx, boxy in sorted(newCoords, key=lambda box: (box[1], box[0])):
        if MAINBOARD[boxy][boxx]:
            GAMESTATE = GAMEOVER
        else:
            MAINBOARD[boxy][boxx] = 1
            drawBox(boxx, boxy)
    if GAMESTATE == GAMEOVER:
        print shape, forward
        return None
    BLOCK['coords'] = newCoords
    return newCoords

def dirFromAdjust(shape, forward):
    if shape == LINE:
        if forward in (UP, DOWN):
            return UP
        else:
            return LEFT
    if shape == SQUIGGLE and forward in (UP, DOWN):
        return LEFT
    if shape in (LBLOCK, RLBLOCK, TBLOCK):
        if forward == DOWN:
            return UP
        elif forward == RIGHT:
            return LEFT
    

def fallOff():
    global FALLSPEED, FALLOVER, GAMESTATE, BLOCK
    FALLEVENT.wait(FALLSPEED)
    while True:
        if GAMESTATE == RUNNING:
            if not move(DOWN):
                GAMESTATE = TRANSITION
                BLOCK = dict(shape=None, forward=None, coords=[]) # empty current state
                eliminate()
                if MAINBOARD[0][CENTER]:
                    print 'top traffic'
                    break
                nextBlock()
                if not moveToBoard():
                    BLOCK = dict(shape=None, forward=None, coords=[]) # traffic occurs at new block
                    break
                GAMESTATE = RUNNING
            FALLEVENT.wait(FALLSPEED)
        elif GAMESTATE == PAUSE:
            pass
        elif GAMESTATE == GAMEOVER:
            break
    gameOver()
    GAMESTATE = GAMEOVER
    FALLOVER = True

def move(direction):
    # move in the 'direction'
    with LOCK:
        #print lock, threading.current_thread()
        oldCoords = BLOCK['coords']
        newCoords = do_move(oldCoords, direction)
        newCoords = checkBounds(oldCoords, newCoords)
        if newCoords:
            for boxx, boxy in oldCoords:
                MAINBOARD[boxy][boxx] = 0
                drawBox(boxx, boxy)
            for boxx, boxy in newCoords:
                MAINBOARD[boxy][boxx] = 1
                drawBox(boxx, boxy)
            BLOCK['coords'] = newCoords
        #print '-'*10+'over'+'-'*10
        return newCoords

def do_move(oldCoords, direction, step=1):
    '''
    oldCoords - the current board coordinates of the block
    direction - (DOWN, LEFT, RIGHT, UP)
    step - how much steps(boxes) to move
    Return the coordinates after moving.
    '''
    newCoords = []
    if direction == DOWN:
        for boxx, boxy in oldCoords:
            newCoords.append((boxx, boxy+step))
    elif direction == LEFT:
        for boxx, boxy in oldCoords:
            newCoords.append((boxx-step, boxy))
    elif direction == RIGHT:
        for boxx, boxy in oldCoords:
            newCoords.append((boxx+step, boxy))
    elif direction == UP:
        for boxx, boxy in oldCoords:
            newCoords.append((boxx, boxy-step))
    '''
    print 'do move'
    print oldCoords
    print newCoords
    print 'over'
    '''
    if not newCoords:
        newCoords = oldCoords
    return newCoords
            
def checkBounds(oldCoords, newCoords):
    for boxx, boxy in newCoords:
        if boxx < 0 or boxy < 0 or boxx >= BOARDWIDTH or boxy >= BOARDHEIGHT:
            return None
    for box in newCoords:
        if box not in oldCoords and MAINBOARD[box[1]][box[0]]:
            return None
    return newCoords
    
def rotate():
    "Rotate the block."
    with LOCK:
        shape, forward = getShapeAndForward()
        oldCoords = BLOCK['coords']
        adjust = []
        newForward = getNewForward(forward)
        nf = RULES[shape][newForward]
        for i in range(len(RULES[shape][newForward])):
            adjust.append(( RULES[shape][newForward][i][0] - RULES[shape][forward][i][0],
                        RULES[shape][newForward][i][1] - RULES[shape][forward][i][1] ))

        newCoords = []
        for (boxx, boxy), (ax, ay) in zip(oldCoords, adjust):
            newCoords.append( (boxx + ax, boxy + ay) )
                
        if not checkBounds(oldCoords, newCoords):
            return
        # erase old block, draw new block
        for boxx, boxy in oldCoords:
            MAINBOARD[boxy][boxx] = 0
            drawBox(boxx, boxy)
        for boxx, boxy in newCoords:
            MAINBOARD[boxy][boxx] = 1
            drawBox(boxx, boxy)
        BLOCK['coords'] = newCoords
        BLOCK['forward'] = newForward
        #print BLOCK

def getNewForward(forward):
    return ALLFORWARD[(forward+1)%len(ALLFORWARD)]

def eliminate():
    global SCORES
    lines = getEliminations()
    if not lines:
        return
    SCORES += len(lines) * LINESCORE
    drawScores()
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
    drawFont(32, 'Game Over!', RED, (WINDOWWIDTH/2, WINDOWHEIGHT/2-16))
    drawFont(16, 'Press Enter to replay game', BLACK, (WINDOWWIDTH/2, WINDOWHEIGHT/2+16))

def drawScores():
    # erase the whole rect area of font
    rect = drawFont(32, str(SCORES), BLACK, (WINDOWWIDTH+(PANELWIDTH)/2, WINDOWHEIGHT-WINDOWHEIGHT/4), False)
    pygame.draw.rect(DISPLAYSURF, PANELCOLOR, rect)
    
    drawFont(32, str(SCORES), BLACK, (WINDOWWIDTH+(PANELWIDTH)/2, WINDOWHEIGHT-WINDOWHEIGHT/4))

def drawFont(size, text, color, center_coords, do_blit=True):
    "Draw font on screen DISPLAYSURF, return the rectangle of font."
    fontObj = pygame.font.Font('freesansbold.ttf', size)
    textSurfaceObj = fontObj.render(text, True, color)
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = center_coords
    if do_blit:
        DISPLAYSURF.blit(textSurfaceObj, textRectObj)
    return textRectObj

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

def moveTo(oldCoords, direction):
    '''
    oldCoords - the board coordinates of the block
    Move and return the destination coordinates.
    '''
    newCoords = do_move(oldCoords, direction)
    return checkBounds(oldCoords, newCoords)

if __name__ == "__main__":
    main()
