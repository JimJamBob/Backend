from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session

from .. import oauth2
from ... import database, schemas, models, utils
from ...livekit_client import lkapi
from fastapi.security.oauth2 import OAuth2PasswordRequestForm


from fastapi import HTTPException, status

from livekit.api import DeleteRoomRequest


router = APIRouter(
    prefix  = "/deactivate",
    tags = ["deactivate"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model= schemas.Post)
async def deactivate_device(device_id: schemas.deviceID, db: Session = Depends(get_db), current_user_id: int = 
                Depends(oauth2.get_current_user)):

    # Fetch the device by ID
    device = db.query(models.Device).filter(models.Device.device_id == device_id).first()


    if device:
        device.marked_active = False  # Update column value
        db.commit()                   # Save changes to DB
        db.refresh(device)            # Refresh object with updated values
        
        #delete the room
        await lkapi.room.delete_room(DeleteRoomRequest(
            room="myroom",
        ))
        
        return device
    else:
        raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Device not found"
    )
