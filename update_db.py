from database import connect

conn = connect()
cursor = conn.cursor()

cursor.execute("ALTER TABLE items ADD COLUMN mrp REAL")

conn.commit()
conn.close()

print("MRP column added!")