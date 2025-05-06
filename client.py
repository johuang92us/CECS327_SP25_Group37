import socket

#Connecting to server
serverIP = input("Enter Server IP: ")
serverPort = int(input("Enter Server Port: "))

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverIP, serverPort))

print("\nConnected to server.")
print("Select avaliable query: ")
print("1:  What is the average moisture inside my kitchen fridge in the past three hours?")
print("2: What is the average water consumption per cycle in my smart dishwasher?")
print("3: hich device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?")
print("Type 'quit' to disconnect\n")

while True:
    user_input = input("Enter query (1/2/3/quit): ")


    clientSocket.send(user_input.encode('utf-8'))
    serverResponse = clientSocket.recv(1024).decode('utf-8')
    print(f"Server Response: {serverResponse}")

    if user_input.lower() == 'quit':
        break

clientSocket.close()
print("Connection closed.")

