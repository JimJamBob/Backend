from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session

from ..oauth2 import oauth2
from .. import database, schemas, models, utils
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(
    tags = ["Authenication"]
)

@router.post('/login', response_model= schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        #Dont tell them whether the email or the password were incorrect
        print("Email Wrong")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    
    if not utils.verify(user_credentials.password, user.password):
        print("Password Wrong")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")
    
    #Create token
    #Return Token

    access_token = oauth2.create_access_token(data = {"user_id": user.id})
    return {"access_token": access_token, "token_type": "Bearer"}
#    return {"token": access_token, "token type": "Bearer"}

    
