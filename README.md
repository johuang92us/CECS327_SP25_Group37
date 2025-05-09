CECS 327 Assignemtn 8: End-to-End IoT System

This assignment demonstrates an end-to-end IoT system with realtime querying of sensor data using a TCP client-server model. Data from smart devices are processed with sensor data stored in a PostgreSQL database (NeonDB) with device behavior simulated by Dataniz.

GitHub Repository: [https://github.com/johuang92us/CECS327_SP25_Group37](https://github.com/johuang92us/CECS327_SP25_Group37)

Project Files:
- ‘server.py’ - TCP server that connects to database, processes queries, and returns results
- ‘client.py’ - TCP client that user interacts with to send queries and receive responded
- ‘README.md’ - Instructions for setup and usage

Before proceeding, ensure you have the following:
- Two Google Cloud Windows VMs (one for Server, one for Client)
- Python 3.8 or later installed on both VMs
- NeonDB PostgreSQL account with access credentials
- Active devices streaming data from Dataniz (must be connected to NeonDB database)
- NeonDB ‘assignment_data_virtual’ table populated with IoT data

-----

Step 1: Setup
Start both VMs. In each one:

Install Python and Git using:
sudo apt update
sudo apt install python3 python3-pip git -y

Clone this repository using:
git clone https://github.com/johuang92us/CECS327_SP25_Group37.git
cd CECS327_SP25_Group37

Install required Python packages using:
pip3 install psycopg2-binary

-----

Step 2: Configure Database Access
In Server VM:

Edit the top section of server.py with NeonDB credentials:
DBhost = "<your_host_url>"
DBname = "<your_database_name>"
DBuser = "<your_user>"
DBpassword = "<your_password>"
DBport = "5432"
sslmode = "require"

If you don’t know your credentials, you can go to NeonDB Dashboard > Connect > Connection String. It should be structured like so:

postgresql://<username>:<password>@<host>/<database_name>?sslmode=require

Insert your credentials as instructed.

-----

Step 3: Running the Server and Client
In VM 1 (Server VM):

Run the server program: python3 server.py

When prompted, enter:
Enter Server IP: <Internal IP of this VM>
Enter Server Port: e.g. 5000

*Make sure the firewall for this VM allows for TCP traffic on this port

In VM 2 (CLient VM):

Run the client program: python3 client.py

When prompted, enter:
Enter Server IP: <Internal IP of Server VM>
Enter Server Port: <Same port as server VM>

When prompted, enter your query as instructed:
1. What is the average moisture inside my kitchen fridge in the past three hours? (1)
2. What is the average water consumption per cycle in my smart dishwasher? (2)
3. Which device consumed more electricity among my three IoT devices? (3)
4. Quit (quit)
   
Any other input will result in a message listing the valid options.

-----

Troubleshooting:
- Connection failure: Ensure that server is running and port is open in the firewall
- No data returned: Ensure your Dataniz devices are on and publishing
- Database error: Verify NeonDB credentials and table names (You may need to edit table names in queries in server.py)
- *Note that early queries may take a little longer as tables have to be updated. Should be faster after this.


Other Database Notes:
- The server will automatically create the following tables if they don’t exist:
   - smartfridge1_data
   - smartfridge2_data
   - smartfridge3_data
- Tables will be populated on creation with historical data
- Tables will be updated on each query
