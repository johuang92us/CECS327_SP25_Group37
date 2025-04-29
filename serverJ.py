import socket
from flask import Flask, jsonify
import psycopg2


#credentials: postgresql://neondb_owner:npg_l38UOSViAEwZ@ep-small-surf-a59ig0mj-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require

db_credential = "postgresql://neondb_owner:npg_l38UOSViAEwZ@ep-small-surf-a59ig0mj-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"
app = Flask(__name__)
@app.route("/get_data", methods=["GET"])


def search(selection):
    avg = 0
    connect = psycopg2.connect(db_credential)
    cur = connect.cursor()
    if selection == 1:
        cur.execute("SELECT * FROM moisture_readings")
        all = cur.fetchall()
        num = len(all)
        for i in all:
            avg += i[2]
        avg = avg / num
        
        message = f"The average moisture inside my kitchen fridge is: {avg}"

        return message

    elif selection == 2:
        cur.execute("SELECT * FROM dishwasher_cycles")
        all = cur.fetchall()
        num = len(all)
        for i in all:
            avg += i[2]
        avg = avg / num

        message = f"The average water consumption per cycle in the smart dishwasher is: {avg}L"

        return message
        

    elif selection == 3:
        e = []
        base = "SELECT * FROM electricity_data"
        for i in range(3):
            tem = 0
            path = base + str(i + 1)
            cur.execute(path)
            data = cur.fetchall()
            for c in data:
                tem += c[2]
            e.append(tem) #opposite

        message = f"The device that consumed more electricity is: "

        if e.index(max(e)) == 0:
            return f"{message}: Fridge 1 ({max(e)}kWh)"
        elif e.index(max(e)) == 1:
            return f"{message}: Fridge 2 ({max(e)}kWh)"
        elif e.index(max(e)) == 2:
            return f"{message}: Dishwasher ({max(e)}kWh)"




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


        if message.lower() == 'exit':
            response = "Server Terminating"
            incomingSocket.send(response.encode('utf-8'))
            break

        else:
            result = search(int(message))
            
        
        incomingSocket.send(result.upper().encode('utf-8'))

    print(f"Closing connection with {incomingAddress}")
    incomingSocket.close()

    if message.lower() == 'exit':
        print("Shutting down server...")
        break

myTCPSocket.close()