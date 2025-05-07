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

#Mapping Tables
DeviceTables = {SmartFridgeID: "smartfridge1_data", SmartFridge2ID: "smartfridge2_data", SmartWasherID: "smartwasher_data"}

#Mapping Device names to ID
DeviceNames = {SmartFridgeID: "SmartFridge1", SmartFridge2ID: "SmartFridge2", SmartWasherID: "SmartWasher"}


#Build tables
def build_tables():
    for device_id, table in DeviceTables.items():
        cursor.execute(f"""
            SELECT
                payload->>'asset_uid' AS device_id,
                key AS sensor_type,
                (value)::NUMERIC AS value,
                to_timestamp((payload->>'timestamp')::BIGINT) AS ts
            FROM assignment_data_virtual
            CROSS JOIN LATERAL jsonb_each_text(payload::jsonb)
            WHERE key NOT IN ('timestamp', 'topic', 'parent_asset_uid', 'asset_uid', 'board_name')
              AND cmd = 'publish'
              AND payload->>'asset_uid' = %s;
        """, (device_id,))
        rows = cursor.fetchall()

        for device_id, sensor_type, value, ts in rows:
            cursor.execute(sql.SQL("""
                INSERT INTO {} (device_id, sensor_type, value, timestamp)
                VALUES(%s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """).format(sql.Identifier(table)), row)

#Update each device table from virtual
def update_tables():
    for device_id, table in DeviceTables.items():
        cursor.execute(sql.SQL("SELECT MAX(timestamp) FROM {}").format(sql.Identifier(table)))
        max_ts = cursor.fetchone()[0]

        if max_ts is None:
            time_filter = ""
        else:
            time_filter = f"AND to_timestamp((payload->>'timestamp')::BIGINT) > '{max_ts}'"

        query = f"""
            SELECT
                payload->>'asset_uid' AS device_id,
                key AS sensor_type,
                (value)::NUMERIC AS value,
                to_timestamp((payload->>'timestamp')::BIGINT) AS ts
            FROM assignment_data_virtual
            CROSS JOIN LATERAL jsonb_each_text(payload::jsonb)
            WHERE key NOT IN ('timestamp', 'topic', 'parent_asset_uid', 'asset_uid', 'board_name')
            AND cmd = 'publish'
            AND payload ->>'asset_uid' = '{device_id}'
            {time_filter};
            
        """

        cursor.execute(query)
        rows = cursor.fetchall()


        for device_id, sensor_type, value, ts in rows:
            cursor.execute(sql.SQL("""
                INSERT INTO {} (device_id, sensor_type, value, timestamp)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """).format(sql.Identifier(table)), (device_id, sensor_type,value, ts))

#Connect to PostgreSQL Database
try:
    db_conn = psycopg2.connect(dbname = DBname, user = DBuser, password = DBpassword, host = DBhost, port = DBport, sslmode = "require")
    db_conn.autocommit = True
    cursor = db_conn.cursor()

    table_queries = {
        "smartfridge1_data": """
            CREATE TABLE IF NOT EXISTS smartfridge1_data (
                id SERIAL PRIMARY KEY,
                device_id TEXT NOT NULL,
                sensor_type TEXT NOT NULL,
                value NUMERIC NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                UNIQUE (device_id, sensor_type, timestamp)
            );
        """,
        "smartfridge2_data": """
            CREATE TABLE IF NOT EXISTS smartfridge2_data (
                id SERIAL PRIMARY KEY,
                device_id TEXT NOT NULL,
                sensor_type TEXT NOT NULL,
                value NUMERIC NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                UNIQUE (device_id, sensor_type, timestamp)
            );
        """,
        "smartwasher_data": """
            CREATE TABLE IF NOT EXISTS smartwasher_data (
                id SERIAL PRIMARY KEY,
                device_id TEXT NOT NULL,
                sensor_type TEXT NOT NULL,
                value NUMERIC NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                UNIQUE (device_id, sensor_type, timestamp)
            );
        """
    }

    tables_made = False
    
    for table_name, create_sql in table_queries.items():
        cursor.execute("""
            SELECT EXISTS(
                SELECT FROM information_schema.tables
                WHERE table_name = %s
            );
        """, (table_name,))
        exists = cursor.fetchone()[0]

        if not exists:
            tables_made = True

        cursor.execute(create_sql)

    if tables_made:
        build_tables()

