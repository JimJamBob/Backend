from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session

from ... import oauth2
from ... import database, schemas, models, utils
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(
    tags = ["Authenication"]
)


# 'user_credentials' is an instance of OAuth2PasswordRequestForm,
# which reads the username and password from the form data of the request.
# We use Depends() because OAuth2PasswordRequestForm is a dependency that FastAPI
# automatically resolves and injects into the route.
# 'db' is a database session dependency, also injected using Depends().
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

    
