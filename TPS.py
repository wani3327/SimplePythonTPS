from tkinter import *
from tkinter.ttk import *
import threading
import math
import socket
from time import sleep

from Player import Player
from Wall import Wall
from Bullets import Bullets


def leftClick(guest: socket.socket, player: Player, bullets: Bullets, mouseX: int, mouseY: int):
    """
    Called when left mouse button is clicked. Summon a bullet and send it to the guest.

    guest: socket.socket - Socket connected with guest.\n
    player: Player - A Player object that has done left clicking.\n
    bullets: Bullets - A Bullets object matching with player parameter.\n
    mouseX: int - X coordinate of mouse when clicked.\n
    mouseY: int - Y coordinate of mouse when clicked.
    """
    shooting(player, bullets, mouseX, mouseY)
    hostSendBullet(guest, player.num, mouseX, mouseY)

def shooting(player: Player, bullets: Bullets, mouseX, mouseY):
    angle = math.atan((mouseY - player.y) / (mouseX - player.x))
    if mouseX - player.x < 0:
        angle += math.pi

    bullets.addBullet(player.x, player.y, angle)

def keyDown(guest: socket.socket, player: Player, wall: Wall, keyInput: str):
    movePlayer(player, wall, keyInput)
    hostSendPlayer(guest, player)

def movePlayer(player: Player, wall: Wall, keyInput: str):
    if keyInput == 'w':
        if player.y <= 20:
            return

        chunkX1 = (player.x - 20) // 100
        chunkX2 = (player.x + 20) // 100
        chunkY = (player.y - 20 - player.speed) // 100

        if not (wall.wallRects[chunkX1 * 8 + chunkY] or wall.wallRects[chunkX2 * 8 + chunkY]):
            player.move(keyInput)

    elif keyInput == 'a':
        if player.x <= 20:
            return

        chunkX = (player.x - 20 - player.speed) // 100
        chunkY1 = (player.y - 20) // 100
        chunkY2 = (player.y + 20) // 100

        if not (wall.wallRects[chunkX * 8 + chunkY1] or wall.wallRects[chunkX * 8 + chunkY2]):
            player.move(keyInput)

    elif keyInput == 's':
        if player.y >= 780:
            return

        chunkX1 = (player.x - 20) // 100
        chunkX2 = (player.x + 20) // 100
        chunkY = (player.y + 20 + player.speed) // 100

        if not (wall.wallRects[chunkX1 * 8 + chunkY] or wall.wallRects[chunkX2 * 8 + chunkY]):
            player.move(keyInput)

    elif keyInput == 'd':
        if player.x >= 980:
            return

        chunkX = (player.x + 20 + player.speed) // 100
        chunkY1 = (player.y - 20) // 100
        chunkY2 = (player.y + 20) // 100

        if not (wall.wallRects[chunkX * 8 + chunkY1] or wall.wallRects[chunkX * 8 + chunkY2]):
            player.move(keyInput)

