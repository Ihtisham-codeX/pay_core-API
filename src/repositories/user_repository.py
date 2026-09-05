from src.database.connection import conn

#_________________________________________________________________________________________

def find_by_email(email: str):
#_________________________________________________________________________________________

    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, email, username, password_hash, first_name, last_name, phone, role, status, created_at, updated_at "
        "FROM users WHERE email = %s",
        (email,)
    )
    row = cursor.fetchone()
    cursor.close()
    return row

#_________________________________________________________________________________________

def find_by_username(username: str):
#_________________________________________________________________________________________

    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, email, username, password_hash, first_name, last_name, phone, role, status, created_at, updated_at "
        "FROM users WHERE username = %s",
        (username,)
    )
    row = cursor.fetchone()
    cursor.close()
    return row

#_________________________________________________________________________________________

def find_by_id(user_id: int):
#_________________________________________________________________________________________

    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, email, username, password_hash, first_name, last_name, phone, role, status, created_at, updated_at "
        "FROM users WHERE id = %s",
        (user_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    return row

#_________________________________________________________________________________________

def create_user(email: str, username: str, password_hash: str,
                first_name: str, last_name: str, phone: str | None, role: str):
#_________________________________________________________________________________________
    
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (email, username, password_hash, first_name, last_name, phone, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id, email, username, password_hash, first_name, last_name, phone, role, status, created_at, updated_at
        """,
        (email, username, password_hash, first_name, last_name, phone, role)
    )
    row = cursor.fetchone()
    conn.commit()
    cursor.close()
    return row

#_________________________________________________________________________________________

def update_profile(user_id: int, first_name: str | None, last_name: str | None, phone: str | None):
#_________________________________________________________________________________________

    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE users SET
            first_name = COALESCE(%s, first_name),
            last_name  = COALESCE(%s, last_name),
            phone      = COALESCE(%s, phone)
        WHERE id = %s
        RETURNING id, email, username, password_hash, first_name, last_name, phone, role, status, created_at, updated_at
        """,
        (first_name, last_name, phone, user_id)
    )
    row = cursor.fetchone()
    conn.commit()
    cursor.close()
    return row
