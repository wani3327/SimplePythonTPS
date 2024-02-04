from tkinter import *
from tkinter.ttk import *
import math

class Bullets:
    def __init__(self, canvas):
        self.canvas = canvas
        self.bullets = []
        self.bulletCircles = []

    def addBullet(self, x, y, angle):
        self.bullets.append([x, y, angle])
        self.bulletCircles.append(self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3))

    def move(self, i, speed):
        self.bullets[i][0] = self.bullets[i][0] + speed * math.cos(self.bullets[i][2])
        self.bullets[i][1] = self.bullets[i][1] + speed * math.sin(self.bullets[i][2])

        self.canvas.move( \
            self.bulletCircles[i], \
            speed * math.cos(self.bullets[i][2]), \
            speed * math.sin(self.bullets[i][2]))

    def delete(self, i = -1):
        if i == -1:
            self.bullets = []
            for j in self.bulletCircles:
                self.canvas.delete(j)
            self.bulletCircles = []
        else:
            self.bullets.pop(i)
            self.canvas.delete(self.bulletCircles[i])
            self.bulletCircles.pop(i)
