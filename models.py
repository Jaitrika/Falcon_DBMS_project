import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="falcon"
    )

def get_all_flights():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Flights")
    return cursor.fetchall()
