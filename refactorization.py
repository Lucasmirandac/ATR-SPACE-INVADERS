import threading
import curses

key = curses.KEY_DOWN
right = curses.KEY_RIGHT
left = curses.KEY_LEFT
shot = curses.KEY_UP
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
        self.event = event
        self.position = [18, 30]
        self.shotPosition [0,0]
        win.addch(self.position[0], self.position[1], 'x')

    def _controlMovements(self, event):
        if event == self.right:
            win.addch(self.postion[0], self.position[1], ' ')  # apaga posicao atual
            coordinates = [self.postion[0], self.position[1] + 1]
            self.position[1] = coordinates[1]
            win.addch(coordinates[0], coordinates[1], "x")

        if event == self.left:
            win.addch(self.postion[0], self.position[1], ' ')  # apaga posicao atual
            coordinates = [self.postion[0], self.position[1] - 1]
            self.position[1] = coordinates[1]
            win.addch(coordinates[0], coordinates[1], "x")

        if event == self.shot:
            self.shotPosition[0] = self.postion[0] + 1
            self.shotPosition[1] = self.position[1]
            win.addch(self.shotPosition[0], self.shotPosition[1], ".")
            while self.shotPosition[0] < WINDOW_HEIGHT:
                win.addch(self.shotPosition[0], self.shotPosition[1], ".")
                old_position = self.shotPosition[0]
                self.shotPosition[0] = self.shotPosition[0] - 1
                win.addch(old_position, self.shotPosition[1], " ")
        
        win.addch(coordinates[0], coordinates[1], 'x')
    
    def controlMovements(self, event):
        threading.Thread(target=self._controlMovements, args=(event,)).start()

class Enemie (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.direction = event
        self.position = [18, 30]
        self.shotPosition [0,0]
        win.addch(self.position[0], self.position[1], 'ooooo')

    def movement(self, event):
        self.direction = curses.KEY_RIGHT

def updateScreen():
    win.timeout(150)

curses.initscr()
win = curses.newwin(WINDOW_HEIGHT, WINDOW_WIDTH, 0, 0)
win.keypad(1)
curses.noecho()
curses.curs_set(0)
win.border(0)
win.nodelay(1)

while key != ESC:
    win.timeout(150)
    event = win.getch()
    player = Player()
    enemie = Enemie()
    thread1 = player.controlMovements(event)
    thread3 = threading.Thread(target = updateScreen).start()
    thread2 = enemie.movements()


thread1.join()
thread3.join()
curses.endwin()
print(f"Final score = {score}")