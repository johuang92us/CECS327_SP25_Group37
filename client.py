import os
import socket

maxByteToReceive = 1024
flag = True

destination = input("Destination IP: ")
port = int(input("Port Number: "))

myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
myTCPSocket.connect((destination, port))

while flag:
    
    message = input("Message: ")
    myTCPSocket.sendall(message.encode('utf-8'))
    serverReponse = myTCPSocket.recv(1024)

    print(f"Server Response: {serverReponse.decode()}")
    flag = input("Continue or Quit: ").lower()

    if flag == "quit":
        flag = False
        message = 'quit'
        myTCPSocket.sendall(message.encode('utf-8'))
        serverReponse = myTCPSocket.recv(1024)
        print(f"{serverReponse.decode()}")

myTCPSocket.close()