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

event = curses.KEY_DOWN
flag = True
flagEnemie = True

class Player (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.position = [18, 30]
        self.shotPosition = [17, 30]

    def run(self):
        self.controlMovements()

    def controlMovements(self):
        global flag
        global event
        if event == curses.KEY_RIGHT:
            coordinates = [self.position[0], self.position[1] + 1]
            if coordinates[1] != WINDOW_WIDTH-1:
                # apaga posicao atual
                win.addch(self.position[0], self.position[1], ' ')
                self.position[1] = coordinates[1]
                self.position[0] = coordinates[0]
                win.addch(coordinates[0], coordinates[1], "x")

        if self.position == WINDOW_WIDTH - 1:
            pass

        if event == curses.KEY_LEFT:
            # move jogador para esquerda
            coordinates = [self.position[0], self.position[1] - 1]
            if coordinates[1] != 1:
                # apaga posicao atual
                win.addch(self.position[0], self.position[1], ' ')
                self.position[1] = coordinates[1]
                self.position[0] = coordinates[0]
                win.addch(coordinates[0], coordinates[1], "x")

        if event == curses.KEY_UP:
            self.shotPosition[0] = self.position[0] - 1
            self.shotPosition[1] = self.position[1]

            win.addch(self.shotPosition[0], self.shotPosition[1], ".")

            while(self.shotPosition[0] > 4):
                if(flag):
                    win.addch(self.shotPosition[0], self.shotPosition[1], ".")
                    oldPosition = self.shotPosition[0]
                    self.shotPosition[0] = self.shotPosition[0] - 1
                    win.addch(oldPosition, self.shotPosition[1], " ")

                    mutex.acquire()
                    flag = False
                    mutex.release()
                
        time.sleep(0.02)

class Enemie (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.enemie_position = [4, 28]  # posição do inimigo
        self.enemie_shot_position = [0, 0]  # inicialização da posição do tiro
        self.operator = 1  # aumenta ou diminui se indo para esquerda ou direita
        self.direction = 'right'

    def run(self):
        self.enemie_movement()

    def enemie_movement(self):
        global event
        global flagEnemie

        if(flagEnemie):
            for x in range(4): 
                if self.direction == 'right':
                    erase = self.enemie_position[1] - 5 # apaga o 5 elemento da direita para esquerda
                else:
                    erase = self.enemie_position[1] + 5 # apaga o 5 elemento da esquerda para direita

                if self.enemie_position[1] == WINDOW_WIDTH-6: #setando largura máxima
                    self.operator = -1
                    self.direction = 'left'

                if self.enemie_position[1] == 6: #setando largura máxima
                    self.operator = 1
                    self.direction = 'right'

                self.enemie_position[1] = self.enemie_position[1] + self.operator # aumenta ou diminui variavel de acordo com o operador
                win.addch(self.enemie_position[0], self.enemie_position[1], 'o') # printa o inimigo
                win.addch(self.enemie_position[0], erase, ' ') # apaga conforme se movimenta
                shot_in_the_middle = self.enemie_position[1] - 2

                if(self.enemie_shot_position[0] < 18):
                    self.enemie_shot_position[0] = self.enemie_position[0] + 1
                    win.addch(self.enemie_shot_position[0], shot_in_the_middle, '|')
                    win.addch(self.enemie_position[0], shot_in_the_middle, ' ')

                elif(self.enemie_shot_position[0] == 18):
                    win.addch(self.enemie_position[0], shot_in_the_middle, ' ')


                mutex.acquire()
                flagEnemie = False
                mutex.release()

            time.sleep(0.02)
            # self.shot()
        

def updateScreen():
    global flag
    global flagEnemie

    while(event != ESC):
        win.timeout(100) 

        mutex.acquire()
        flag = True #flag que sinaliza que o player pode se mover
        flagEnemie = True #flag que sinaliza que o enemie pode se mover
        mutex.release()

        time.sleep(0.1)


def main():
    global event
    enemie = Enemie()
    thread3 = threading.Thread(target=updateScreen)
    win.addch(18, 30, 'x')  # inicializando posição do jogador
    player = Player()
    player.start()
    enemie.start()
    thread3.start()

    while event != ESC: # enquanto evento não for esc continua rodando o programa
        event = win.getch()
        player.run()
        enemie.run()

    thread3.join()
    enemie.join()
    player.join()

    curses.endwin()
    print(f"Final score = {score}")

main()
