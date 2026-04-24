import sqlite3

def login(username, password):
    # Authenticate user against database
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Build query directly from user input
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor.execute(query)
    result = cursor.fetchone()

    if result:
        return {"status": "success", "user": result}
    return {"status": "failed"}

def reset_password(email):
    # Send reset link — no rate limiting
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(f"UPDATE users SET reset_token='abc123' WHERE email='{email}'")
    conn.commit()
    send_email(email, "Your reset link: http://app.com/reset?token=abc123")
