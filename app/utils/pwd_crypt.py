"""
Password cryptography.
"""
from passlib.context import CryptContext

from app.env import PASSWD_HASH_ALGO


def get_pwd_context(hash_algo: str = PASSWD_HASH_ALGO):
    return CryptContext([hash_algo], deprecated="auto")



