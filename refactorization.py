import time
import threading
import curses
from random import randint
sem = threading.Semaphore()
mutex = threading.Lock()

WINDOW_WIDTH = 60  # number of columns of window box
WINDOW_HEIGHT = 20  # number of rows of window box
ESC = 27
score = 0
curses.initscr()
win = curses.newwin(WINDOW_HEIGHT, WINDOW_WIDTH, 0, 0)
win.keypad(1)
curses.noecho()
curses.curs_set(0)
win.border(0)
win.nodelay(1)

class Player (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.key = curses.KEY_DOWN
        self.right = curses.KEY_RIGHT
        self.left = curses.KEY_LEFT
        self.shot = curses.KEY_UP
        self.position = [18, 30]
        self.shotPosition = [0, 0]        

    def controlMovements(self, event):
        if event == self.right:
            sem.acquire()
            coordinates = [self.position[0], self.position[1] + 1]
            if coordinates[1] != WINDOW_WIDTH-1:
                # apaga posicao atual
                win.addch(self.position[0], self.position[1], ' ')
                self.position[1] = coordinates[1]
                self.position[0] = coordinates[0]
                win.addch(coordinates[0], coordinates[1], "x")
            sem.release()

        if self.position == WINDOW_WIDTH - 1:
            pass

        if event == self.left:
            mutex.acquire()
            # move jogador para esquerda
            coordinates = [self.position[0], self.position[1] - 1]
            if coordinates[1] != 1:
                # apaga posicao atual
                win.addch(self.position[0], self.position[1], ' ')
                self.position[1] = coordinates[1]
                self.position[0] = coordinates[0]
                win.addch(coordinates[0], coordinates[1], "x")
            mutex.release()

        if event == self.shot:
            mutex.acquire()
            self.shotPosition[0] = self.position[0] - 1
            self.shotPosition[1] = self.position[1]
            win.addch(self.shotPosition[0], self.shotPosition[1], ".")
            mutex.release()

            for x in range(WINDOW_HEIGHT-4):
                win.addch(self.shotPosition[0], self.shotPosition[1], ".")
                old_position = self.shotPosition[0]
                self.shotPosition[0] = self.shotPosition[0] - 1
                win.addch(old_position, self.shotPosition[1], " ")

        time.sleep(0.02)


class Enemie (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.enemie_position = [4, 28]  # posição do inimigo
        self.enemie_shot_position = [0, 0]  # direção do tiro
        self.operator = 1 ## define esquerda ou direita, está começando para direita
        self.direction = 'right' 

    def begin(self):
        win.addch(self.enemie_position[0], self.enemie_position[1], 'o')

    def enemie_movement(self):

        for x in range(4):
            if self.direction == 'right':
                erase = self.enemie_position[1] - 5
            else:
                erase = self.enemie_position[1] + 5

            if self.enemie_position[1] == WINDOW_WIDTH-6:
                self.operator = -1
                self.direction = 'left'

            if self.enemie_position[1] == 6:
                self.operator = 1
                self.direction = 'right'

            mutex.acquire()
            self.enemie_position[1] = self.enemie_position[1] + self.operator
            mutex.release()
            win.addch(self.enemie_position[0], self.enemie_position[1], 'o')
            win.addch(self.enemie_position[0], erase, ' ')
            self.enemie_shot_position[0] = self.enemie_position[0] + 1
            #self.shot()

    def shot(self):
        shot_in_the_middle = self.enemie_position[1] - 2
        win.addch(self.enemie_shot_position[0], shot_in_the_middle, '|')
        win.addch(self.enemie_position[0], shot_in_the_middle, ' ')

        time.sleep(0.02)


def updateScreen():
    mutex.acquire()
    win.timeout(100)
    mutex.release()
    time.sleep(0.01)

def main():
    enemie = Enemie()
    enemie.begin()
    thread3 = threading.Thread(target=updateScreen)
    thread3.start()
    win.addch(18, 30, 'x')  # inicializando posição do jogador
    key = curses.KEY_DOWN
    player = Player()
    enemie = Enemie()
    player.start()
    enemie.start()
    while key != ESC:
        event = win.getch()
        if event != -1:
            key = event
        player.controlMovements(event)
        enemie.enemie_movement()

    thread3.join()
    enemie.join()
    player.join()

    curses.endwin()
    print(f"Final score = {score}")

main()
