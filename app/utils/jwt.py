from fastapi import Request, Response, HTTPException
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from typing import TypedDict

from app.env import (
    JWT_PUB_KEY_PATH, 
    JWT_PRIV_KEY_PATH, 
    JWT_ACCESS_EXPIRES_MINUTES, 
    JWT_REFRESH_EXPIRES_MINUTES, 
    JWT_ALGO, 
)

class TokenData(TypedDict):
    token: str
    type: str 
    expires_at: datetime

def create_token(
    data: dict, 
    expires_minutes: int, 
    token_type: str, 
    priv_key_path: str = JWT_PRIV_KEY_PATH, 
    algorithm: str = JWT_ALGO, 
) -> TokenData: 
    with open(priv_key_path, "r") as key_file:
        private_key = key_file.read()

    to_encode = data.copy()
    expires = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expires})

    token = jwt.encode(to_encode, private_key, algorithm)

    return {
        "token": token, 
        "type": token_type, 
        "expires_at": expires,
    }

class TokensData(TypedDict):
    access_token: str
    refresh_token: str 
    token_type: str 
    access_expires_at: datetime
    refresh_expires_at: datetime

def create_tokens(
    data: dict, 
    priv_key_path: str = JWT_PRIV_KEY_PATH, 
    access_expires_minutes: int = JWT_ACCESS_EXPIRES_MINUTES, 
    refresh_expires_minutes: int = JWT_REFRESH_EXPIRES_MINUTES,
    algorithm: str = JWT_ALGO, 
) -> TokensData:
    
    access_token = create_token(
        data, 
        access_expires_minutes, 
        "access", 
        priv_key_path, 
        algorithm
    )

    refresh_token = create_token(
        data, 
        refresh_expires_minutes, 
        "refresh", 
        priv_key_path, 
        algorithm
    )

    return {
        "access_token": access_token["token"], 
        "refresh_token": refresh_token["token"], 
        "token_type": "bearer", 
        "access_expires_at": access_token["expires_at"], 
        "refresh_expires_at": refresh_token["expires_at"],  
    }


def validate_token(
    token: str, 
    pub_key_path: str = JWT_PUB_KEY_PATH, 
    algorithm: str = JWT_ALGO
) -> dict:
    """Validate and get JWT data."""
    with open(pub_key_path) as f:
        public_key = f.read()

    payload = jwt.decode(token, public_key, algorithms=[algorithm])
    return payload

def validate_refresh_token(
    req: Request, 
    _: Response, 
    cookie_name: str = "refresh_token", 
    pub_key_path: str  = JWT_PUB_KEY_PATH, 
    algorithm: str = JWT_ALGO, 
) -> dict:
    """
    Validate refresh token got from Request object cookies and return its payload. 
    Raise HTTPException if token is not valid!
    """

    token = req.cookies.get(cookie_name)
    if not token:
        raise HTTPException(400, "Couldn't find refresh token in request cookies!")
    
    try: 
        payload = validate_token(token, pub_key_path, algorithm)
    except JWTError as _:
        raise HTTPException(400, "Got JWTError while validating token! Maybe refresh expired or is invalid.")
    except: 
        raise HTTPException(500, "Got unexpected error while validating refresh token!")
    
    return payload