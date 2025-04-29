import socket
import psycopg2
from psycopg2 import sql

#Database Connection Parameters:
DBhost = "ep-bitter-block-a4kk37qe-pooler.us-east-1.aws.neon.tech"
DBname = "neondb"
DBuser = "neondb_owner"
DBpassword = "npg_M2GWUidmJNO6"
DBport = "5432"

#Device IDs
SmartFridgeID = "vbi-831-t1i-28g"
SmartFridge2ID = "fc10411b-0f0f-481f-84f2-671e859981c0"
SmartWasherID = "68n-b24-76c-hmr"

#Sensors
#Fridge 1
Fridge1_Moisture = "Moisture Meter - SmartFridge"
Fridge1_Ammeter = "Ammeter - SmartFridge"

#Fridge 2
Fridge2_Moisture = "Moisture Meter - SmartFridge2"
Fridge2_Ammeter = "Ammeter - SmartFridge2"

#Dishwasher
Washer_Water = "Water Consumption Sensor - SmartWasher"
Washer_Ammeter = "Ammeter - SmartWasher"

#Mapping Device names to ID
DeviceNames = {SmartFridgeID: "SmartFridge1", SmartFridge2ID: "SmartFridge2", SmartWasherID: "SmartWasher"}

#Connect to PostgreSQL Database
try:
    db_conn = psycopg2.connect(dbname = DBname, user = DBuser, password = DBpassword, host = DBhost, port = DBport, sslmode = "require")
    db_conn.autocommit = True
    cursor = db_conn.cursor()

    #Clear table
    cursor.execute("TRUNCATE assignment_data RESTART IDENTITY;")

    #Automated Update: Transfer data from assignment_data_virtual to assignment_data
    cursor.execute("""
        INSERT INTO assignment_data (device_id, sensor_type, value, timestamp)
        SELECT
            payload->>'asset_uid' AS device_id,
            key AS sensor_type,
            (value)::NUMERIC AS value,
            to_timestamp((payload->>'timestamp')::BIGINT) AT TIME ZONE 'UTC'
        FROM assignment_data_virtual
        CROSS JOIN LATERAL jsonb_each_text(payload::jsonb)
        WHERE key NOT IN ('timestamp', 'topic', 'parent_asset_uid', 'asset_uid', 'board_name')
          AND cmd = 'publish';
    """)
    print("assignment_data table updated successfully from virtual table.")

except Exception as e:
    print(f"Failed to connect to database or updata data: {e}")
    exit(1)

#Setting up TCP server
serverIP = input("Enter Server IP: ")
serverPort = int(input("Enter Server Port (e.g., 5000): "))

myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
elif message == "Q3":
    try:
        cursor.execute("""
            SELECT device_id, SUM(value)
            FROM assignment_data
            WHERE sensor_type IN (%s, %s, %s)
            GROUP BY device_id;
        """, (Fridge1_Ammeter, Fridge2_Ammeter, Washer_Ammeter))

        results = cursor.fetchall()
        device_kwh = {}

        for device_id, total_current in results:
            if device_id in (SmartFridgeID, SmartFridge2ID):
                # Fridge = 1-minute interval → multiply by 0.002
                kwh = float(total_current) * 0.002
            else:
                # Dishwasher = 1-hour interval → multiply by 0.12
                kwh = float(total_current) * 0.12
            device_kwh[device_id] = kwh

        if device_kwh:
            highest_device = max(device_kwh, key=device_kwh.get)
            highest_kwh = device_kwh[highest_device]
            device_name = DeviceNames.get(highest_device, highest_device)
            response = f"Device with Highest Electricity Usage: {device_name} ({highest_kwh:.2f} kWh)"
        else:
            response = "No electricity usage data available."

    except Exception as e:
        response = f"Error querying electricity usage: {e}"
myTCPSocket.bind((serverIP, serverPort))
myTCPSocket.listen(5)

print(f"Server listening on {serverIP}:{serverPort}...")

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

        #Processing Queries
        if message == "Q1":
            try:
                #Average for SmartFridge1
                cursor.execute("""
                    SELECT AVG(value)
                    FROM assignment_data
                    WHERE device_id = %s
                      AND sensor_type = %s
                      AND (timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'America/Los_Angeles') >
                          (NOW() AT TIME ZONE 'UTC' AT TIME ZONE 'America/Los_Angeles') - INTERVAL '3 HOURS';
                """, (SmartFridgeID, Fridge1_Moisture))
                avg_moisture_fridge1 = cursor.fetchone()[0]

                #Average for SmartFridge2
                cursor.execute("""
                    SELECT AVG(value)
                    FROM assignment_data
                    WHERE device_id = %s
                      AND sensor_type = %s
                      AND (timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'America/Los_Angeles') >
                          (NOW() AT TIME ZONE 'UTC' AT TIME ZONE 'America/Los_Angeles') - INTERVAL '3 HOURS';
                """, (SmartFridge2ID, Fridge2_Moisture))
                avg_moisture_fridge2 = cursor.fetchone()[0]

                if avg_moisture_fridge1 is not None and avg_moisture_fridge2 is not None:
                    response = (
                            f"Average Moisture (Last 3 Hours, PST):\n"
                            f"Smart Fridge 1: {avg_moisture_fridge1:.2f}%RH\n"
                            f"Smart Fridge 2: {avg_moisture_fridge2:.2f}%RH"
                    )
                else:
                    response = "No moisture data available for one or both refrigerators."

            except Exception as e:
                response = f"Error querying moisture: {e}"

        elif message == "Q2":
            try:
                cursor.execute("""
                    SELECT AVG(value)
                    FROM assignment_data
                    WHERE device_id = %s
                        AND sensor_type = %s;
                """, (SmartWasherID, Washer_Water))
                avg_water = cursor.fetchone()[0]
                response = f"Average Dishwasher Water Usage: {avg_water:.2f} gallons" if avg_water else "No water consumption data available."
            except Exception as e:
                response = f"Error querying water consumption: {e}"

        elif message == "Q3":
            try:
                cursor.execute("""
                    SELECT device_id, SUM(value)
                    FROM assignment_data
                    WHERE sensor_type IN (%s, %s, %s)
                    GROUP BY device_id;
                """, (Fridge1_Ammeter, Fridge2_Ammeter, Washer_Ammeter))

                results = cursor.fetchall()
                device_kwh = {}

                for device_id, total_current in results:
                    if device_id in (SmartFridgeID, SmartFridge2ID):
                        # Fridge = 1-minute interval → multiply by 0.002
                        kwh = float(total_current) * 0.002
                    else:
                        # Dishwasher = 1-hour interval → multiply by 0.12
                        kwh = float(total_current) * 0.12

                device_kwh[device_id] = kwh

                if device_kwh:
                    highest_device = max(device_kwh, key=device_kwh.get)
                    highest_kwh = device_kwh[highest_device]
                    device_name = DeviceNames.get(highest_device, highest_device)
                    response = f"Device with Highest Electricity Usage: {device_name} ({highest_kwh:.2f} kWh)"
                else:
                    response = "No electricity usage data available."

            except Exception as e:
                response = f"Error querying electricity usage: {e}"

                
        else:
            response = "Invalid Query. Send Q1/Q2/Q3/quit."

        incomingSocket.send(response.encode('utf-8'))

    print(f"Closing connection with {incomingAddress}")
    incomingSocket.close()

    if message.lower() == 'quit':
        print("Shutting down server...")
        break

myTCPSocket.close()
cursor.close()
db_conn.close()

    


