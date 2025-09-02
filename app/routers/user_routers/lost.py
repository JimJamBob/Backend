from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session

from ..oauth2 import oauth2
from .. import database, schemas, models, utils
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router = APIRouter(
    prefix  = "/lost",
    tags = ["lost"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model= schemas.Post)
def mark_lost(deviceID: schemas.deviceID, db: Session = Depends(get_db), current_user_id: int = 
                Depends(oauth2.get_current_user)):
    
    return 
