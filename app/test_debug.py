from inference import tier1_predict, tier2_predict

code_get_user = 'def get_user(user_id):\n    conn = sqlite3.connect("db.sqlite")\n    cursor = conn.cursor()\n    query = "SELECT * FROM users WHERE id = " + user_id\n    cursor.execute(query)\n    return cursor.fetchone()'

print("Bandit:", tier1_predict(code_get_user))
print("CodeBERT:", tier2_predict(code_get_user))