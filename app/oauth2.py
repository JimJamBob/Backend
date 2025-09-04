from jose import JWTError, jwt
from datetime import datetime, timedelta
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
DEVICE_ACCESS_TOKEN_EXPIRE_MINUTES = settings.device_access_token_expire_minutes
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_user_access_token(data: dict): 
    to_encode = data.copy()
    to_encode.update({"token_type": "user"})  # Add user token type
    
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_device_access_token(data: dict): 
    to_encode = data.copy()
    to_encode.update({"token_type": "device"})  # Add device token type
    
    expire = datetime.utcnow() + timedelta(minutes= DEVICE_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_user_access_token(token: str, credentials_exception): 
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if this is a user token
        token_type = payload.get("token_type")
        if token_type != "user":
            raise credentials_exception
        
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
            
        token_data = schemas.UserTokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    return token_data


def verify_device_access_token(token: str, credentials_exception): 
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if this is a device token
        token_type = payload.get("token_type")
        if token_type != "device":
            raise credentials_exception
        
        user_id = payload.get("user_id")
        device_id = payload.get("device_id")
        
        if user_id is None or device_id is None:
            raise credentials_exception
            
        token_data = schemas.DeviceTokenData(user_id=user_id, device_id=device_id)
    except JWTError:
        raise credentials_exception
    return token_data


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Invalid user token", 
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    token = verify_user_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.user_id).first()
    return user.id


def get_current_device_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Invalid device token", 
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    token = verify_device_access_token(token, credentials_exception)
    return schemas.DeviceTokenData(user_id=token.user_id, device_id=token.device_id)