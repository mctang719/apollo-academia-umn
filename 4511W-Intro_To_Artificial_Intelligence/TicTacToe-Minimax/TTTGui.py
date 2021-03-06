#!/usr/bin/python3

from tkinter import Frame, Canvas, Label, Button, LEFT,RIGHT, ALL, Tk
from tkinter.font import Font

class TTTGui:
    def __init__(self, controller, dimension):
        self.controller = controller

        self.root = Tk()  # put this here removes Tkinter dep in the Controller
        self.root.title('TicTacToe Minimax')
        self.root.resizable(width=False, height=False)

        self.font = Font(family="Helvetica", size=128)
        self.buttons = {}

        self.dimension = dimension
        self.draw_grids()
        self.load_restart_button()

    def draw_grids(self):
        for x in range (0, self.dimension):
            for y in range(0, self.dimension):
                handler = lambda x=x,y=y: self.playerMoved(x, y)
                button = Button(self.root, command=handler, font=self.font, width=2, height=1)
                button.grid(row=x, column=y)
                self.buttons[x,y] = button

    def load_restart_button(self):
        button = Button(self.root, text='Restart',font=Font(family="Helvetica", size=32), command=lambda: self.controller.restart(self.reloadUI))
        button.grid(row=self.dimension + 1, column=0, columnspan=self.dimension, sticky="WE")
        self.root.update()

    def updateUI(self, board_state, winCoordinates=None):
        # winCoordinates is a list of the winning coordinates
        for x in range(len(board_state)):
            for y in range(len(board_state[0])):
                if board_state[x][y] != 0:
                    self.buttons[x, y]['disabledforeground'] = 'black'
                    self.buttons[x, y]['state'] = 'disabled'
                    self.buttons[x, y]['relief'] = 'sunken'

                if board_state[x][y] == 'x':
                    self.buttons[x, y]['text'] = 'x'

                if board_state[x][y] == 'o':
                    self.buttons[x, y]['text'] = 'o'

        if winCoordinates is not None:
            for x, y in winCoordinates:
                self.buttons[x, y]['disabledforeground'] = 'red'
            for x in range(len(board_state)):
                for y in range(len(board_state[0])):
                    self.buttons[x, y]['relief'] = 'sunken'
                    self.buttons[x, y]['state'] = 'disabled'

    def reloadUI(self, board_state):
        print("Restarting Game.")
        for x in range(len(board_state)):
            for y in range(len(board_state[0])):
                self.buttons[x, y]['relief'] = 'raised'
                self.buttons[x, y]['state'] = 'normal'
                self.buttons[x, y]['text'] = ""
        self.updateUI(board_state)

    def playerMoved(self, x, y):
        print('Played Moved: ', x,y)
        self.controller.updateModel(x, y, self.updateUI)

    def start(self, state):
        self.updateUI(state)
        self.root.mainloop()
