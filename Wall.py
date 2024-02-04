from tkinter import *
from tkinter.ttk import *
import random

class Wall:
    """
    Class for walls in game.
    """
    def __init__(self, canvas: Canvas, isHost: bool = True):
        """
        Constructor.
        Randomly generate walls in gameboard.
        canvas: tkinter.Canvas - A tkinter canvas where player will be drawn.
        isHost: bool - Determine if it is called by a host or a guest.
        """
        self.canvas = canvas
        self.wallRects = [None] * 80

        #random wall generation
        if isHost:
            for i in range(10):
                for j in range(8):
                    if not (i == 0 and j == 0) and not (i == 9 and j == 7) \
                       and random.randrange(1, 6) == 5:
                        left = i * 100
                        top = j * 100

                        self.wallRects[i * 8 + j] = self.canvas.create_polygon(
                                                        left, top, \
                                                        left + 100, top, \
                                                        left + 100, top + 100, \
                                                        left, top + 100)
