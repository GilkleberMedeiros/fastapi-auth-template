from fastapi import APIRouter, HTTPException, Request, Response, Depends
from sqlmodel import select, Session
from datetime import datetime, timezone, timedelta

from app.models.user import User, UserCreate, get_user
from app.db import get_session
from app.utils.pwd_crypt import get_pwd_context
from app.utils.jwt import create_tokens, validate_refresh_token, JWTError


pwd_context = get_pwd_context()

router = APIRouter(
    prefix="/users/auth", 
    tags=["auth"]
)

@router.post("/login")
def login(body: UserCreate, req: Request, res: Response, session: Session = Depends(get_session)):
    try: 
        statement = select(User).where(User.username == body.username)
        results = session.exec(statement)
        user = results.first()
    except Exception as e:
        res.status_code = 500
        return {"detail": "Database Error!", "success": False}
    
    if not user:
        res.status_code = 404
        return {"detail": f"Couldn't found User with Username {body.username}!", "success": False}

    equal_pwd = pwd_context.verify(body.password, user.hashed_password)
    if not equal_pwd:
        res.status_code = 400
        return {"detail": f"Wrong Password for User {body.username}!", "success": False}
    
    # Generate JWT Tokens
    try: 
        token_data = {"id": user.id}
        tokens = create_tokens(token_data)
    except JWTError as _:
        res.status_code = 400
        return {"detail": f"Got JWTError when creating tokens for User {body.username}!", "success": False}
    except:
        res.status_code = 500
        return {"detail": f"Got Error while creating JWT tokens for User {body.username}!", "success": False}
    
    res.set_cookie(
        "refresh_token", 
        tokens["refresh_token"], 
        expires=tokens["refresh_expires_at"], 
        httponly=True, 
    )
    del tokens["refresh_token"]
    del tokens["refresh_expires_at"]

    return tokens

@router.post("/join")
def join(
    body: UserCreate, 
    req: Request, 
    res: Response, 
    session: Session = Depends(get_session)
): 
    statement = select(User).where(User.username == body.username)
    results = session.exec(statement)
    
    if results.first():
        res.status_code = 400
        return {"detail": f"There's already an User with username {body.username}!", "success": False}
    
    try: 
        body.save()
    except: 
        res.status_code = 500 
        return {"detail": f"Got unknow database error while creating User {body.username}!", "success": False}
    
    res.status_code = 201
    return {"detail": f"User {body.username} created Successfully!", "success": True}

@router.get("/refresh")
def refresh(req: Request, res: Response):
    payload = validate_refresh_token(req, res)
    user_id = payload.get("id")

    if not user_id:
        raise HTTPException(400, "Request doesn't contain an User id!")
    
    try:
        user = get_user(user_id)
    except: 
        raise HTTPException(400, "Error while validanting the User. Given user credentials are invalid!")


    try: 
        token_data = {"id": user.id}
        tokens = create_tokens(token_data)
    except JWTError as _:
        res.status_code = 400
        return {"detail": f"Got JWTError when creating tokens for User {user.username}!", "success": False}
    except:
        res.status_code = 500
        return {"detail": f"Got Error while creating JWT tokens for User {user.username}!", "success": False}
    
    del tokens["refresh_token"]
    del tokens["refresh_expires_at"] 

    return tokens

@router.get("/logout")
def logout(req: Request, res: Response):
    hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)

    res.set_cookie(
        "refresh_token", 
        "logout", 
        expires=hour_ago, 
        httponly=True,  
    )

    return {"detail": "Logout Successfully!", "success": True}