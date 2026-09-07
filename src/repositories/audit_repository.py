from src.database.connection import conn



def log(
    user_id:     int | None,
    action:      str,
    resource:    str | None = None,
    resource_id: str | None = None,
    ip_address:  str | None = None,
    metadata:    str | None = None,
) -> None:
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO audit_logs
                (user_id, action, resource, resource_id, ip_address, metadata)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (user_id, action, resource, resource_id, ip_address, metadata)
        )
        conn.commit()
        cursor.close()
    except Exception as e:
        # Never let an audit failure crash the main operation so we didnt add raise here 
        print(f" Audit log failed: {e}")
