from tkinter import *
from tkinter.ttk import *

class Player:
    """
    Class for a player.
    """

    def __init__(self, canvas: Canvas, num: int):
        """
        Constructor.

        canvas: tkinter.Canvas - A tkinter canvas where player will be drawn.\n
        num: int - Only 1 or 2 is valid value.
        Determine if the object is about the host or the guest.
        """
        self.canvas = canvas
        self.num = num
        self.health = 5

        if self.num == 1:
            self.x = 20
            self.y = 20
            self.playerCircle = self.canvas.create_oval( \
                self.x - 20, self.y - 20, self.x + 20, self.y + 20, fill="blue") #player circle

        elif self.num == 2:
            self.x = 979
            self.y = 779
            self.playerCircle = self.canvas.create_oval( \
                self.x - 20, self.y - 20, self.x + 20, self.y + 20, fill="red") #player circle

        self.speed = 7

    def move(self, direction: str):
        """
        Move player.
        direction: str - Either 'w', 'a', 's', 'd'. Determine direction of moving.
        """
        if direction == 'w':
            self.y -= self.speed
            self.canvas.move(self.playerCircle, 0, -self.speed)

        elif direction == 'a':
            self.x -= self.speed
            self.canvas.move(self.playerCircle, -self.speed, 0)

        elif direction == 's':
            self.y += self.speed
            self.canvas.move(self.playerCircle, 0, self.speed)

        elif direction == 'd':
            self.x += self.speed
            self.canvas.move(self.playerCircle, self.speed, 0)

    def moveToCoord(self, x: int, y: int):
        """
        Move to exact coordinate.
        x: int
        y: int
        """
        self.canvas.move(self.playerCircle, x - self.x, y - self.y)
        self.x = x
        self.y = y

    def hurt(self):
        self.health -= 1
        if self.health == 0:
            if self.num == 1:
                self.moveToCoord(20, 20)
                self.health = 5

            elif self.num == 2:
                self.moveToCoord(979, 779)
                self.health = 5
