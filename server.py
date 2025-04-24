import socket


serverIP = "0.0.0.0"
serverPort = int(input("Enter Server Port: ")) # Example: 5000
myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
myTCPSocket.bind((serverIP, serverPort))
myTCPSocket.listen(5)

print(f"Server listening on port {serverPort}...")

while True:
    incomingSocket, incomingAddress = myTCPSocket.accept()
    print(f"Connected to {incomingAddress}")
   
    while True:
        
        message = incomingSocket.recv(1024).decode('utf-8')
        if not message:
            break
        
        print(f"Received Message: {message}")

        if message.lower() == 'quit':
            response = "Server Terminating"
            incomingSocket.send(response.encode('utf-8'))
            break
        
        incomingSocket.send(message.upper().encode('utf-8'))

    print(f"Closing connection with {incomingAddress}")
    incomingSocket.close()

    if message.lower() == 'quit':
        print("Shutting down server...")
        break
myTCPSocket.close()