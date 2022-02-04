from glob import glob
from multiprocessing import Event
import time
import threading
import curses
sem = threading.Semaphore()
mutex = threading.Lock()

WINDOW_WIDTH = 60  # numero de colunas da tela
WINDOW_HEIGHT = 20  # numero de linhas da tela
ESC = 27 
PAUSE = 112 #letra p na tabela ascii
RESET = 114 #letra R na tabela ascii
EXIT = 101 #letra e na tabela ascii

curses.initscr()
win = curses.newwin(WINDOW_HEIGHT, WINDOW_WIDTH, 0, 0)
win.keypad(1)
curses.noecho()
curses.curs_set(0)
win.border(0)
win.nodelay(1)

score = 0
event = curses.KEY_DOWN
flag = True
flagEnemie = True
paused = False

class Player (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.position = [18, 30]
        self.shotPosition = [17, 30]
        self.shot = False

    def run(self):
        self.controlMovements()

    def controlMovements(self):
        global flag
        global event

        if(flag):
            if event == curses.KEY_RIGHT:
                coordinates = [self.position[0], self.position[1] + 1]

                if coordinates[1] != WINDOW_WIDTH-6:
                    # apaga posicao atual
                    win.addch(self.position[0], self.position[1], ' ')
                    self.position[1] = coordinates[1]
                    self.position[0] = coordinates[0]
                    win.addch(coordinates[0], coordinates[1], "x")

            if self.position == WINDOW_WIDTH - 6:
                pass

            if event == curses.KEY_LEFT:
                # move jogador para esquerda
                coordinates = [self.position[0], self.position[1] - 1]
                if coordinates[1] != 6:
                    # apaga posicao atual
                    win.addch(self.position[0], self.position[1], ' ')
                    self.position[1] = coordinates[1]
                    self.position[0] = coordinates[0]
                    win.addch(coordinates[0], coordinates[1], "x")

            if event == curses.KEY_UP:
                self.shotPosition[0] = self.position[0] - 1
                self.shotPosition[1] = self.position[1]
                self.shot = True
                self.shotMovement(self.shotPosition[1], self.shotPosition[0])
                
            mutex.acquire()
            flag = False
            mutex.release()
            time.sleep(0.02)

    def shotMovement(self, xPosition, yPosition):
        global flag
        self.shotPosition[1] = xPosition
        self.shotPosition[0] = yPosition
        win.addch(self.shotPosition[0], self.shotPosition[1], ".")
        while(self.shot and self.shotPosition[0] > 4):
            
            if (flag):
                win.addch(self.shotPosition[0], self.shotPosition[1], " ")
                self.shotPosition[0] = self.shotPosition[0] - 1
                win.addch(self.shotPosition[0], self.shotPosition[1], ".")
                
                mutex.acquire()
                flag = False
                mutex.release()
                
            if (self.shotPosition[0] == 4):
                self.shot = False
                win.addch(self.shotPosition[0], self.shotPosition[1], " ")


class Enemie (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.enemie_position = [4, 28]  # posição do inimigo
        self.enemie_shot_position = [0, 0]  # inicialização da posição do tiro
        self.operator = 1  # aumenta ou diminui se indo para esquerda ou direita
        self.direction = 'right'
        self.numOfShots = 0
        self.stopped = event

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

                    for x in range(6):
                        delete = WINDOW_WIDTH-6 - x
                        win.addch(self.enemie_position[0], delete, ' ')

                    self.enemie_position[0] = self.enemie_position[0] + 1

                if self.enemie_position[1] == 6: #setando largura minima
                    self.operator = 1
                    self.direction = 'right'
                    
                    for x in range(6):
                        delete = 6 + x
                        win.addch(self.enemie_position[0], delete, ' ')

                    self.enemie_position[0] = self.enemie_position[0] + 1
                
                if self.enemie_position[0] == 18:
                    event = ESC

                self.enemie_position[1] = self.enemie_position[1] + self.operator # aumenta ou diminui variavel de acordo com o operador
                win.addch(self.enemie_position[0], self.enemie_position[1], 'o') # printa o inimigo
                win.addch(self.enemie_position[0], erase, ' ') # apaga conforme se movimenta
                shot_in_the_middle = self.enemie_position[1] - 2

                mutex.acquire()
                flagEnemie = False
                mutex.release()

            # if(self.numOfShots < 5):
            #     pass
            #     self.shotMovement(shot_in_the_middle)
                
            # if (self.numOfShots == 5):
            #     self.numOfShots -= 1
        time.sleep(0.02)
            
    def shotMovement(self, shot_in_the_middle):
        while(self.enemie_shot_position[0] < 18):
            self.numOfShots += 1
            self.enemie_shot_position[0] += 1
            win.addch(self.enemie_shot_position[0], shot_in_the_middle, '|')
            win.addch(self.enemie_position[0], shot_in_the_middle, ' ')

        if(self.enemie_shot_position[0] == 18):
            self.numOfShots -= 1
            

def updateScreen():
    global flag
    global flagEnemie
    global paused
    win.timeout(150)

    while(event != ESC):
        mutex.acquire()
        if (paused == False): # se não está pausado então habilita movimentos
            flag = True #flag que sinaliza que o player pode se mover
            flagEnemie = True #flag que sinaliza que o enemie pode se mover
        mutex.release()
        time.sleep(0.1)

def interfaceThread():
    global event
    global flag
    global flagEnemie
    global paused
    global score

    while(True):
        if (event == PAUSE and paused == False):
            mutex.acquire()
            flag = False #flag que sinaliza que o player pode se mover
            flagEnemie = False #flag que sinaliza que o enemie pode se mover
            paused = True
            event = 97 # usando apenas para mudar event e poder retomar o jogo
            mutex.release()

        if (event == PAUSE and paused == True):
            mutex.acquire()
            flag = True #flag que sinaliza que o player pode se mover
            flagEnemie = True #flag que sinaliza que o enemie pode se mover
            paused = False
            event = 97 # usando apenas para mudar event e poder pausar o jogo
            mutex.release()

        if(event == RESET):
            mutex.acquire()
            score = 0

            mutex.release()


        if (event == EXIT):
            curses.endwin()


def main():

    global event
    
    enemie = Enemie()
    thread3 = threading.Thread(target=updateScreen)
    thread4 = threading.Thread(target=interfaceThread)
    win.addch(18, 30, 'x')  # inicializando posição do jogador

    player = Player()
    player.start()
    enemie.start()
    thread3.start()
    thread4.start()

    while event != ESC: # enquanto evento não for esc continua rodando o programa
        event = win.getch()
        win.addstr(2, 2, 'Score ' + str(score) + ' ')
        player.run()
        enemie.run()

    thread4.join()
    thread3.join()
    enemie.join()
    player.join()

    curses.endwin()
    print(f"Final score = {score}")

main()