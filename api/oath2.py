from jose import JWTError, jwt
from datetime import datetime, timedelta
from bson import ObjectId
from dotenv import load_dotenv
import os
from .schemas import TokenData, db, UserInDB
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict, expires_delta: int = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        id: str = payload.get("id")
        
        if id is None:
            raise credentials_exception
        
        token_data = TokenData(id=id)
        return token_data
    except JWTError:
        raise credentials_exception

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token is invalid or expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    result = verify_access_token(token, credentials_exception)
    if result is None:
        raise credentials_exception
    current_user_id = result.id
    current_user = await db["users"].find_one({"_id": ObjectId(current_user_id)})
    if current_user is None:
        raise credentials_exception
    return UserInDB(**current_user)