import threading

def main():
    global cnt, isdead, lock
    cnt = 0
    isdead = False
    lock = threading.RLock()
    newThread(1)
    newThread(2)

def newThread(tid):
    t = threading.Thread(target=doit, name=tid)
    t.deamon = True
    t.start()
def doit():
    while not isdead:
        incr()
def incr():
    global cnt, isdead, lock

    with lock:
        for i in range(100*2):
            cnt += 1
    #    print cnt
        if cnt % 2 != 0:
            print 'Confilct occurs between threads.'
            print 'Current value:', cnt
            isdead = True

main()

