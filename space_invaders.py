from datetime import datetime as dt
import json
import multiprocessing
import socket
import time
import threading
import curses
import asyncio

mutex = threading.Lock()

WINDOW_WIDTH = 60  # numero de colunas da tela
WINDOW_HEIGHT = 20  # numero de linhas da tela
ESC = 27
PAUSE = 112  # letra p na tabela ascii
RESET = 114  # letra R na tabela ascii
EXIT = 101  # letra e na tabela ascii

score = 0
event = curses.KEY_DOWN
flag = True
flag_enemy = True
paused = False
reset = False
exited = False
t1 = time.time()
init = dt.now()
endGameTime = 'Game in progress'
vidas = 3
deadTime = 'Still alive'

curses.initscr()
win = curses.newwin(WINDOW_HEIGHT, WINDOW_WIDTH, 0, 0)
win.keypad(True)
curses.noecho()
curses.curs_set(0)
win.border(0)
win.nodelay(True)

class Player(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.position = [18, 30]
        self.shotPosition = [17, 30]
        self.shot = False

    def run(self):
        self.control_movements()

    def control_movements(self):
        global flag
        global event
        global reset

        if flag:
            if reset:
                win.addch(self.position[0], self.position[1], ' ')
                self.position = [18, 30]
                win.addch(self.position[0], self.position[1], 'x')
                self.shotPosition = [17, 30]
                self.shot = False
                reset = False

            if event == curses.KEY_RIGHT:
                coordinates = [self.position[0], self.position[1] + 1]

                if coordinates[1] != WINDOW_WIDTH - 6:
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
                self.shot_movement(self.shotPosition[1], self.shotPosition[0])

            mutex.acquire()
            flag = False
            mutex.release()
            time.sleep(0.02)

    def shot_movement(self, x_position, y_position):
        global flag
        self.shotPosition[1] = x_position
        self.shotPosition[0] = y_position
        win.addch(self.shotPosition[0], self.shotPosition[1], ".")
        while self.shot and self.shotPosition[0] > 4:

            if flag:
                win.addch(self.shotPosition[0], self.shotPosition[1], " ")
                self.shotPosition[0] = self.shotPosition[0] - 1
                win.addch(self.shotPosition[0], self.shotPosition[1], ".")

                mutex.acquire()
                flag = False
                mutex.release()

            if self.shotPosition[0] == 4:
                self.shot = False
                win.addch(self.shotPosition[0], self.shotPosition[1], " ")


class Enemy(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.enemy_position = [4, 28]  # posição do inimigo
        self.enemy_shot_position = [0, 0]  # inicialização da posição do tiro
        self.operator = 1  # aumenta ou diminui se indo para esquerda ou direita
        self.direction = 'right'
        self.numOfShots = 0
        self.stopped = event
        self.shot = False

    def run(self):
        self.enemy_movement()

    def enemy_movement(self):
        global event
        global flag_enemy
        global reset
        global exited
        global endGameTime

        if flag_enemy:
            if reset:
                for n in range(WINDOW_WIDTH - 5):
                    self.enemy_position[1] = n + 1
                    # apaga caracteres na linha onde reset foi acionado
                    win.addch(
                        self.enemy_position[0], self.enemy_position[1], ' ')

                self.enemy_position = [4, 28]
                self.enemy_shot_position = [0, 0]
                self.shot = False
                self.operator = 1
                self.direction = 'right'
                self.numOfShots = 0
                self.stopped = event
                reset = False

            for x in range(4):
                if self.direction == 'right':
                    # apaga o 5 elemento da direita para esquerda
                    erase = self.enemy_position[1] - 5
                else:
                    # apaga o 5 elemento da esquerda para direita
                    erase = self.enemy_position[1] + 5

                # setando largura máxima
                if self.enemy_position[1] == WINDOW_WIDTH - 6:
                    self.operator = -1
                    self.direction = 'left'

                    for n in range(6):
                        delete = WINDOW_WIDTH - 6 - n
                        win.addch(self.enemy_position[0], delete, ' ')

                    self.enemy_position[0] = self.enemy_position[0] + 1

                if self.enemy_position[1] == 6:  # setando largura minima
                    self.operator = 1
                    self.direction = 'right'

                    for n in range(6):
                        delete = 6 + n
                        win.addch(self.enemy_position[0], delete, ' ')

                    self.enemy_position[0] = self.enemy_position[0] + 1

                if self.enemy_position[0] == 18:
                    mutex.acquire()
                    endGameTime = dt.now()
                    exited = True
                    event = ESC
                    mutex.release()

                # aumenta ou diminui variavel de acordo com o operador
                self.enemy_position[1] = self.enemy_position[1] + self.operator
                # printa o inimigo
                win.addch(self.enemy_position[0],
                          self.enemy_position[1], 'o')
                # apaga conforme se movimenta
                win.addch(self.enemy_position[0], erase, ' ')
                shot_in_the_middle = self.enemy_position[1] - 2

                mutex.acquire()
                flag_enemy = False
                mutex.release()

            # if(self.numOfShots < 5):
            #     pass
            #     self.shotMovement(shot_in_the_middle)

            # if (self.numOfShots == 5):
            #     self.numOfShots -= 1
        time.sleep(0.02)

    def shot_movement(self, shot_in_the_middle):
        while self.enemy_shot_position[0] < 18:
            self.numOfShots += 1
            self.enemy_shot_position[0] += 1
            win.addch(self.enemy_shot_position[0], shot_in_the_middle, '|')
            win.addch(self.enemy_position[0], shot_in_the_middle, ' ')

        if self.enemy_shot_position[0] == 18:
            self.numOfShots -= 1


def update_screen():
    global flag
    global flag_enemy
    global paused
    win.timeout(150)

    while event != ESC:
        if not paused:  # se não está pausado então habilita movimentos
            mutex.acquire()
            flag = True  # flag que sinaliza que o player pode se mover
            flag_enemy = True  # flag que sinaliza que o enemie pode se mover
            mutex.release()
        time.sleep(0.1)


def interface_thread():
    global event
    global flag
    global flag_enemy
    global paused
    global score
    global exited

    while True:
        if event == PAUSE and not paused:
            mutex.acquire()
            flag = False  # flag que sinaliza que o player pode se mover
            flag_enemy = False  # flag que sinaliza que o enemie pode se mover
            paused = True
            event = 97  # usando apenas para mudar event e poder retomar o jogo
            mutex.release()

        if event == PAUSE and paused:
            mutex.acquire()
            flag = True  # flag que sinaliza que o player pode se mover
            flag_enemy = True  # flag que sinaliza que o enemie pode se mover
            paused = False
            event = 97  # usando apenas para mudar event e poder pausar o jogo
            mutex.release()

        if event == RESET:
            global reset
            global score
            mutex.acquire()
            score = 0
            reset = True
            event = 97  # usando apenas para mudar event e poder retomar o jogo
            mutex.release()

        if event == EXIT:
            mutex.acquire()
            curses.endwin()
            exited = True
            mutex.acquire()


def logger_thread():
    global t1
    global exited

    async def run():
        t2 = time.time()
        tempo_de_execucao = t2 - t1
        await asyncio.sleep(10)
        with open('log.txt', 'w') as writer:
            writer.writelines(
                f"Score = {score} | Tempo de execucao = {round(tempo_de_execucao, 2)}")

    while not exited:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        task = [loop.create_task(run())]
        wait_task = asyncio.wait(task)
        loop.run_until_complete(wait_task)
        loop.close()


def generate_log():
    host = "localhost"
    port = 8080
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((host, port))

    while True:
        data, endereco = server.recvfrom(2048)
        data_loaded = data.decode()

        with open('logUDP.txt', 'w') as writer:
            writer.writelines(data_loaded)
        time.sleep(5)


def main():
    global init
    global score
    global vidas
    global event
    global exited
    global deadTime
    global endGameTime

    host = "localhost"
    port = 8080
    server = (host, port)
    connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    enemy = Enemy()
    player = Player()
    thread3 = threading.Thread(target=update_screen)
    thread4 = threading.Thread(target=interface_thread)
    thread5 = threading.Thread(target=logger_thread)
    cloud_process = multiprocessing.Process(target=generate_log)

    win.addch(18, 30, 'x')  # inicializando posição do jogador

    player.start()
    enemy.start()
    thread3.start()
    thread4.start()
    thread5.start()
    cloud_process.start()

    def send_data():
        global init
        global score
        global vidas
        global event
        global exited
        global deadTime
        global endGameTime

        hour_minute_second_init = init.strftime("%H:%M:%S")

        if endGameTime != 'Game in progress':
            mutex.acquire()
            endGameTime = endGameTime.strftime("%H:%M:%S")
            mutex.release()

        data = {
            "Initial game time": hour_minute_second_init,
            "Score": score,
            "Credits": vidas,
            "time of player destruction": deadTime,
            "End game time": endGameTime
        }
        data = str.encode(json.dumps(data))
        connection.sendto(data, server)
  

    while event != ESC and not exited:  # enquanto evento não for esc continua rodando o programa
        event = win.getch()
        win.addstr(2, 2, 'Score ' + str(score) + ' ')
        player.run()
        enemy.run()
        send_data()

    if exited:
        send_data()
        thread4.join()
        thread3.join()
        enemy.join()
        player.join()
        thread5.join()
        cloud_process.join()
        curses.endwin()
        print(f"Final score = {score}")


if __name__ == '__main__' and event != ESC:
    main()