def moveBullet(bullets: Bullets, player: Player, wall: Wall):
    """
    Moving Bullet. Runs every 0.1 second.
    """
    BULLETSPEED = 20

    bulletList = list(range(len(bullets.bullets)))

    for i in bulletList:
        bullet = bullets.bullets[i]

        x = int(bullet[0])
        y = int(bullet[1])
        chunkX = int((x + BULLETSPEED * math.cos(bullet[2])) // 100)
        chunkY = int((y + BULLETSPEED * math.sin(bullet[2])) // 100)

        # When hit walls or hit the game border
        if chunkX * chunkY < 0 or chunkX >= 10 or chunkY >= 8 \
           or wall.wallRects[chunkX * 8 + chunkY]:
            bullets.delete(i)
            bulletList.pop(len(bulletList) - 1) # Removing last element

        # When hit player
        elif distanceBetween2Points(player.x, player.y, x, y) < 20:
            player.hurt()
            bullets.delete(i)
            bulletList.pop(len(bulletList) - 1) # Removing last element

        else:
            bullets.move(i, BULLETSPEED)

    threading.Timer(0.02, lambda : moveBullet(bullets, player, wall)).start()

def send(s: socket.socket, msg: bytes):
    try:
        s.send(msg)
    except OSError: # When disconnected by chance
        pass

def hostSendPlayer(guest: socket.socket, player: Player):
    msg = b'P '

    # Player Information
    msg += str(player.num).encode() + b' '
    msg += str(player.x).encode() + b' '
    msg += str(player.y).encode() + b'\0'

    print(msg)
    guest.send(msg)

    return

def hostSendWall(guest: socket.socket, wall: Wall):
    isWall = []

    for i in wall.wallRects:
        isWall.append(True if i else False)

    guest.send(b'W ' + bytes(isWall) + b'\0')

    return

def hostSendBullet(guest: socket.socket, owner: int, mouseX: int, mouseY: int):
    msg = b'B '
    msg += str(owner).encode() + b' '
    msg += str(mouseX).encode() + b' '
    msg += str(mouseY).encode() + b'\0'

    print(msg)
    guest.send(msg)

def hostRecieve(guest: socket.socket, player: Player, wall: Wall, bullets: Bullets):
    try:
        msgs = guest.recv(2048)

    except BlockingIOError:
        msgs = b''

    msgs = msgs.decode().split('\x00')

    for msg in msgs:
        if not msg:
            break

        print(msg)
        msg = msg.split()

        if msg[0] == 'p':   # Enemy Moves.
            keyDown(guest, player, wall, msg[1])

        elif msg[0] == 'b': # Enemy shoots.
            leftClick(guest, player, bullets, int(msg[1]), int(msg[2]))

    threading.Timer(0.001, lambda : hostRecieve(guest, player, wall, bullets)).start()
    return

def guestSendPlayer(guest: socket.socket, keyInput: str):
    if keyInput:
        msg = b'p ' + keyInput.encode() + b'\0'
        print(msg)
        guest.send(msg)
    return

def guestSendBullet(guest: socket.socket, mouseX: int, mouseY: int):
    msg = b'b ' + str(mouseX).encode() + b' ' + str(mouseY).encode() + b'\0'
    print(msg)
    guest.send(msg)
    return

def guestRecieve(host: socket.socket, player1: Player, player2: Player, bullets1: Bullets, bullets2: Bullets):
    try:
        msgs = host.recv(2048)

    except BlockingIOError:
        msgs = b''

    msgs = msgs.decode().split('\x00')

    for msg in msgs:
        if not msg:
            break

        print(msg)
        msg = msg.split()

        if msg[0] == 'P':
            if msg[1] == '1':
                player1.moveToCoord(int(msg[2]), int(msg[3]))
            elif msg[1] == '2':
                player2.moveToCoord(int(msg[2]), int(msg[3]))

        elif msg[0] == 'B':
            if msg[1] == '1':
                shooting(player1, bullets1, int(msg[2]), int(msg[3]))
            elif msg[1] == '2':
                shooting(player2, bullets2, int(msg[2]), int(msg[3]))

    threading.Timer \
        (0.001, lambda : guestRecieve(host, player1, player2, bullets1, bullets2)).start()
    return

def guestRecieveWall(host: socket.socket, wall: Wall):
    while True:
        msg = host.recv(2048)

        if msg[0] == ord('W'):
            wall.wallRects = list(msg[2:])

            for i in range(10):
                for j in range(8):
                    if wall.wallRects[i * 8 + j]:
                        left = i * 100
                        top = j * 100

                        wall.wallRects[i * 8 + j] = gameCanvas.create_polygon( \
                                                        left, top, \
                                                        left + 100, top, \
                                                        left + 100, top + 100, \
                                                        left, top + 100)
            break

def distanceBetween2Points(x1: int, y1: int, x2: int, y2: int):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


window = Tk()
window.title('The Game')
window.geometry('1000x800+100+100')
window.resizable(False, False)

gameCanvas = Canvas(window, relief = 'solid', bd = 1)
gameCanvas.focus_set()

player1 = Player(gameCanvas, 1)
player2 = Player(gameCanvas, 2)
bullets1 = Bullets(gameCanvas)
bullets2 = Bullets(gameCanvas)


print('Are you a host or a guest?')
print('1: Host')
print('2: Guest')
print('Any other key will close the program')

inp = input()

if inp == '1':
    s = socket.socket()  # Create a socket object
    port = 12345         # Reserve a port for your service.
    s.bind(('', port))   # Bind to the port
    s.listen(5)          # Now wait for client connection.

    print('Now waiting...')

    c, addr = s.accept() # Establish connection with client.
    c.setblocking(False)
    c.send(b'HANSUNG KIM KYEONG-WAN')

    print('Got connection from', addr, '.')
    print('Starting a game in a second...')

    sleep(1)


    wall = Wall(gameCanvas)
    hostSendWall(c, wall)

    gameCanvas.bind('<Button-1>', lambda event: leftClick(c, player1, bullets1, event.x, event.y))
    gameCanvas.bind('<Key>', lambda event: keyDown(c, player1, wall, event.char))

    hostRecieve(c, player2, wall, bullets2)

    moveBullet(bullets1, player2, wall)
    moveBullet(bullets2, player1, wall)

    gameCanvas.pack(expand = True, fill = "both")

    window.mainloop()

    c.close() # Close the connection


elif inp == '2':
    s = socket.socket() # Create a socket object

    print('Please input the IP address of a host. Inputting nothing will connect you to localhost.')
    hostIp = input()    # Get local machine name
    port = 12345        # Reserve a port for your service.
    if not hostIp:
        hostIp = socket.gethostname()


    s.connect((hostIp, port))

    wall = Wall(gameCanvas, False)
    guestRecieveWall(s, wall) # Getting wall information from host

    s.setblocking(False)

    gameCanvas.bind('<Button-1>', lambda event: guestSendBullet(s, event.x, event.y))
    gameCanvas.bind('<Key>', lambda event: guestSendPlayer(s, event.char))

    guestRecieve(s, player1, player2, bullets1, bullets2)

    moveBullet(bullets1, player2, wall)
    moveBullet(bullets2, player1, wall)

    gameCanvas.pack(expand = True, fill = "both")

    window.mainloop()

    s.close()                 # Close the socket when done