except Exception as e:
    print(f"Failed to connect to database or updata data: {e}")
    exit(1)

#Setting up TCP server
serverIP = input("Enter Server IP: ")
serverPort = int(input("Enter Server Port: "))
myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
myTCPSocket.bind((serverIP, serverPort))
myTCPSocket.listen(5)

print(f"Server listening on {serverIP}:{serverPort}...")

while True:
    incomingSocket, incomingAddress = myTCPSocket.accept()
    print(f"Connected to {incomingAddress}")
    while True:
        message = incomingSocket.recv(1024).decode('utf-8').strip()
        if not message:
            break
        print(f"Received Message: {message}")

        if message.lower() == 'quit':
            response = "Server Terminating"
            incomingSocket.send(response.encode('utf-8'))
            break

        try:
            update_tables()
        except Exception as e:
            print(f"Warning Failed to update tables before query: {e}")

        #Processing Queries
        if message == "1":
            try:
                cursor.execute("""
                    SELECT AVG(value)
                    FROM smartfridge1_data
                    WHERE sensor_type = %s
                      AND (timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'America/Los_Angeles') >
                          (NOW() AT TIME ZONE 'UTC' AT TIME ZONE 'America/Los_Angeles') - INTERVAL '3 HOURS';
                """, (Fridge1_Moisture,))
                fridge1_avg = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT AVG(value)
                    FROM smartfridge2_data
                    WHERE sensor_type = %s
                      AND (timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'America/Los_Angeles') >
                          (NOW() AT TIME ZONE 'UTC' AT TIME ZONE 'America/Los_Angeles') - INTERVAL '3 HOURS';
                """, (Fridge2_Moisture,))
                fridge2_avg = cursor.fetchone()[0]

                if fridge1_avg is not None and fridge2_avg is not None:
                    response = (
                        f"Average Moisture (Last 3 Hours, PST):\n"
                        f"Smart Fridge 1: {fridge1_avg:.2f}%RH\n"
                        f"Smart Fridge 2: {fridge2_avg:.2f}%RH"
                    )
                else:
                    response = "No moisture data available for one or both refrigerators."
            
            except Exception as e:
                response = f"Error querying moisture: {e}"

        elif message == "2":
            try:
                cursor.execute("""
                    SELECT AVG(value)
                    FROM smartwasher_data
                    WHERE sensor_type = %s;
                """, (Washer_Water,))
                water_avg= cursor.fetchone()[0]
                if  water_avg is not None:
                    response = f"Average Dishwasher Water Usage: {water_avg:.2f} gallons"
                else:
                    response = "No water consumption data available for Dishwasher."

            except Exception as e:
                response = f"Error querying water consumption: {e}"

        elif message == "3":
            try:
                device_kwh = {}
                    
                cursor.execute("""
                    SELECT SUM(value)
                    FROM smartfridge1_data
                    WHERE sensor_type = %s
                """, (Fridge1_Ammeter,))
                result = cursor.fetchone()[0]
                if result is not None:
                    device_kwh[SmartFridgeID] = float(result) * 0.006

                cursor.execute("""
                    SELECT SUM(value)
                    FROM smartfridge2_data
                    WHERE sensor_type = %s
                """, (Fridge2_Ammeter,))
                result = cursor.fetchone()[0]
                if result is not None:
                    device_kwh[SmartFridge2ID] = float(result) * 0.006

                cursor.execute("""
                    SELECT SUM(value)
                    FROM smartwasher_data
                    WHERE sensor_type = %s
                """, (Washer_Ammeter,))
                result = cursor.fetchone()[0]
                if result is not None:
                    device_kwh[SmartWasherID] = float(result) * 0.36

                if device_kwh:
                    highest_use = max(device_kwh, key = device_kwh.get)
                    response = f"Device with Highest Electricity Usage: {DeviceNames[highest_use]} ({device_kwh[highest_use]:.2f} kWh)"
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

    


