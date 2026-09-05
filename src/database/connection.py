import psycopg2
from src.config import settings


# A single connection is shared across the application (simple connection pool)

conn = None

try:
    conn = psycopg2.connect(
        host     = settings.PG_HOST,
        port     = settings.PG_PORT,
        dbname   = settings.PG_DATABASE,
        user     = settings.PG_USER,
        password = settings.PG_PASSWORD,
        sslmode  = settings.PG_SSLMODE,
    )
    print("Database connected successfully.")

except Exception as e:
    print(f"Database connection failed: {e}")
    raise RuntimeError(f"Could not connect to PostgreSQL: {e}")
