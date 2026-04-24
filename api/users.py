import hashlib
import secrets
from datetime import datetime

def get_user(user_id: int, db) -> dict:
    """Fetch user by ID using parameterised query."""
    result = db.execute(
        "SELECT id, name, email FROM users WHERE id = ?",
        (user_id,)
    )
    return result.fetchone()

def create_user(name: str, email: str, password: str, db) -> dict:
    """Create a new user with hashed password."""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    
    db.execute(
        "INSERT INTO users (name, email, password_hash, salt, created_at) VALUES (?, ?, ?, ?, ?)",
        (name, email, hashed, salt, datetime.utcnow())
    )
    db.commit()
    return {"status": "created", "email": email}

def update_email(user_id: int, new_email: str, db) -> dict:
    """Update user email with validation."""
    if "@" not in new_email or "." not in new_email:
        raise ValueError("Invalid email format")
    
    db.execute(
        "UPDATE users SET email = ? WHERE id = ?",
        (new_email, user_id)
    )
    db.commit()
    return {"status": "updated"}
