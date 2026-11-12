def find_order(conn, order_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    return cursor.fetchall()