from dotenv import load_dotenv
from os import environ

load_dotenv()

DEBUG = bool(environ.get("DEBUG", False))
PORT = int(environ.get("PORT", 8000))

DB_HOST = environ.get("DB_HOST", default="sqlite:///db.sqlite3")

PASSWD_HASH_ALGO = environ.get("PASSWD_HASH_ALGO", "bcrypt")

JWT_PUB_KEY_PATH = environ.get("JWT_PUB_KEY_PATH", "JWT_EC_PUBKEY.pem")
JWT_PRIV_KEY_PATH = environ.get("JWT_PRIV_KEY_PATH", "JWT_EC_PRIVKEY.pem")
JWT_ACCESS_EXPIRES_MINUTES = int(environ.get("JWT_ACCESS_EXPIRES_MINUTES", 15))
JWT_REFRESH_EXPIRES_MINUTES = int(environ.get("JWT_REFRESH_EXPIRES_MINUTES", 2880)) 
JWT_ALGO = environ.get("JWT_ALGO", "ES256")


