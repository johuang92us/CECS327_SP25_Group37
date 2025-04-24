import os
import socket

maxByteToReceive = 1024
flag = True

destination = input("Destination IP: ")
port = int(input("Port Number: "))

myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
myTCPSocket.connect((destination, port))

while flag:
    smallLoop = True
    
    print(f"Please select from the following options: ")
    
    while smallLoop:
        print(f"    1. The average moisture inside the kitchen fridge in the past three hours")
        print(f"    2. The average water consumption per cycle in the smart dishwasher")
        print(f"    3. The device that consumed more electricity among the three IoT devices (two refrigerators and a dishwasher)")
        selection = input("Please enter your choice: ")
        if selection == 1:
            smallLoop = False
            pass
        elif selection == 2:
            smallLoop = False
            pass
        elif selection == 3:
            smallLoop = False
            pass

        else:
            print(f"Sorry, this query cannot be processed. Please try one of the following:")


    myTCPSocket.sendall(selection.encode('utf-8'))
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