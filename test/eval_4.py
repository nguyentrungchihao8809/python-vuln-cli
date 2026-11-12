import sqlite3

def find_order(conn, order_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id = %s" % order_id)
    return cursor.fetchall()