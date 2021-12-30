import time
import threading
import curses

mutex = threading.Lock()

key = curses.KEY_DOWN
score = 0

WINDOW_WIDTH = 60  # number of columns of window box
WINDOW_HEIGHT = 20  # number of rows of window box
ESC = 27


class Player (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.key = curses.KEY_DOWN
        self.right = curses.KEY_RIGHT
        self.left = curses.KEY_LEFT
        self.shot = curses.KEY_UP
        self.event = win.getch()
        self.position = [18, 30]
        self.shotPosition = [0, 0]

    def begin(self):
        win.addch(self.position[0], self.position[1],
                  'x')  # Colocar no init do Player

    def _controlMovements(self, event):
        if event == self.right:
            mutex.acquire()
            coordinates = [self.position[0], self.position[1] + 1]

            if coordinates[1] != WINDOW_WIDTH-1:
                # apaga posicao atual
                win.addch(self.position[0], self.position[1], ' ')
                self.position[1] = coordinates[1]
                self.position[0] = coordinates[0]
                win.addch(coordinates[0], coordinates[1], "x")

            mutex.release()

        if self.position == WINDOW_WIDTH - 1:
            pass

        if event == self.left:
            mutex.acquire()  
            # move jogador para esquerda
            coordinates = [self.position[0], self.position[1] - 1]
            if coordinates[1] !=1:
                win.addch(self.position[0], self.position[1], ' ') # apaga posicao atual
                self.position[1] = coordinates[1]
                self.position[0] = coordinates[0]
                win.addch(coordinates[0], coordinates[1], "x")
            mutex.release()

        if event == self.shot:
            mutex.acquire()
            self.shotPosition[0] = self.position[0] + 1
            self.shotPosition[1] = self.position[1]
            win.addch(self.shotPosition[0], self.shotPosition[1], ".")
            mutex.release()

            mutex.acquire()
            for x in range(WINDOW_HEIGHT-4):
                win.addch(self.shotPosition[0], self.shotPosition[1], ".")
                old_position = self.shotPosition[0]
                self.shotPosition[0] = self.shotPosition[0] - 1
                win.addch(old_position, self.shotPosition[1], " ")
            mutex.release()
        time.sleep(0.02)

    def controlMovements(self, event):
        threading.Thread(target=self._controlMovements, args=(event,)).start()
class Enemie (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.position = [4, 28]
        self.shotPosition = [0, 0]
        win.addch(self.position[0], self.position[1], 'o')

    def _enemie_movement(self):
        win.addch(self.position[0], self.position[1], ' ')
        for x in range(WINDOW_WIDTH/2):
            mutex.acquire()
            self.position = self.position+1
            win.addch(self.position[0], self.position[1], 'x')
            mutex.release()
        time.sleep(0.02)

    def enemie_movement(self):
        threading.Thread(target=self._enemie_movement, args=(event,)).start()


def updateScreen():
    mutex.acquire()
    win.timeout(150)
    mutex.release()
    time.sleep(0.01)


curses.initscr()
win = curses.newwin(WINDOW_HEIGHT, WINDOW_WIDTH, 0, 0)
win.keypad(1)
curses.noecho()
curses.curs_set(0)
win.border(0)
win.nodelay(1)

player = Player()
player.begin()
enemie = Enemie()

while key != ESC:
    event = win.getch()
    if event != -1:
        key = event
    thread1 = player.controlMovements(event)
    thread3 = threading.Thread(target=updateScreen).start()
    thread2 = enemie.enemie_movement()

thread3.join()
thread1.join()
thread2.join()


curses.endwin()
print(f"Final score = {score}")
