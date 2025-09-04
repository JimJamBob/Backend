from typing import List
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session

from app.database import get_db

from ... import oauth2
from ... import database, schemas, models, utils
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from livekit import api
import os
from livekit.api import CreateRoomRequest
from ...livekit_client import get_livekit_client
from livekit.api import LiveKitAPI


router = APIRouter(
    tags = ["Device Authenication"],
    prefix  = "/gettoken"
    )


#The following endpoint takes the backend jwt and provides the livekit jwt 
@router.post('/', response_model= schemas.Token)
async def build_room_get_token(device_id: schemas.DeviceID,
                            db: Session = Depends(get_db), 
                                current_user: int = Depends(oauth2.get_current_user),
                                    lkapi: LiveKitAPI = Depends(get_livekit_client)):
    print("Hello")
    
    # Check if the user has the device and if its not flagged
    device = db.query(models.Device).filter(
        models.Device.user_id == current_user.id,
        models.Device.device_id == device_id
    ).first()

    if device is None or device.marked_active == False:
        return None  # or raise an exception
    
    #CHecked that the device isn't flagged lost, and the user exists and it logged in. Now create room
    #Use the device name as the room is better, as it requires less db queries.
    room = await lkapi.room.create_room(CreateRoomRequest(
        name=f"{device_id}",
        empty_timeout=10 * 60,
        max_participants=2,
        ))
    
    #With name room, is where the device can only join the room above.
    livekit_token = get_livekit_token(device_id)

    
    return {"access_token": livekit_token, "token_type": "Bearer"}
