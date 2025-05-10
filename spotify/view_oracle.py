import oracledb
from .credentials import DB_USER, DB_PASSWORD, DB_DSN

def view_data():
    print("Connecting to Oracle...")
    conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM top_charts")
    print("Total rows:", cursor.fetchone())

    cursor.execute("""
        SELECT country_code, rank, song_name, artist_name, track_id, retrieved_at
        FROM top_charts
        WHERE country_code = 'KR'
        ORDER BY retrieved_at DESC, rank ASC
    """)
    for row in cursor.fetchall():
        print(row)

    cursor.close()
    conn.close()
