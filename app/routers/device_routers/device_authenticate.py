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
from ...livekit_client import get_livekit_client, get_livekit_token
from livekit.api import LiveKitAPI


router = APIRouter(
    tags = ["Device Authenication"],
    prefix  = "/gettoken"
    )


#The following endpoint takes the backend jwt and provides the livekit jwt 
@router.post('/')
async def build_room_get_token(db: Session = Depends(get_db), 
                                token_data: schemas.DeviceTokenData = Depends(oauth2.get_current_device_user),
                                    lkapi: LiveKitAPI = Depends(get_livekit_client)):
    
    user_id = token_data.user_id
    device_id = token_data.device_id

    # Check if the user has the device and if it's not flagged
    device = db.query(models.Device).filter(
        models.Device.user_id == user_id,
        models.Device.device_id == device_id
    ).first()

    if device is None or device.marked_active == False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found or inactive"
        )
    
    #CHecked that the device isn't flagged lost, and the user exists and it logged in. Now create room
    #Use the device name as the room is better, as it requires less db queries.
    room = await lkapi.room.create_room(CreateRoomRequest(
        name=f"{device.device_id}",
        empty_timeout=10 * 60,
        max_participants=2,
        ))
    

    #With name room, is where the device can only join the room above.
    livekit_token = await get_livekit_token(device.device_id)

    
    return livekit_token
