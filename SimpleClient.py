
import socket               # Import socket module

s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 12345                # Reserve a port for your service.

s.connect((host, port))


while True:
    msg = s.recv(2048)
    print(msg.decode())

count = 0
while s.recv(2048):
    count += 1

print(count)
s.close()                     # Close the socket when done