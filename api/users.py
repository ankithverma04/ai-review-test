import bcrypt
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def get_user(user_id: int, db) -> dict:
    """Fetch user by ID using parameterised query."""
    try:
        result = db.execute(
            "SELECT id, name, email, created_at FROM users WHERE id = ?",
            (user_id,)
        )
        user = result.fetchone()
        if not user:
            raise ValueError(f"User {user_id} not found")
        return dict(user)
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}")
        raise

def email_exists(email: str, db) -> bool:
    """Check if an email is already registered."""
    result = db.execute(
        "SELECT 1 FROM users WHERE email = ?", (email,)
    )
    return result.fetchone() is not None

def validate_email(email: str) -> None:
    """Validate email format."""
    if not EMAIL_REGEX.match(email):
        raise ValueError(f"Invalid email format: {email}")

def create_user(name: str, email: str, password: str, db) -> dict:
    """Create a new user with securely hashed password."""
    validate_email(email)

    if email_exists(email, db):
        raise ValueError(f"Email already in use: {email}")

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=12)
    ).decode("utf-8")

    try:
        db.execute(
            "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (name, email, password_hash, datetime.utcnow())
        )
        db.commit()
        logger.info(f"User created: {email}")
        return {"status": "created", "name": name, "email": email}
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user {email}: {e}")
        raise

def update_email(user_id: int, new_email: str, db) -> dict:
    """Update user email with validation and duplicate check."""
    validate_email(new_email)

    if email_exists(new_email, db):
        raise ValueError(f"Email already in use: {new_email}")

    try:
        get_user(user_id, db)  # raises if user not found
        db.execute(
            "UPDATE users SET email = ? WHERE id = ?",
            (new_email, user_id)
        )
        db.commit()
        logger.info(f"Email updated for user {user_id}")
        return {"status": "updated", "user_id": user_id, "email": new_email}
    except ValueError:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating email for user {user_id}: {e}")
        raise
