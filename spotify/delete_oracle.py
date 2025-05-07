import oracledb
from .credentials import DB_USER, DB_PASSWORD, DB_DSN

def delete_data():
    print("Connecting to Oracle...")
    conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
    cursor = conn.cursor()

    print("Deleting all data from top_charts...")
    cursor.execute("DELETE FROM top_charts")
    conn.commit()
    print("✅ All rows deleted.")

    cursor.close()
    conn.close()
