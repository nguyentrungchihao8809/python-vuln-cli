import os
import sqlite3

def run_command(cmd):
    os.system(cmd)

def get_user(user_id):
    conn = sqlite3.connect("db.sqlite")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
    return cursor.fetchone()

def add_numbers(a, b):
    return a + b