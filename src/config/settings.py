import os


# Database 
PG_HOST     = os.getenv("PG_HOST",     "localhost")
PG_PORT     = os.getenv("PG_PORT",     "5432")
PG_DATABASE = os.getenv("PG_DATABASE", "pay_core")
PG_USER     = os.getenv("PG_USER",     "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "")
PG_SSLMODE  = os.getenv("PG_SSLMODE",  "disable")


# JWT 
# Two separate secrets: one for short-lived access tokens,
# one for long-lived refresh tokens (rotation strategy)
JWT_SECRET_KEY          = os.getenv("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY  = os.getenv("JWT_REFRESH_SECRET_KEY")
JWT_ALGORITHM           = os.getenv("JWT_ALGORITHM",           "HS256")
JWT_EXPIRE_MINUTES      = int(os.getenv("JWT_EXPIRE_MINUTES",  "30"))
JWT_REFRESH_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))


# App 
# COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", "localhost")

# Default currency for new wallets.
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "PKR")
