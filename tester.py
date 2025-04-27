import psycopg2

DB_CONNECTION = "postgresql://neondb_owner:npg_l38UOSViAEwZ@ep-small-surf-a59ig0mj-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"

def fetch():
    conn = psycopg2.connect(DB_CONNECTION)
    cur = conn.cursor()
    
    # Query your DATABASE_virtual table
    cur.execute(f'SELECT * FROM "DATABASE_virtual";')
    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return rows

if __name__ == "__main__":
    data = fetch()
    for row in data:
        print(f"id: {row[0]}, cmd: {row[1]}, retain: {row[2]}, qos: {row[3]}, dup: {row[4]}")
